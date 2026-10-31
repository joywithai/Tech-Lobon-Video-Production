# Learning Box

The learning box remembers **explicit user corrections** across future runs. It is structured feedback memory, not automatic model retraining and not a promise that a correction has been verified in a finished video.

- `rules.json` contains active, scoped rules consulted by the planner and written into each job's `applied-rules.json`.
- `events.jsonl` is an append-only log of output checkpoints, feedback, additions, and deactivations. Every completed output records a pending-review checkpoint; it does not invent feedback. It records provenance, UTC time, scope, and optional project/job. Events contain user-provided text; do not put credentials or confidential media in feedback.
- Add corrections after an output using `python -m app feedback add --instruction "..." --observation "..." --scope channel --job JOB_ID`. The user has explicitly requested this memory; do not infer a broad rule from a vague reaction.
- Use `--scope project --project PROJECT_ID` for a one-project rule. The default `channel` scope applies to Tech Lobon future jobs; `global` affects every channel and should be used only when explicitly requested.
- `python -m app feedback list` shows rules. `python -m app feedback disable RULE_ID --reason "..."` deactivates one and leaves the audit record.
- Keep this folder in the repository or sync its changes explicitly; a fresh clone cannot remember uncommitted local feedback.

The six initial rules record actual prior user feedback. Do not use learning to silently change the channel card or fabricate verified fixes. Ask when two active instructions conflict.
