---
name: run-graph
description: Run this repo's agent graph (loop/graph.json) in order, with each agent checking its own work against its rubric before handing off. Use when asked to "run the graph", "run the agents", "run the pipeline", or to run one node by name.
---

# Run the agent graph

Read `loop/README.md` (the loop protocol) and `loop/graph.json`.

## Order
Walk the nodes in graph order, starting from the first node or the node the user named. For each node:

- **agent**: delegate to the subagent named in `agent` using the Task tool. Give it the node id, the items to work on (the outputs of the previous node) and the instruction: "Follow the loop protocol in loop/README.md for node <id>." It must log every item with `loopkit log`. Only items that passed go on to the next node.
- **human**: stop and list what is waiting for approval, with links. Never act for the human: no sending, publishing, posting, spending or merging. Carry on with branches that don't depend on this gate.
- **measure**: run the measuring agent. It records outcomes (`loopkit outcome`) and headline numbers (`loopkit metric`).
- **check**: run the command in `run` and log the result.

A node with `"schedule": "weekly"` runs only when asked or when its last run is 7 or more days old (check with `python loop/loopkit.py graph`).

## Finish
1. `python loop/loopkit.py dashboard loop/dashboard.html`
2. Report in 6 lines or fewer: items in and out of each node, failures with their causes, what is waiting at a human gate, and the next action.

The graph's `notes` and the repo's own rules (CLAUDE.md, README, compliance files) win over this skill.
