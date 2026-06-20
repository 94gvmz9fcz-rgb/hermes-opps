# Cost Control Strategy

## Goal

Enable frequent, high-quality collaboration between JStew and Hermy while minimizing API calls, cloud compute, and paid services.

Quality remains non-negotiable. The strategy is to reduce waste, not capability.

## Principles

1. **Use cheap storage for context.** Prefer Markdown, files, and repo state over repeatedly re-explaining context.
2. **Summarize once, reuse often.** Turn long conversations into compact state docs when they become durable.
3. **Separate capture from processing.** Capturing a note should be free or near-free; processing can happen later when worthwhile.
4. **Use native device capabilities first.** iOS Shortcuts, Files, iCloud Drive, Share Sheet, and Telegram should do simple routing.
5. **Use open-source tools where practical.** Prefer local scripts and OSS utilities over paid SaaS glue.
6. **Spend model calls on judgment.** Use LLM calls for synthesis, planning, writing, debugging, and decisions—not for every file movement.
7. **Batch low-urgency work.** Process inboxes, summaries, and maintenance in batches when possible.
8. **Keep systems inspectable.** Plain text, git diffs, and simple folder structures reduce hidden costs and debugging time.

## Cost-Aware Workflow Pattern

```text
Capture → Store cheaply → Batch/summarize → Decide → Act → Commit durable state
```

Examples:

- Voice/text idea → Telegram or iCloud Inbox → later summary → project doc.
- Photo/nature note → iCloud folder → batch review → nature log.
- Infrastructure decision → conversation → decisions log → commit.
- Repeated task → skill → reuse instead of re-planning.

## What Should Trigger Immediate LLM Processing

Use immediate Hermy processing for:

- time-sensitive tasks
- decisions that unblock work
- repo/document edits
- debugging
- planning sessions
- creative collaboration Josh actively wants to do now

Defer or batch:

- raw idea dumps
- passive notes
- large file collections
- photo folders
- reading queues
- low-urgency summaries

## Compute Strategy

### Near Term

- Use the existing cloud Hermes runtime for always-on access.
- Keep workflows document-driven and lightweight.
- Avoid adding paid cloud services unless they replace a lot of manual work.

### Later Options

- Local/open-source transcription where feasible.
- Scheduled batch processing for inboxes.
- Local embedding/search index if the corpus grows.
- More advanced model routing: cheap model for simple summarization, stronger model for high-value reasoning.
- OpenRouter as the first cheap-model gateway once credentials are available.
- iPad/local inference as a serious parallel lane for bursty private/local work, while keeping the cloud runtime as the always-on coordinator.

## API Call / Rate-Limit Reduction Tactics

- Keep concise state docs in `docs/state/`.
- Use skills for repeat workflows.
- Avoid re-sending large context when a state doc can be read instead.
- Prefer deterministic scripts for mechanical tasks.
- Batch file creation/inspection into fewer tool calls when safe.
- Use background jobs or scheduled cron jobs for long-running work that does not need Josh present.
- Add deliberate pauses between phases when rate limits are likely, especially after large research or generation bursts.
- Use dry-runs before expensive or risky operations.
- Ask Josh for missing info instead of guessing through repeated attempts.

Preferred pattern for large tasks:

```text
Plan → Batch mechanical work → Pause if needed → Verify → Commit/push → Report concise result
```

## Quality Guardrails

Cost saving should not mean:

- using weak reasoning for important decisions
- skipping verification
- hiding state in inaccessible systems
- losing source-of-truth clarity
- over-automating before workflows are understood

## Memory-First Cost Architecture

The biggest cost reducer is not replacing OpenAI with a single free model. It is avoiding unnecessary model calls.

Preferred order:

1. Search memory/state/docs first.
2. Use deterministic tools for file lookup, git state, and workspace checks.
3. Build a compact answer packet from retrieved evidence.
4. Use cheap/local models for routine summarization or extraction when needed.
5. Use OpenAI/premium models only for high-value reasoning, ambiguity, architecture, sensitive decisions, or hard debugging.

See `06-memory-first-cost-architecture.md` for the detailed plan.

## Current Recommendation

Build the first operating layer with:

- Telegram
- OneDrive/Hermy private workspace
- GitHub repo docs
- Hermes memory
- Hermes skills
- iOS Shortcuts
- iCloud Drive as optional Apple-side staging/capture
- OpenRouter as first cheap-model gateway once credentials are available
- iPad/local inference as a parallel evaluation lane, not a blocker

Delay heavier provider sprawl until memory, retrieval, tasks, skills, and state are stable. Do not dismiss the iPad Pro M5 as local compute; evaluate it for local/offline burst work after the routing policy is in place.
