"""Check semantic comparison without consulting ground-truth answer values."""
import ast
from pathlib import Path
import re
import unittest

import nbformat
from lab05_core import numbers_in, to_float

ROOT=Path(__file__).resolve().parents[1]


class SecondOpinionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nb=nbformat.read(ROOT/'lab05_harness.ipynb',as_version=4)
        source=next(c.source for c in nb.cells if c.id=='extension-4')
        node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='answers_agree')
        scope=dict(re=re,numbers_in=numbers_in,to_float=to_float)
        exec(compile(ast.Module(body=[node],type_ignores=[]),'notebook-comparison','exec'),scope)
        cls.agree=staticmethod(scope['answers_agree'])

    def test_equivalent_numeric_format_and_catalogue_unit(self):
        self.assertTrue(self.agree('387365.00 KZT','387365.0',0.06,'KZT'))
        self.assertTrue(self.agree('3422.7 bnKZT','3422.70',0.06,'bn KZT'))

    def test_wrong_unit_is_flagged(self):
        self.assertFalse(self.agree('387365 USD','387365.0',0.06,'KZT'))

    def test_different_value_is_flagged(self):
        self.assertFalse(self.agree('3423.7 bn KZT','3422.7',0.06,'bn KZT'))

    def test_region_distinction_is_preserved(self):
        self.assertFalse(self.agree('Almaty City','Almaty Region',0.0,''))

    def test_missing_answer_is_flagged(self):
        self.assertFalse(self.agree(None,'3.5',0.06,'%'))
        self.assertFalse(self.agree('UNVERIFIED','3.5',0.06,'%'))


if __name__=='__main__':
    unittest.main()
