# Agent loop

This repo runs as a graph of agents that check their own work and get better over time. It has four layers:

1. **Agents.** Each one has a single job and lives in `.claude/agents/<name>.md`.
2. **Loops.** Every agent output must pass a rubric before it moves on. If it fails, the agent revises it, up to 3 attempts.
3. **Graph.** `loop/graph.json` fixes the order agents run in. Nobody has to hope one giant prompt gets every step right. The `run-graph` skill walks it.
4. **Self-improvement.** The `improver` agent reads results and tests one prompt change at a time against the current version (A/B). It keeps a change only if the numbers say it's better, and a human merges the change.

## Files

| Path | What it is |
|---|---|
| `loop/graph.json` | Nodes (agent / human gate / measure), their order, the headline metrics |
| `loop/rubrics/<node>.json` | Hard checks run by `loopkit check`. A failure blocks the hand-off. |
| `loop/rubrics/<node>.md` | Judgement rubric. The `critic` agent scores against it in a fresh context, so no agent grades its own work. |
| `loop/guardrails.md` | Things the improver must never change |
| `loop/runs.jsonl` | Every node run, plus outcomes that arrive later (a reply, a sale, views) |
| `loop/metrics.jsonl` | Headline numbers over time |
| `loop/experiments.json` | A/B tests of prompt changes |
| `loop/variants/<node>/<exp>.md` | The challenger instructions being tested |
| `loop/lessons.md` | What each finished experiment taught. The improver reads it before proposing anything. |
| `loop/loopkit.py` | The engine. Stdlib Python 3.10+, no installs. Tests: `python loop/test_loopkit.py` |

## The loop every agent follows

```
1. python loop/loopkit.py variant <node>
   -> {"arm": "challenger", "file": "loop/variants/write/exp-001.md", ...}
   If a file is given, read it and follow it on top of your normal instructions.
2. Do the job. Write the output to a file (e.g. loop/out/<node>-<ref>.md).
3. python loop/loopkit.py check <node> <file>        # hard gate, exit 1 = fail
4. Ask the critic agent to score the file against loop/rubrics/<node>.md
5. Failed either? Revise using the listed failures. Max 3 attempts in total.
6. python loop/loopkit.py log <node> --status pass|fail --score <critic 0-1> \
     --attempts <n> --arm <arm> --experiment <id> --ref <record id>
7. Only a pass moves to the next node. After 3 fails: stop that item and report why.
```

Results that arrive later are attached by reference:

```
python loop/loopkit.py outcome --ref FD-0041 --node write replied=1 positive=0
python loop/loopkit.py metric sent=12 replies=1
```

## See it

```
python loop/loopkit.py dashboard loop/dashboard.html     # open in a browser
python loop/loopkit.py graph --mermaid                   # paste into any Mermaid viewer
python loop/loopkit.py experiment status
```

## Rules for the self-improvement step

- One experiment per node at a time. Each one changes one thing.
- A change is promoted only when `experiment decide` says `promote`: both arms have reached `min_n` and the challenger wins at p < alpha. Too little data means "continue", never a guess.
- Promotion means a branch plus a pull request. The human merges it; nothing is auto-merged.
- Rubric gates can only get stricter without human approval. The improver never weakens a check to make its numbers look better.
- `loop/guardrails.md` wins over everything else.
