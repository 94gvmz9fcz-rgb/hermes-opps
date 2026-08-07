# diggi — Digital Product Track: Scope & Recommendation
**Date:** 2026-08-07 · **Status:** SCOPED — awaiting go/no-go

## The question
What digital products / offerings / services have **real market liquidity and paying customers right now** that we can build cheaply with the existing stack and sell?

## Market reality (evidence-graded)
| Signal | Grade | Read |
|---|---|---|
| HN "micro-SaaS MRR" thread (Aug 2026, live) | [VERIFIED] | AI podcast tools at $250–2,000 MRR; micro-SaaS pre-sales $200 in 2 weeks — small tools reach real revenue in weeks, not years |
| SMBs spending on AI subscriptions — CBS | [VERIFIED-headline] | Consumers AND SMBs actively paying for AI tools; the money is real and flowing now |
| JPMorgan: AI use among small businesses | [VERIFIED-headline] | SMB adoption rising — they buy outcomes, not software |
| Shopify: revenue acceleration from AI merchant tools (WSJ) | [VERIFIED-headline] | Ecom merchants are the payer segment with the fastest AI spend |
| GitHub Copilot cost squeeze (devops.com) | [VERIFIED-headline] | Pure-AI-wrappers face margin pressure — **the moat must be data/evidence, not the model** |
| Price-monitoring SaaS (Prisync, Price2Spy) $99–500/mo | [HIGH] | Established willingness-to-pay for price/MAP data in ecom |
| Paid niche intelligence briefs $50–500/mo | [HIGH] | Proven category (institutional newsletters 6-fig/yr; niche briefs 3-fig/mo) |

**Thesis:** the durable 2026 plays are (1) evidence/data products with a real pipeline behind them, (2) done-for-you automation for SMB ecom merchants (they pay for outcomes), and (3) niche intelligence where you have domain access. Pure AI wrappers are a commodity — skip.

## What we can build cheaply (existing inventory)
1. **TT fleet** — headless Amazon scanners, evidence hashing, violation packets (Rocky: 12 violations, delivered). Differentiated tech, proven.
2. **Research pipeline** — fireside brief, media monitoring, weekly cadence, human-reviewed output.
3. **CRM + email infra** — Airtable CRM (133 contacts), email ingestion, followup system.
4. **Agent build speed** — end-to-end product builds in days-weeks.

## Candidate wedges

### 🥇 A. MAP Compliance API — the productization of the TT fleet
- **What:** self-serve API + dashboard: brands pull their MAP-violation feeds (alerts, hashed evidence links, historical price charts) programmatically. TT stays the concierge service; diggi is the automated tier. Same fleet, two price points — a product ladder, not cannibalization.
- **Market:** [HIGH] price/MAP monitoring is a paid category ($99–500/mo). Our differentiation = *enforcement-grade evidence* (verifiable packets), not just price data.
- **Liquidity:** medium — warm list already exists (Rocky/Kuiu conversations = seed customers).
- **Build cost:** LOW. Add API layer (FastAPI), API-key auth, usage metering + Stripe billing, docs, a landing page. ~2–4 weeks agent-time.
- **Moat:** the evidence pipeline + fleet; competitors can't cheaply replicate verified-violation packets.
- **Pricing:** $99/mo (1 brand, daily scans) · $299/mo (5 brands, alerts + packets) · $1k+/mo enterprise.

### 🥈 B. Productized AI-ops for SMB ecom (done-for-you automation)
- **What:** flat-fee retainers — price/MAP monitoring + CRM sync + review/email pipelines, run end-to-end by the agent. $750 setup + $500–1,500/mo.
- **Market:** [HIGH/VERIFIED] SMBs are the current AI spenders; services have the shortest sales cycle (1–2 weeks).
- **Build cost:** LOW (reuse TT fleet + CRM + email infra per client).
- **Moat:** weak (services don't scale) — but it's the fastest cash engine and a feedback loop into product A.
- **Risk:** client management overhead.

### 🥉 C. Niche intelligence subscription (productize the fireside pipeline)
- **What:** paid weekly brief for the DoT/IT-channel vertical (or one chosen niche) at $50–200/mo.
- **Market:** [HIGH] category exists; [EST] 1–3% free→paid conversion; **moat = Josh's domain access** (the hardest thing to copy).
- **Build cost:** LOW (pipeline exists); **distribution cost HIGH** — 3–6 months audience-building with no revenue guarantee.
- **Risk:** slowest to liquidity.

### ✂️ Skipped (honest)
- Templates/Notion/prompts — crowded, low-ticket, no moat.
- Trading-data products — regulated-adjacent, thin market.
- Pure AI wrapper SaaS — margin-squeezed commodity (Copilot signal above).

## Recommendation — one lane
**diggi = the MAP Compliance API (A).** It is the only candidate with all three: proven willingness-to-pay, an already-built differentiated asset, and warm first customers. B is the on-ramp cash engine if A stalls; C is the long-tail moat play — both stay scoped, neither gets built in parallel.

## 30/60/90
- **D30:** API layer + auth + Stripe metering on the fleet; landing page; docs; 3 seed brands from the TT outreach list at $99/$299. Metric: 3 paying.
- **D60:** webhook alerting + dashboard; 5 more brands; start B retainers for concierge-wanting brands. Metric: $1.5k MRR.
- **D90:** publish the Rocky case study as the sales asset; raise the evidence tier; decision on C. Metric: $4k MRR or kill/pivot.
- **Kill criteria:** < 3 paying brands by D60 → pivot to B-only (services) or C (intelligence).

## Open decisions for Josh
1. Go/no-go on diggi-A (and whether it lives under the TT umbrella or as a separate brand).
2. Pricing validation against the Rocky/Kuiu conversations (what did they actually say about paying?).
3. If diggi is meant to be strictly NOT-TT-adjacent: B becomes the recommended lane (fastest independent cash).
