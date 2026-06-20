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

Do not start here. Local inference is useful, but only after state/retrieval exists.

Future options:

- Ollama
- llama.cpp
- vLLM
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

## Current Decision

Memory, retrieval, and state are the real bottlenecks. Local/free models come later. The immediate priority is making Hermy search, read, and maintain shared/private state before spending premium model calls.
