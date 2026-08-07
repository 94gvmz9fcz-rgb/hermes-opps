# Orchestrator Operating Model

## Purpose

This document defines how AStew operates when Josh wants the system to behave like a real operator: assign work, supervise execution, verify outcomes, and keep a record of what happened.

## Role Split

### AStew — Orchestrator
- Breaks work into tasks
- Chooses the right worker lane
- Sets success criteria
- Checks progress and final output
- Reconciles disagreements before reporting back

### Worker Agents — Executors
- Do the assigned work
- Report status as they go
- Never widen scope on their own
- Never assume missing context without flagging it
- Deliver a result or a blocker, not a guess

### Chex — Adversarial Checker
- Reviews substantial decisions
- Challenges assumptions
- Flags gaps, risks, and missing verification
- Escalates if the answer is still not safe or coherent

### Deterministic Scripts — Repeatable Checks
- Preferred for routine verification, monitoring, counting, and state inspection
- Should be used whenever a script can answer the question without LLM reasoning

## Operating Rules

1. **One orchestrator, many workers.**
   AStew coordinates. Workers execute. Chex checks.

2. **No hidden work.**
   Every worker task must produce a visible log or result file.

3. **No silent failure.**
   If a worker hits a blocker, it must report the blocker directly.

4. **No scope drift.**
   Workers do not expand tasks without explicit instruction.

5. **Review before report.**
   Anything meaningful gets checked before Josh sees the final answer.

## Logging Contract

Every worker task should record:
- task name
- start time
- finish time
- files touched
- result
- blockers
- next step if incomplete

Every review should record:
- pass/fail
- challenge notes
- missing evidence
- recommended next action

## Pilot Standard

For the first pilot lane:
- Keep the task narrow
- Keep the worker count to one
- Keep the output format simple
- Keep the logs local and readable
- Do not add a second lane until the first lane is stable

## Success Criteria

The model works if:
- AStew can assign work without handholding
- The worker completes the task or clearly reports the blocker
- Chex catches anything sloppy or incomplete
- Josh gets a clean summary instead of a pile of confusion

## Failure Modes

- AStew becomes the bottleneck because the task is too broad
- Workers start guessing instead of reporting blockers
- Logs are skipped or become inconsistent
- Chex is treated as optional on meaningful decisions

## Immediate Next Step

Stand up one narrow worker lane and run a single end-to-end test: assign → execute → verify → report.