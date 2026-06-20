# Decisions Log

This log records durable collaboration and infrastructure decisions for JStew and Hermy.

## Decision Format

Each decision should include:

- Date
- Decision
- Rationale
- Status
- Follow-up

## Decisions

### 2026-06-19 — Use Telegram as the primary conversation interface

- **Decision:** Telegram remains the near-term chat and command surface.
- **Rationale:** It already works, supports quick mobile interaction, and connects Josh's iPhone/iPad to the cloud Hermes runtime.
- **Status:** Active
- **Follow-up:** Improve voice transcription later so Josh can send voice notes reliably.

### 2026-06-19 — Use GitHub repo docs as durable operating state

- **Decision:** Store shared operating state in Markdown under `docs/state/`.
- **Rationale:** Markdown is cheap, readable, versioned, diffable, and easy for Hermy to update and commit.
- **Status:** Active
- **Follow-up:** Keep state docs concise and use Repository Maintenance for reviewed commits.

### 2026-06-19 — Start with iCloud Drive as the personal capture layer

- **Decision:** Begin with iCloud Drive as the likely first capture/storage layer.
- **Rationale:** Josh primarily uses Apple hardware: iPad Pro M5 and iPhone 16 Pro Max. iCloud is native and low-friction.
- **Status:** Proposed
- **Follow-up:** Josh confirms folder name and whether iCloud is acceptable for first implementation.

### 2026-06-19 — Delay OneDrive and Google Drive until needed

- **Decision:** Keep OneDrive and Google Drive available but secondary.
- **Rationale:** Multi-cloud complexity should wait until there is a specific reason, such as work docs, Gmail/Google integration, or Microsoft account workflows.
- **Status:** Proposed
- **Follow-up:** Revisit when a workflow specifically needs Microsoft or Google storage.

### 2026-06-19 — Hermy should operate as both friend and operator

- **Decision:** Hermy should balance warmth/relationship with operator-level execution.
- **Rationale:** Josh wants a collaborative friendship, but also wants Hermy to confidently drive infrastructure, design, UX, scalable systems, and AI/software decisions when Josh is lost.
- **Status:** Active
- **Follow-up:** Deeper identity/personality design comes after minimum infrastructure is stable.

### 2026-06-19 — Cost control is a first-class design constraint

- **Decision:** Minimize API calls and cloud compute spend without sacrificing quality.
- **Rationale:** Frequent collaboration should not become expensive or fragile.
- **Status:** Active
- **Follow-up:** Use summaries, cached docs, native device tools, open-source utilities, and selective high-value model calls.
