"""Check the submission's evidence and required answer locations; never invent outputs.

Usage: python verify_submission.py [--require-complete]
The strict mode deliberately fails until the notebook AND independent conclusion are ready.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

import nbformat

import lab05_core as core

ROOT = Path(__file__).resolve().parent
ANSWERS = {
    'lab05-10': 'PREDICTION_0', 'lab05-14': 'PREDICTION_1',
    'lab05-17': 'OBSERVATION_1', 'lab05-24': 'LOOP_NOTES',
    'lab05-28': 'PREDICTION_3', 'lab05-34': 'OBSERVATION_3',
    'lab05-36': 'NOTES', 'lab05-39': 'OBSERVATION_4',
}


def literal_assignment(source: str, name: str) -> str:
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            value = ast.literal_eval(node.value)
            assert isinstance(value, str), f'{name} must be a written string'
            return value
    raise AssertionError(f'{name} assignment missing')


def check_evidence(path: Path) -> int:
    payload = json.loads(path.read_text(encoding='utf-8'))
    env = payload['environment']
    assert env['model_id'] == core.MODEL_ID
    assert env['greedy'] is True and env['repetition_penalty'] == 1.0
    assert env['model_revision'], 'Exact model revision missing'
    data = core.load_dataset(ROOT / 'data')
    questions = {q.qid: q for q in core.build_questions(data)}
    toolbox = core.Toolbox(data)
    checked = 0
    for name, rows in payload['runs'].items():
        expected_ids = [q.qid for q in questions.values() if name != 'workflow' or q.shape == 'fixed']
        assert [r['qid'] for r in rows] == expected_ids, f'{name}: incomplete or reordered questions'
        for row in rows:
            q = questions[row['qid']]
            assert row['outcome'] == core.score_answer(q, row['answer']), f'{name}/{q.qid}: wrong score'
            assert row['model_calls'] == sum(t['kind'] == 'model' for t in row['trace'])
            assert row['prompt_tokens'] > 0 and row['new_tokens'] > 0 and row['seconds'] > 0
            for step in row['trace']:
                if step['kind'] == 'tool' and step.get('ok') and 'name' in step:
                    actual = toolbox.run(step['name'], step['arguments'])
                    assert actual == step['text'], f'{name}/{q.qid}: tool result differs from CSV'
            checked += 1
    return checked


def verify(require_complete: bool = False) -> list[str]:
    nb = nbformat.read(ROOT / 'lab05_harness.ipynb', as_version=4)
    nbformat.validate(nb)
    by_id = {c.id: c for c in nb.cells}
    toolbox_cells = [c for c in nb.cells if c.cell_type == 'code' and c.source.startswith('"""Lab 05 toolbox:')]
    assert len(toolbox_cells) == 1
    assert toolbox_cells[0].source.strip() == (ROOT / 'lab05_core.py').read_text(encoding='utf-8').strip()
    pending = []
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        ast.parse(cell.source)
        assert not any(o.output_type == 'error' for o in cell.outputs), f'Unhandled error in {cell.id}'
        if cell.execution_count is None:
            pending.append(f'unexecuted cell {cell.id}')
    for cell_id, name in ANSWERS.items():
        if not literal_assignment(by_id[cell_id].source, name).strip():
            pending.append(f'written answer {name} is empty')
    for number in range(1, 5):
        cell_id = f'extension-{number}-answer'
        source = by_id[cell_id].source
        if 'pending the actual measurements' in source or len(source.split()) < 15:
            pending.append(f'extension {number}: written interpretation missing')
    loop_tree = ast.parse(by_id['lab05-19'].source)
    assert not any(isinstance(n, ast.Name) and n.id == 'NotImplementedError' for n in ast.walk(loop_tree))
    printed = '\n'.join(o.get('text', '') for c in nb.cells if c.cell_type == 'code' for o in c.outputs)
    if 'all three match' not in printed:
        pending.append('real-model check_loop output missing')
    for name in ANSWERS.values():
        if not any(name in line and 'filled in' in line for line in printed.splitlines()):
            pending.append(f'final pencil check missing for {name}')
    evidence = ROOT / 'results' / 'runs.json'
    if evidence.exists():
        checked = check_evidence(evidence)
        print(f'Checked {checked} measured question/configuration records against the CSV and scoring.')
        payload = json.loads(evidence.read_text(encoding='utf-8'))
        for name in ('bare', 'workflow', 'layer 1', 'layer 2', 'layer 3', 'layer 3 + notes'):
            if name not in payload['runs']:
                pending.append(f'missing measured configuration {name}')
    else:
        pending.append('measured results/runs.json missing')
    conclusion = (ROOT / 'CONCLUSION.md').read_text(encoding='utf-8')
    if '(write here)' in conclusion:
        pending.append('student-written CONCLUSION.md is still the template')
    else:
        # Mechanical length check only; do not edit or suggest the student's prose.
        for number, section in enumerate(re.split(r'^## ', conclusion, flags=re.MULTILINE)[1:], 1):
            body = section.split('\n', 1)[1].split('\n---')[0]
            words = len(body.split())
            if not 80 <= words <= 200:
                pending.append(f'independent conclusion {number}: {words} words, expected about 80–200')
    assert conclusion.rstrip().endswith('I wrote this file myself, without any AI tool.')
    print('Notebook structure, Python syntax, original toolbox, and answer locations checked.')
    if pending:
        print('PENDING:\n' + '\n'.join(f'- {p}' for p in pending))
    else:
        print('Submission checks passed.')
    if require_complete and pending:
        raise SystemExit('Incomplete submission; do not call this ready to submit.')
    return pending


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    verify(parser.parse_args().require_complete)
