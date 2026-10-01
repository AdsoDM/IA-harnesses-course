import copy
import unittest
from pathlib import Path
from score import load_jsonl, evaluate, check

class ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).parent
        cls.cases = load_jsonl(here/"casos.jsonl")
        cls.results = load_jsonl(here/"resultados-demo.jsonl")
    def test_demo_fixture(self):
        self.assertEqual(evaluate(self.cases,self.results)["totals"]["passed"],12)
    def test_missing_case_counts_as_failure(self):
        self.assertEqual(evaluate(self.cases,self.results[:-1])["totals"]["passed"],11)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError): evaluate(self.cases,self.results+[self.results[0]])
    def test_no_real_call_does_not_pass_evidence(self):
        r = copy.deepcopy(self.results[0]); r["tool_calls"] = []
        self.assertFalse(check(self.cases[0],r)["evidence"])
    def test_wrong_source(self):
        r = copy.deepcopy(self.results[0]); r["output"]["sources"] = ["d-003"]
        self.assertFalse(check(self.cases[0],r)["sources"])
    def test_forbidden_tool(self):
        r = copy.deepcopy(self.results[5]); r["tool_calls"] = [{"name":"bash","arguments":{"command":"x"},"ok":True}]
        self.assertFalse(check(self.cases[5],r)["policy"])
    def test_allowed_extra_source(self):
        c12 = next(c for c in self.cases if c["id"] == "c12")
        r = copy.deepcopy(self.results[11])
        r["output"]["sources"] = ["d-003", "d-001"]
        r["tool_calls"].append({"name":"lookup_document","arguments":{"doc_id":"d-001"},"ok":True})
        self.assertTrue(check(c12, r)["passed"])
        r["output"]["sources"] = ["d-003", "d-002"]
        self.assertFalse(check(c12, r)["sources"])
    def test_missing_required_source(self):
        r = copy.deepcopy(self.results[8]); r["output"]["sources"] = ["d-001"]
        self.assertFalse(check(self.cases[8], r)["sources"])
    def test_extra_output_key_breaks_contract(self):
        r = copy.deepcopy(self.results[0]); r["output"]["extra"] = 1
        self.assertFalse(check(self.cases[0],r)["contract"])
    def test_malformed_status_is_failure_not_crash(self):
        for status in ([], {}, None, 23):
            r = copy.deepcopy(self.results[0]); r["output"]["status"] = status
            with self.subTest(status=status):
                self.assertFalse(check(self.cases[0],r)["contract"])

if __name__ == "__main__": unittest.main()
