---
name: self-improve
description: Run the self-improvement step: decide running A/B experiments on agent prompts and start one evidence-based change on the weakest node. Use when asked to improve the agents, run the improver, or weekly.
---

Delegate to the `improver` subagent with: "Run the self-improvement step for this repo." Then regenerate the dashboard with `python loop/loopkit.py dashboard loop/dashboard.html` and pass on the improver's report as it is.
