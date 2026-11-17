"""Tests for loopkit. Run: python loop/test_loopkit.py"""
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loopkit as lk  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        lk.LOOP = Path(self.tmp.name)
        (lk.LOOP / "rubrics").mkdir()
        (lk.LOOP / "variants").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return lk.main(list(args))


class Checks(Base):
    RUB = {"checks": [
        {"type": "max_words", "value": 20, "field": "body"},
        {"type": "must_include", "value": "no thanks", "label": "opt-out"},
        {"type": "must_not_include", "value": ["hope this finds you well"]},
        {"type": "not_regex", "value": r"^\S+\.(co\.uk|com)$", "field": "subject", "label": "subject not bare domain"},
        {"type": "max_links", "value": 2},
        {"type": "max_words", "value": 5, "field": "subject", "severity": "should"},
    ]}

    def test_pass_and_fail(self):
        good = "Subject: Booking button on your site\nHi, your booking button is hidden on mobile. Reply 'no thanks' to opt out."
        r = lk.check(self.RUB, good)
        self.assertTrue(r["pass"], r)
        bad = "Subject: example.co.uk\nI hope this finds you well. " + "word " * 30
        r = lk.check(self.RUB, bad)
        self.assertFalse(r["pass"])
        failed = {f["check"] for f in r["failures"]}
        self.assertIn("opt-out", failed)
        self.assertIn("subject not bare domain", failed)
        self.assertIn("must_not_include", failed)

    def test_should_does_not_block(self):
        txt = "Subject: one two three four five six seven\nok no thanks"
        r = lk.check(self.RUB, txt)
        self.assertTrue(r["pass"])
        self.assertLess(r["score"], 1)

    def test_json_fields_and_hashtags(self):
        rub = {"checks": [{"type": "hashtags_between", "value": [3, 5], "field": "caption"},
                          {"type": "max_chars", "value": 50, "field": "caption"}]}
        self.assertTrue(lk.check(rub, json.dumps({"caption": "Frizz fix #a #b #c"}))["pass"])
        self.assertFalse(lk.check(rub, json.dumps({"caption": "#a #b"}))["pass"])

    def test_cli_exit_code(self):
        (lk.LOOP / "rubrics" / "t.json").write_text(json.dumps(self.RUB))
        f = lk.LOOP / "in.txt"
        f.write_text("Subject: Fine subject\nshort body no thanks")
        self.assertEqual(self.run_cli("check", "t", str(f)), 0)
        f.write_text("Subject: x.com\nbody")
        self.assertEqual(self.run_cli("check", "t", str(f)), 1)


class Experiments(Base):
    def start(self, typ="binary", min_n=20):
        v = lk.LOOP / "variants" / "write.md"
        v.write_text("Lead with the observation.")
        self.run_cli("experiment", "start", "write", str(v), "--metric", "replied", "--type", typ,
                     "--hypothesis", "observation first", "--min-n", str(min_n))
        return lk.experiments()["experiments"][0]

    def test_one_experiment_per_node(self):
        self.start()
        with self.assertRaises(SystemExit):
            self.start()

    def test_balanced_arms(self):
        e = self.start()
        for _ in range(10):
            arm = lk.pick_arm("write")["arm"]
            self.run_cli("log", "write", "--status", "pass", "--arm", arm, "--experiment", e["id"])
        runs, _ = lk.runs_and_outcomes()
        arms = [r["arm"] for r in runs]
        self.assertEqual(arms.count("champion"), 5)
        self.assertEqual(arms.count("challenger"), 5)

    def _feed(self, e, champ_rate, chall_rate, n):
        random.seed(1)
        for arm, rate in (("champion", champ_rate), ("challenger", chall_rate)):
            for i in range(n):
                ref = f"{arm}-{i}"
                self.run_cli("log", "write", "--status", "pass", "--arm", arm, "--experiment", e["id"], "--ref", ref)
                self.run_cli("outcome", "--ref", ref, "--node", "write", f"replied={1 if i < rate * n else 0}")

    def test_continue_until_min_n(self):
        e = self.start()
        self._feed(e, 0.1, 0.5, 5)
        self.assertEqual(lk.decide(e)["decision"], "continue")

    def test_promote_clear_winner(self):
        e = self.start()
        self._feed(e, 0.05, 0.40, 30)
        d = lk.decide(e)
        self.assertEqual(d["decision"], "promote", d)

    def test_reject_worse(self):
        e = self.start()
        self._feed(e, 0.40, 0.05, 30)
        self.assertEqual(lk.decide(e)["decision"], "reject")

    def test_no_win_within_budget(self):
        e = self.start()
        self._feed(e, 0.20, 0.20, 60)
        self.assertEqual(lk.decide(e)["decision"], "reject")

    def test_pending_outcomes_excluded(self):
        v = lk.LOOP / "variants" / "w.md"; v.write_text("x")
        self.run_cli("experiment", "start", "write", str(v), "--metric", "replied", "--hypothesis", "h", "--window-days", "7")
        e = lk.experiments()["experiments"][0]
        self.run_cli("log", "write", "--status", "pass", "--arm", "champion", "--experiment", e["id"])
        self.assertEqual(lk.arm_values(e)["champion"], [])  # still inside window


class Graph(Base):
    G = {"name": "T", "goal": "g", "headline": ["orders"], "nodes": [
        {"id": "a", "label": "A", "kind": "agent", "next": ["b"]},
        {"id": "b", "label": "B", "kind": "human", "next": ["c"]},
        {"id": "c", "label": "C", "kind": "measure", "next": ["imp"]},
        {"id": "imp", "label": "Improve", "kind": "agent", "loop": ["a"]}]}

    def test_layout_handles_loop(self):
        g = json.loads(json.dumps(self.G))
        pos = lk.layout(g)
        self.assertEqual(pos["a"][0], 0)
        self.assertEqual(pos["imp"][0], 3)
        self.assertIn(("imp", "a"), g["_back"])

    def test_cycle_in_next_is_broken(self):
        g = {"name": "c", "nodes": [{"id": "a", "label": "A", "next": ["b"]}, {"id": "b", "label": "B", "next": ["a"]}]}
        pos = lk.layout(g)
        self.assertEqual(pos["b"][0], 1)
        self.assertIn(("b", "a"), g["_back"])

    def test_dashboard_renders(self):
        (lk.LOOP / "graph.json").write_text(json.dumps(self.G))
        self.run_cli("log", "a", "--status", "pass", "--score", "0.9", "--attempts", "2")
        self.run_cli("metric", "orders=3")
        self.run_cli("metric", "orders=5")
        out = lk.LOOP / "d.html"
        self.run_cli("dashboard", str(out), str(lk.LOOP))
        page = out.read_text()
        self.assertIn("<svg", page)
        self.assertIn("1 runs", page)
        self.assertIn("polyline", page)  # sparkline from 2 metric points
        self.assertIn("needs your OK", page)

    def test_mermaid(self):
        self.assertIn("a --> b", lk.mermaid(self.G))
        self.assertIn("imp -.->|improves| a", lk.mermaid(self.G))


if __name__ == "__main__":
    unittest.main(verbosity=1)
