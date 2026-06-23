# CRM Alias Map

*Last updated: 2026-06-23*
**Entity resolution table — canonical names and their known aliases.**
**See also: `docs/crm/acronym-registry.md` for branch-specific DoD acronym resolution (AFLCMC, PEO C3T, SPACECOSM, etc.).**

Read this before resolving any company/organization name from voice, text, or written source.

---

## Companies & Customers

| Canonical | Aliases | Airtable Tag? | Notes |
|---|---|---|---|
| Northrop Grumman Corporation | NGC, Northrop, Northrop Grumman, NG, NG Corp | ✅ Northrop Grumman | Lawrence Carter is a **purchaser at NGC**, not synonymous with any single program. He may cover IBCS and other programs. See contact-level anecdotal notes in OneDrive/contacts/ for his specific scope. |
| Red River Technology | Red River, RR | ❌ | |
| SentinelOne | S1, SentOne | ❌ | Doug Marco contact |
| Wildflower International | Wildflower Intl | ❌ | Marquiese Hannah contact |
| Vertex Wireless | Vertex | ❌ | Ryan Ford contact |
| McKeon Sales Group | McKeon Sales | ❌ | Jade McKeon contact |

## Military / Government

| Canonical | Aliases | Airtable Tag | Notes |
|---|---|---|---|
| United States Air Force | USAF, Air Force, AF | ✅ AF | Western US coverage |
| United States Army | USA, Army | ✅ Army | Western US + Madison, AL |
| United States Navy | USN, Navy | ✅ Navy | |
| United States Marine Corps | USMC, Marines | ✅ USMC | |
| United States Space Force | USSF, Space Force | ✅ Space Force | |

## Programs

| Canonical | Aliases | Associated Entity | Notes |
|---|---|---|---|
| Joint All-Domain Command and Control | JADC2 | Multi-branch | Capability area, not a single customer |
| Integrated Battle Command System | IBCS | Northrop Grumman | Program under NGC |
| Indo-Pacific Command | INDOPACOM, USPACOM | U.S. Army | Josh's expansion target |

## Partners & OEMs

| Canonical | Aliases | Airtable Tag | Notes |
|---|---|---|---|
| Cisco Systems | Cisco | ✅ Cisco | |
| Dell Technologies | Dell, Dell EMC | ✅ Dell | |

## Internal / Misc

| Canonical | Aliases | Airtable Tag | Notes |
|---|---|---|---|
| CyKor LLC | CyKor | ✅ CyKor | Both Org Type and Tags |

---

## Resolution Priority (when multiple aliases match)

1. **Exact name match** → use as-is
2. **Canonical alias match** → resolve to canonical
3. **Company field contains alias** → flag for review (may be wrong company)
4. **No match found** → add to CRM with source noted, flag for Josh to classify

## Zero-Tolerance Triggers

Any of these trigger a pause + flag to Josh:
- Same person appears as two records
- Two companies in the alias map look like they might be the same entity
- A contact's company doesn't match any canonical name or alias

---

*This map grows every time a new alias is encountered during CRM work.*
