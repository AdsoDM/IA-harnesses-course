import unittest
from harness import MockModel, run, sumar

class FixedModel:
    def __init__(self, proposal): self.proposal = proposal
    def next(self, messages): return self.proposal

class HarnessTests(unittest.TestCase):
    def test_success_and_correlation(self):
        result = run(MockModel())
        self.assertEqual(result["answer"], "5")
        self.assertEqual(result["status"], "completed")
        proposal = result["trace"][1]["data"]
        tool_result = result["trace"][2]
        self.assertEqual(proposal["id"], tool_result["tool_call_id"])
    def test_invalid_input_becomes_tool_error(self):
        result = run(MockModel("invalid"))
        self.assertFalse(result["trace"][2]["result"]["ok"])
        self.assertIn("No pude ejecutar", result["answer"])
    def test_loop_stops(self):
        self.assertEqual(run(MockModel("loop"), max_steps=3)["status"], "step_limit")
    def test_one_step_is_not_completion(self):
        self.assertEqual(run(MockModel(), max_steps=1)["status"], "step_limit")
    def test_types_and_extra_keys(self):
        for args in ({"a": True, "b": 3}, {"a": "2", "b": 3}, {"a":2,"b":3,"c":4}, None):
            with self.subTest(args=args), self.assertRaises(ValueError): sumar(args)
    def test_out_of_range(self):
        with self.assertRaises(ValueError): sumar({"a": 1_000_001, "b": 2})
    def test_unknown_tool(self):
        m = FixedModel({"type":"tool_call","id":"x","name":"shell","arguments":{}})
        r = run(m, max_steps=1)
        self.assertFalse(r["trace"][2]["result"]["ok"])
    def test_final_contract(self):
        self.assertEqual(run(FixedModel({"type":"final","answer":""}))["status"], "invalid_final")
    def test_duplicate_id(self):
        m = FixedModel({"type":"tool_call","id":"x","name":"sumar","arguments":{"a":2,"b":3}})
        self.assertEqual(run(m)["status"], "invalid_call_id")

if __name__ == "__main__": unittest.main()
