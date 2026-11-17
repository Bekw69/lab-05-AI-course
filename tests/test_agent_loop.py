"""Exercise the student's actual notebook loop without a model download."""
import ast
from pathlib import Path
import unittest

import nbformat

from lab05_core import Generation, ToolError, build_messages, parse_tool_calls

ROOT = Path(__file__).resolve().parents[1]


class ScriptedModel:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.conversations = []

    def generate(self, messages):
        self.conversations.append([dict(m) for m in messages])
        return Generation(next(self.replies), 1, 1)


class RecordingTools:
    def __init__(self, error=False):
        self.calls = []
        self.error = error

    def run(self, name, arguments):
        self.calls.append((name, arguments))
        if self.error:
            raise ToolError('Unknown region')
        return '{"value": 12}'


def load_loop(model, tools):
    notebook = nbformat.read(ROOT / 'lab05_harness.ipynb', as_version=4)
    source = next(c.source for c in notebook.cells if c.id == 'lab05-19')
    assert len(ast.parse(source).body) == 1
    namespace = dict(llm=model, toolbox=tools, build_messages=build_messages, parse_tool_calls=parse_tool_calls)
    exec(compile(source, 'notebook-agent-loop', 'exec'), namespace)
    return namespace['my_agent']


class AgentLoopTests(unittest.TestCase):
    def test_final_reply_stops_without_calling_tools(self):
        model, tools = ScriptedModel(['ANSWER: NO DATA']), RecordingTools()
        reply, messages = load_loop(model, tools)('question')
        self.assertEqual(reply, 'ANSWER: NO DATA')
        self.assertEqual(messages[-1], {'role': 'assistant', 'content': reply})
        self.assertEqual(tools.calls, [])

    def test_multiple_tools_are_returned_before_next_model_reply(self):
        calls = ('<tool_call>{"name":"first","arguments":{"x":1}}</tool_call>\n'
                 '<tool_call>{"name":"second","arguments":{"x":2}}</tool_call>')
        model, tools = ScriptedModel([calls, 'ANSWER: 12']), RecordingTools()
        reply, messages = load_loop(model, tools)('question')
        self.assertEqual(tools.calls, [('first', {'x': 1}), ('second', {'x': 2})])
        self.assertEqual([m['role'] for m in messages], ['system', 'user', 'assistant', 'tool', 'tool', 'assistant'])
        self.assertEqual([m['role'] for m in model.conversations[1]][-2:], ['tool', 'tool'])
        self.assertEqual(reply, 'ANSWER: 12')

    def test_bare_loop_propagates_tool_error(self):
        model = ScriptedModel(['<tool_call>{"name":"get_series","arguments":{}}</tool_call>'])
        with self.assertRaises(ToolError):
            load_loop(model, RecordingTools(error=True))('question')

    def test_step_budget_stops_continuing_tool_calls(self):
        model = ScriptedModel(['<tool_call>{"name":"list_regions","arguments":{}}</tool_call>'] * 2)
        tools = RecordingTools()
        reply, messages = load_loop(model, tools)('question', max_steps=2)
        self.assertEqual(reply, '')
        self.assertEqual(len(tools.calls), 2)
        self.assertEqual(messages[-1]['role'], 'tool')


if __name__ == '__main__':
    unittest.main()
