# Model Routing and Local Inference Plan

## Purpose

Reduce avoidable premium OpenAI usage without flattening Hermy's quality, continuity, or relationship with Josh.

The target is not to replace OpenAI with one free model. The target is to make OpenAI the premium specialist and make retrieval, deterministic tools, cheaper models, and local models handle the work they are actually good at.

## Current Verified Runtime State

As of this document:

- Primary model/provider: `gpt-5.5` via `openai-api`.
- Compression: enabled.
- Memory: enabled.
- OpenRouter response cache setting: enabled.
- Additional provider credentials visible in the current runtime: OpenRouter configured; other cheap/direct providers not configured.
- Hermes CLI binary is available at `/opt/hermes/.venv/bin/hermes`; it may not be on the default tool shell `PATH`.
- Local cloud runtime has limited RAM for serious local inference; Josh's iPad Pro M5 should be treated as a promising local compute lane, not ignored.
- OpenRouter smoke test succeeded using `qwen/qwen-2.5-7b-instruct`.

Do not store API keys, tokens, or local model credentials in this repo.

## Routing Ladder

Use the cheapest layer that preserves correctness.

| Tier | Route | Use for | Cost posture |
|---:|---|---|---|
| 0 | No model | direct repo lookup, file search, git status, OneDrive checks, deterministic scripts | free except compute |
| 1 | Tiny/cheap model | classification, extraction, formatting, short summaries | low cost |
| 2 | Mid-cost model | draft synthesis, routine coding, research drafts | controlled spend |
| 3 | Premium OpenAI | architecture, judgment, ambiguity, emotional/personality continuity, high-stakes debugging | intentional spend |
| 4 | Human approval | destructive actions, secrets, broad OneDrive access, account changes | safety gate |

## Initial Provider Strategy

### 1. OpenRouter first

OpenRouter is the fastest practical integration because one credential unlocks multiple cheap models and lets Hermy test quality/cost before committing to direct provider accounts.

Recommended uses:

| Workload | Candidate route |
|---|---|
| title generation | cheap Qwen/Gemini-class model |
| compression/summarization | Qwen/Gemini-class model |
| extraction/classification | Qwen-class model |
| routine coding/research draft | DeepSeek-class model |
| premium judgment | OpenAI default |

### 2. Direct providers later

Only add direct provider credentials when telemetry shows repeated usage that justifies provider-specific setup.

Candidate direct providers:

- DeepSeek: coding/research drafts if cheaper or more reliable direct.
- Qwen/DashScope or Qwen OAuth: extraction/summarization if OpenRouter is insufficient.
- Gemini: cheap auxiliary fallback if useful.

### 3. Local/iPad lane in parallel, not as a blocker

Josh's iPad Pro M5 has meaningful local compute/storage. Treat it as a serious future worker lane for private/offline/local inference, especially for:

- local summaries
- inbox triage
- extraction/classification
- draft cleanup
- embeddings/search experiments
- privacy-sensitive local processing

However, do not block the core architecture on iPad local inference. The immediate win remains retrieval/no-call routing.

## iPad Local Inference Direction

The iPad should be evaluated as a local worker, not as the always-on gateway host.

Likely pattern:

```text
iPad local model app / local inference endpoint
  ↔ Shortcuts / local automation
  ↔ OneDrive/Hermy files or Telegram handoff
  ↔ cloud Hermy for always-on coordination
```

Candidate approaches to validate:

1. iPad app with local LLM support for manual/offline work.
2. Shortcuts-based local summarization/extraction if an app exposes actions.
3. Local network endpoint only if iPad can run a stable server-style inference process.
4. Cloud Hermy treats iPad outputs as files in `OneDrive/Hermy/Inbox` or `Exports`, not as trusted state until reviewed.

Important constraint: iPad compute is powerful but iOS background execution/server behavior may be the limiting factor. Use it where it is strong: local bursts, private processing, and manual initiated workflows.

## Premium Model Protection Rules

Keep premium OpenAI for:

- architecture decisions
- ambiguous strategy
- sensitive personal/relationship moments
- hard debugging when cheap/local models are stuck
- final synthesis when correctness matters
- Hermy personality/continuity work

Do not route these blindly to a cheap model unless Josh explicitly requests a cheap pass or the result is clearly marked as draft/low-confidence.

## Cost Governor Decision Procedure

Before invoking a model for a task, check:

1. Can this be answered from `docs/state/`, skills, memory, session search, or OneDrive/Hermy files?
2. Can a deterministic script answer it?
3. Is this a routine transformation suitable for a cheap model?
4. Is this a coding/research draft suitable for DeepSeek/Qwen-class models?
5. Does this require premium reasoning, judgment, emotional nuance, or high-stakes accuracy?
6. Should Josh approve before the action continues?

Record the route for meaningful work:

```text
route: no-model | cheap | mid | premium | human
source_checked: repo docs | session DB | memory | OneDrive | skills | web | none
fallback_reason: retrieval miss | ambiguity | quality | safety | user preference
```

## Configuration Applied

Live configuration now uses:

```text
display.show_cost = true
openrouter.response_cache = true
auxiliary.title_generation = openrouter / qwen/qwen-2.5-7b-instruct
auxiliary.compression = openrouter / qwen/qwen-2.5-7b-instruct
delegation = openrouter / deepseek/deepseek-chat-v3-0324
```

Primary premium model remains OpenAI/default. Restart/reset gateway/session after config changes so the running Telegram agent loads the updated environment.

## Validation Harness

Use this test matrix before changing defaults broadly.

| Test prompt | Expected route |
|---|---|
| What is our current roadmap? | no model / repo state |
| What did we decide about iCloud vs OneDrive? | no model / decisions + state docs |
| Summarize this inbox note | cheap/local model |
| Extract names/dates/tasks from this text | cheap/local model |
| Draft code for a small utility | DeepSeek/Qwen-class model |
| Review this architecture tradeoff | premium OpenAI |
| Talk with Josh about Hermy personality/identity | premium OpenAI |

Acceptance criteria:

- The answer cites or names the source when retrieved from state.
- Cheap/local model output is marked as draft when quality is not proven.
- Premium model usage is intentional and explainable.
- No secrets are logged or committed.

## Immediate Decision

Proceed with OpenRouter + Cost Governor policy first. Keep iPad local inference as an active parallel lane for evaluation, but do not delay retrieval/state/model-routing work waiting for local infrastructure.
