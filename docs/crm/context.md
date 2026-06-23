# CRM Prerequisite Context

*Last updated: 2026-06-23*
**Read this before any CRM operation — enrichment, contact update, alias resolution, or relationship mapping.**

---

## Purpose

This document exists to prevent confusion, duplication, and embarrassment when working with Josh's CRM. It captures naming conventions, alias mappings, contextual guardrails, and process prerequisites that are known but not yet encoded anywhere else.

---

## Acronym Resolution

**Every unfamiliar acronym gets resolved same session.** See `docs/crm/acronym-registry.md` for the full registry — branch-tagged, context-scoped, and growing with every interaction.

### Tiered Resolution

| Tier | Meaning | Action |
|---|---|---|
| 🔵 Confident | Expansion + branch scope match public DoD sources | Flagged for Josh's quick review |
| 🟡 Needs Josh | I have pieces but can't scope without you | Surfaced at session end |
| 🔴 Unknown | No match in registry or public sources | Build entry together in same interaction |

### Key Acronyms (Quick Reference — See Registry for Full)

| Acronym | Expansion | Branch | Josh Relevance |
|---|---|---|---|
| AFLCMC | Air Force Life Cycle Mgmt Center | 🇺🇸 USAF (+ 🚀 Space Force) | Primary AF entry point for IT/modernization |
| AFNWC | AF Nuclear Weapons Center | 🇺🇸 USAF | Nuclear-specific, not general IT |
| SPACECOSM | Space Systems Command | 🚀 Space Force | Key USSF entry point |
| PEO C3T | PEO Cmd Ctrl Comms-Tactical | 🪖 Army | Key Army entry point |
| IBCS | Integrated Battle Command System | 🪖 Army (NGC prime) | Lawrence Carter's purview as a purchaser at NGC — not a one-to-one mapping |
| JADC2 | Joint All-Domain Cmd & Control | 🌐 All branches | Broad capability vision |
| INDOPACOM | Indo-Pacific Command | 🌐 Joint combatant cmd | Josh's expansion target |

**Always check the registry before asking Josh what an acronym means.** If it's not there, build an entry before leaving the interaction.

All names in this map are **canonical** (left) with their **known aliases** (right). When Josh mentions an alias in voice or text, resolve to the canonical name before looking up in the CRM.

### Companies & Customers

| Canonical Name | Aliases & Variants | Notes |
|---|---|---|
| Northrop Grumman Corporation | NGC, Northrop, Northrop Grumman, NG, NG Corp | Tags in Airtable already include "Northrop Grumman". Lawrence Carter is listed under "NGC - IBCS" (IBCS is a program, not a separate entity). |
| Red River Technology | Red River, RR | |
| SentinelOne | S1, SentOne | Doug Marco listed under SentinelOne in CRM. |
| Wildflower International | Wildflower Intl | Marquiese Hannah listed here. |
| Vertex Wireless | Vertex | Ryan Ford listed here. |
| McKeon Sales Group | McKeon Sales | Jade McKeon listed here. |

### Military Branches & Agencies

| Canonical Name | Aliases | Airtable Tag |
|---|---|---|
| United States Air Force | USAF, Air Force, AF | ✅ "AF" tag exists |
| United States Army | USA, Army | ✅ "Army" tag exists |
| United States Navy | USN, Navy | ✅ "Navy" tag exists |
| United States Marine Corps | USMC, Marines | ✅ "USMC" tag exists |
| United States Space Force | USSF, Space Force | ✅ "Space Force" tag exists |

### Programs & Initiatives

| Program Name | Aliases | Notes |
|---|---|---|
| Joint All-Domain Command and Control | JADC2 | Multi-branch initiative. Not a single customer — a capability area. |
| Integrated Battle Command System | IBCS | Northrop Grumman program. Lawrence Carter listed under "NGC - IBCS" in CRM. |
| Indo-Pacific Command | INDOPACOM, USPACOM | Josh's Army expansion target. |

### Partners & Distributors

| Name | Aliases | Notes |
|---|---|---|
| Cisco | Cisco Systems | ✅ "Cisco" tag exists in Airtable |
| Dell Technologies | Dell, Dell EMC | ✅ "Dell" tag exists in Airtable |

### Internal

| Name | Aliases | Notes |
|---|---|---|
| CyKor | CyKor LLC | ✅ "CyKor" tag exists. Both in Org Type and Tags. |

---

## Naming Conventions

### CRM Contact Fields

