# Memory-First Cost Architecture

## Core Thesis

Do not focus first on replacing OpenAI with one free model. Focus first on eliminating unnecessary LLM calls entirely.

The model should become the last thing Hermy uses, not the first.

## Why This Matters

If Josh cannot afford frequent Hermy interaction, collaboration becomes intermittent. The operating layer must therefore preserve quality while reducing avoidable API calls, token volume, and cloud compute.

The highest-leverage path is to make state, memory, retrieval, and deterministic tools do the first pass of work before any premium model is called.

## Target Flow

```text
Josh message
  → classify intent cheaply
  → search repo state
  → search private OneDrive workspace when relevant and authorized
  → search skills
  → search tasks / decisions / notes
  → build compact answer packet
  → answer directly if enough evidence exists
  → otherwise route to cheapest adequate model
  → use OpenAI only for premium reasoning / hard ambiguity
```

## Cost Ladder

Use the cheapest sufficient layer:

1. **No model**: direct file lookup, grep/search, deterministic scripts, repo state, known docs.
2. **Tiny/cheap model**: formatting, classification, extraction, light summarization.
3. **Mid-cost model**: drafting, coding help, multi-doc synthesis.
4. **Premium model**: strategy, architecture, ambiguous decisions, sensitive reasoning, complex debugging.

## Routing Principles

| Task | Preferred Route |
|---|---|
| Approved roadmap / current state | Read repo docs, no LLM if direct answer exists |
| Private workspace status | Microsoft Graph / OneDrive helper, no LLM unless summarization needed |
| File search | Search tools / scripts, no LLM |
| Contact or metadata extraction | Cheap model or deterministic parser |
| Routine summarization | Cheap model / local model later |
| Coding/debugging | DeepSeek/Qwen/local coding model where viable; premium only when stuck |
| Architecture decisions | OpenAI/premium model |
| Relationship/personality work | Premium or current default when nuance matters |

## Context Compression Strategy

Hermy should not resend large conversation history when a state doc or summary can answer.

Maintain:

- **Long-term memory**: compact durable facts about Josh and stable preferences.
- **Repo state**: operating state, decisions, architecture, plans, public-ish project docs.
- **Private workspace**: personal/private files in OneDrive/Hermy.
- **Active memory**: current thread/task state.
- **Compressed summaries**: periodic summaries of long conversations or project phases.

## Retrieval-First Answering

For questions like “what did we decide?” or “what’s next?” Hermy should:

1. Read Home Base and relevant state docs.
2. Search decisions log.
3. Search current project notes/tasks.
4. Answer from evidence when sufficient.
5. Use a model only to synthesize if the answer is spread across multiple sources or requires judgment.

## Local / Self-Hosted Inference Path

Do not start here as the blocking dependency. Local inference is useful, but only after state/retrieval exists.

Josh's iPad Pro M5 is a serious local compute candidate. The constraint is less raw horsepower and more iOS background/server ergonomics. Treat it as a burst/local/private worker lane, while the cloud Hermes runtime remains the always-on coordinator.

Future options:

- Ollama or Ollama-compatible endpoint where supported
- llama.cpp / MLX-style local runtimes
- vLLM on a cheap GPU instance if sustained load justifies it
- Qwen
- Llama
- DeepSeek

Good future use cases:

- classification
- extraction
- routine summarization
- inbox triage
- coding drafts
- formatting

## Phased Plan

### Phase 1 — Operating State

- Telegram working.
- GitHub repo docs working.
- OneDrive/Hermy private workspace working.
- Repository Maintenance working.
- Home Base and state docs active.

### Phase 2 — Retrieval Before Reasoning

- Search state docs before answering state questions.
- Search skills before re-planning repeat workflows.
- Search OneDrive/Hermy when private workspace context is needed and allowed.
- Add task/contact search when those systems exist.

### Phase 3 — Router

- Use no-LLM retrieval whenever possible.
- Add cheap model routes for simple extraction/summarization.
- Keep OpenAI for premium reasoning.

### Phase 4 — Local / Cheap Workers

- Add local or low-cost inference for routine work.
- Evaluate quality before replacing any premium route.

### Phase 5 — Automatic Memory Hygiene

- Periodic summaries.
- Memory pruning.
- State doc compaction.
- Archive stale notes.

## Critical Refinements

### 1. Do Not Summarize Everything Blindly

"Every Telegram conversation gets summarized" is directionally right but should not mean every message triggers a summary call.

Better rule:

- summarize at phase boundaries
- summarize when a decision is made
- summarize when durable preferences emerge
- summarize before context gets too large
- skip summarization for throwaway chatter unless Josh asks

This preserves continuity without turning summaries into their own cost center.

### 2. True Zero-LLM Answers Require A Pre-Agent Path

If every Telegram message is first sent to a premium LLM, then reading a state file still saves context tokens but not the initial model call.

For actual $0 answers, Hermy eventually needs one of these:

- gateway command shortcuts that answer from files directly
- a lightweight pre-router before the main agent
- scheduled/background summarizers that prepare answerable state
- deterministic scripts for known queries like status, roadmap, repo state, or workspace checks

Near term, we still reduce cost by keeping context compact. Long term, we reduce cost further by routing some messages around premium inference entirely.

### 3. Retrieval Quality Beats Model Shopping

Local/free models only help if the retrieval packet is good. Bad retrieval plus a cheap model still gives bad answers. The priority is therefore:

1. source-of-truth docs
2. consistent folder/task/decision schemas
3. search and retrieval helpers
4. compact answer packets
5. model routing

### 4. Use Premium Models For Relationship And Judgment

Cost control should not flatten the Hermy/JStew relationship. Use cheaper/no-model routes for mechanical state questions, but keep premium reasoning available for high-trust moments, ambiguity, design decisions, and personality/relationship work.

## Current Decision

Memory, retrieval, and state are the real bottlenecks. Local/free models come after or alongside that foundation, not before it. The immediate priority is making Hermy search, read, and maintain shared/private state before spending premium model calls; the next implementation layer is OpenRouter-backed cheap routing plus an iPad/local inference evaluation lane.