| Field | Rule |
|---|---|
| **Name** | First name + Last initial preferred for cleanup (e.g., "Caitlin C", "Lawrence Carter"). Full names encouraged but not enforced. |
| **Company** | Use **canonical name** from alias map above, not a variant. "NGC - IBCS" is an edge case — prefer "Northrop Grumman Corporation" with a note specifying the program. |
| **Org Type** | One of: DoD, Vendor, Partner, Personal, CyKor. If unsure, leave blank rather than guessing. |
| **Tags** | Military branch tags (AF, Army, Navy, USMC, Space Force) should match the contact's customer org. Company tags (Cisco, Dell, Northrop Grumman) should match their employer. |
| **Notes** | Short inline observations only (<100 words). Full anecdotal feedback goes in OneDrive (see Anecdotal Feedback section below). |

### Zero-Tolerance for:

- **Duplicate contacts** — same person, two records. If found, flag to Josh before merging.
- **Company name variance** — "Northrop Grumman" and "Northrop" should not both appear as separate entries. Resolve to canonical.
- **Tag mismatch** — if someone is DoD but tagged "Vendor" because their current role is at a vendor serving DoD, use `Org Type: Vendor` + `Tags: [relevant military branch]` to capture both.

---

## The Four Repositories — Quick Reference

This is a compact version of the full federated architecture. See the full design doc for details.

| # | Repository | Primary Location | Contents |
|---|---|---|---|
| 1 | CRM | Airtable (Contacts table) | Entity registry — names, companies, titles, contact info. Source of truth for "who exists." |
| 2 | Anecdotal Feedback | `OneDrive/Hermy/contacts/{Company}/{Name}.md` | Josh's personal observations, relationship history, personality notes per contact. Flagged in CRM by `Has Notes ✅` checkbox + `Notes Link 🔗` URL field — tap to open in OneDrive. |
| 3 | Enrichment Vault | `OneDrive/Hermy/enrichment/{Company}.md` + mirror in `docs/enrichment/` | Research: ChatGPT context extracts, independent findings, verified intel, open questions. |
| 4 | Business History & Strategy | `OneDrive/Hermy/strategy/{Category}.md` + mirror in `docs/strategy/` | Wins, losses, burns, strategic vision, program history, capability briefs. |
| 5 | Prerequisite Context | `docs/crm/context.md` (this file) | Aliases, naming rules, and process guardrails. Must be read before any CRM work. |

---

## Process Workflow

### Before Any CRM Operation

1. ✅ Re-read this document (docs/crm/context.md)
2. ✅ Re-read docs/josh/work-profile.md (current role + territory)
3. ✅ Check alias-map section above for name resolution
4. ✅ Check docs/crm/alias-map.md if it exists (more detailed alias data)

### When Josh Dictates Contact Feedback

1. Capture the voice transcription
2. Identify the contact in Airtable CRM
3. Resolve company name via alias map
4. Write feedback to `OneDrive/Hermy/contacts/{Company}/{Name}.md`
5. Update Airtable: set `Has Notes = true`, `Notes Link` URL to OneDrive file
6. If feedback mentions an opportunity or program → cross-reference with strategy docs
7. Log activity to tracker.md

### When Enriching from ChatGPT Context

1. Extract each unique contact/company mentioned
2. Cross-reference against CRM — who exists, who's new?
3. For existing contacts → append verified intel to enrichment vault
4. For new contacts → add to Airtable CRM with source = "ChatGPT context"
5. Resolve all company and name aliases against the alias map
6. Flag any contradictions between ChatGPT context and current CRM data for Josh's review

---

## Contact-by-Contact Audio Intake Plan

Josh will process CRM contacts in ascending or descending order (matching order sent to Hermy). For each contact, he'll dictate:

- **Skip** — no action needed
- **Personal feedback** — what to note about this person
- **Linked opportunity** — if this contact is part of a larger strategy doc or program history
- **Enrichment flag** — if he wants me to independently research this person/company

All of this feeds into the four-repository system above.

---

## Known Gaps & Questions for Josh

| # | Question |
|---|---|
| 1 | Should company-less contacts (29/100 have no company) get "unaffiliated" or should I research their employers? |
| 2 | Email is only 15% populated — do most contacts not share email, or was it never captured? |
| 3 | Title is 1% populated — Josh's preference: leave blank unless he provides it? |
| 4 | Should I pre-fill company names from the CRM cards he shared (Archived CRM Cards in OneDrive)? |

---

*This document is living. It gets updated as new aliases, rules, and patterns emerge during CRM work.*
