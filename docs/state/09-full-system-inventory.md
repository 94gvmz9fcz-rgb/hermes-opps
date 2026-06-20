1|---
2|date: 2026-06-20
3|author: Hermy
4|purpose: Exhaustive inventory of every tool, service, credential, skill, state doc, script, and planned enhancement for external review.
5|---
6|
7|# Hermy System — Full Inventory
8|
9|## 1. Infrastructure & Hosting
10|
11|| Item | Detail | Status |
12||---|---|---|
13|| Cloud host | DigitalOcean Droplet, 4GB RAM, ~110GB disk | Running |
14|| OS | Ubuntu 24.04 LTS x64 | Running |
15|| Container supervisor | s6 (Docker-based) | Running |
16|| Runtime user | `hermes` (uid 10000) | Running |
17|| Python | 3.13.5 | Installed |
18|| uv | 0.11.6 | Installed |
19|| git | 2.47.3 | Installed |
20|| GitHub repo | `git@github.com:94gvmz9fcz-rgb/hermes-opps.git`, branch `main` | Active |
21|| App directory | `/opt/hermes/` | Running |
22|| Hermes data | `/opt/data/` | Active |
23|| Hermes config | `/opt/data/config.yaml` | Active |
24|| Hermes env file | `/opt/data/.env` (credentials) | Active |
25|
26|## 2. Messaging / Interface
27|
28|| Platform | Detail | Status |
29||---|---|---|
30|| Telegram | Bot connected, Home chat ID 8327493830 | Live |
31|| Discord | Not configured | Future |
32|| WhatsApp | Not configured | Future |
33|| Signal | Not configured | Future |
34|| Slack | Not configured | Future |
35|| Email | Not configured | Future |
36|| SMS | Not configured | Future |
37|| Others | WeCom, Feishu, Matrix, DingTalk, BlueBubbles, Weixin | Future |
38|| Hermes Gateway | s6-managed process, PID 3852 | Running |
39|
40|## 3. Model Providers & Credentials
41|
42|| Provider | Auth type | Key stored | Used for | Status |
43||---|---|---|---|---|
44|| OpenAI | API key `****` | `/opt/data/.env` | Premium fallback (architecture, judgment, personality) | Configured, not default |
45|| DeepSeek | API key `****` | `/opt/data/.env` | Primary default model (`deepseek-chat`, funded account) | Live |
46|| OpenRouter | API key `****` | `/opt/data/.env` | Qwen (`qwen/qwen-2.5-7b-instruct`) for title gen, compression; DeepSeek (`deepseek/deepseek-chat-v3-0324`) for subagent delegation | Live |
47|| Gemini/Google | API key `****` | `/opt/data/.env` | Web extraction (`gemini-2.5-flash-lite`) | Live |
48|| Local llama.cpp | None | — | Qwen 2.5 0.5B GGUF, server at `127.0.0.1:18080` | Running |
49|| iPad local | TBD | — | Burst/private inference lane | Future |
50|
51|## 4. Hermes Agent Configuration
52|
53|| Setting | Value |
54||---|---|
55|| Default model | `deepseek-chat` |
56|| Default provider | `deepseek` |
57|| Base URL | `https://api.deepseek.com/v1` |
58|| Cost display | `on` |
59|| Compression | `enabled` |
60|| Memory | `enabled` |
61|| Context compression | `enabled` |
62|| OpenRouter response cache | `on` |
63|| Security: secret redaction | `on` |
64|| Security: TIRITH | `enabled` |
65|| Approvals mode | `manual` |
66|| Delegation provider | `openrouter` |
67|| Delegation model | `deepseek/deepseek-chat-v3-0324` |
68|| Auxiliary: title gen | `openrouter` / `qwen/qwen-2.5-7b-instruct` |
69|| Auxiliary: compression | `openrouter` / `qwen/qwen-2.5-7b-instruct` |
70|| Auxiliary: web extract | `gemini` / `gemini-2.5-flash-lite` |
71|| Auxiliary: vision | `auto` |
72|| STT | `local` (faster-whisper) |
73|| TTS | `edge` (free) |
74|
75|## 5. Enabled Toolsets
76|
77|| Toolset | Purpose | Status |
78||---|---|---|
79|| `web` | Web search and content extraction | Enabled |
80|| `browser` | Browser automation | Enabled |
81|| `terminal` | Shell commands and process management | Enabled |
82|| `file` | File read/write/search/patch | Enabled |
83|| `code_execution` | Sandboxed Python execution | Enabled |
84|| `vision` | Image analysis | Enabled |
85|| `video` | Video analysis | Disabled |
86|| `image_gen` | AI image generation | Enabled |
87|| `tts` | Text-to-speech | Enabled |
88|| `skills` | Skill browsing and management | Enabled |
89|| `todo` | In-session task planning | Enabled |
90|| `memory` | Persistent cross-session memory | Enabled |
91|| `session_search` | Search past conversations | Enabled |
92|| `clarify` | Ask user clarifying questions | Enabled |
93|| `delegation` | Subagent task delegation | Enabled |
94|| `cronjob` | Scheduled task management | Enabled |
95|| `computer_use` | macOS automation | Enabled (macOS only) |
96|| `homeassistant` | Smart home | Disabled |
97|| `spotify` | Spotify control | Disabled |
98|| `yuanbao` | Yuanbao groups | Disabled |
99|| `moa` | Mixture of Agents | Disabled |
100|| `x_search` | X/Twitter search | Disabled |
101|| `context_engine` | Context engine plugin | Disabled |
102|| `video_gen` | Video generation | Disabled |
103|
104|## 6. Skills (installed)
105|
106|| Skill | Category | Purpose |
107||---|---|---|
108|| `hermes-agent` | autonomous-ai-agents | Hermes Agent reference — config, CLI, troubleshooting |
109|| `claude-code` | autonomous-ai-agents | Delegate coding to Claude Code |
110|| `codex` | autonomous-ai-agents | Delegate coding to OpenAI Codex |
111|| `opencode` | autonomous-ai-agents | Delegate coding to OpenCode CLI |
112|| `cost-governor` | productivity | **Active** — model routing, provider setup, cost-awareness procedures |
113|| `onedrive-workspace` | productivity | **Active** — OneDrive/Hermy private workspace management |
114|| `personal-cloud-workspace` | productivity | Cloud workspace setup docs |
115|| `personal-operating-layer` | productivity | Phase 1 operating layer docs |
116|| `telegram-collaboration` | productivity | Telegram collaboration patterns |
117|| `repository-maintenance` | github | **Active** — git review, commit, push workflow |
118|| `repository-file-edits` | software-development | Telegram-driven repo editing |
119|| `github-auth` | github | GitHub SSH/HTTPS auth setup |
120|| `github-pr-workflow` | github | PR lifecycle workflow |
121|| `github-code-review` | github | PR code review |
122|| `github-issues` | github | Issue creation and triage |
123|| `github-repo-management` | github | Repo clone/create/fork |
124|| `codebase-inspection` | github | LOC and language analysis |
125|| *(plus 40+ other installed skills for creative, media, data-science, mlops, note-taking, email, smart-home, dogfood, devops, software-development)* | | |
126|
127|## 7. State Documents (repo/docs/state/)
128|
129|| Document | Purpose |
130||---|---|
131|| `00-jstew-hermy-home.md` | Home Base — who we are, collaboration preferences, safety rules |
132|| `01-infrastructure-plan.md` | Original Phase 1 infrastructure plan |
133|| `02-decisions-log.md` | All durable collaboration and infrastructure decisions |
134|| `03-ios-shortcuts-plan.md` | iOS Shortcut intake plan |
135|| `04-cost-control-strategy.md` | Cost-aware workflow principles and tactics |
136|| `05-onedrive-workspace.md` | OneDrive/Hermy setup and boundary |
137|| `06-memory-first-cost-architecture.md` | Full memory-first architecture with multi-model routing, context compression, local inference path |
138|| `07-model-routing-and-local-inference.md` | Live configuration, routing ladder, verification harness |
139|| `99-hermes-state-export.md` | Build status, infrastructure, providers, critical path, secrets inventory |
140|
141|## 8. Skills Created by Hermy (agent-authored)
142|
143|| Skill | Status |
144||---|---|
145|| `cost-governor` | Active — contains provider integration procedures (OpenRouter, DeepSeek direct, Gemini, local llama.cpp), routing ladder, accident guardrails, live patch recipe |
146|| `onedrive-workspace` | Active — OneDrive/Hermy boundary, Microsoft Graph auth |
147|| `repository-maintenance` | Active — git review, commit, push |
148|| `repository-file-edits` | Active — Telegram-driven repo editing |
149|
150|## 9. Scripts (repo/scripts/)
151|
152|| Script | Purpose |
153||---|---|
154|| `hermy-model-health.py` | **New** — smoke-tests OpenRouter Qwen, DeepSeek direct, Gemini direct, local llama.cpp in one pass. No secrets printed. |
155|| `hermy-provider-preflight.py` | **New** — env file loading, credential presence, OpenRouter endpoint test, command availability. No secrets printed. |
156|| `start-local-llama-qwen.sh` | **New** — daemonise/verify local llama.cpp server (Qwen 2.5 0.5B). |
157|
158|## 10. Private Workspace (OneDrive/Hermy/)
159|
160|| Path | Purpose |
161||---|---|
162|| `_system/` | System-level state, backups, token caches |
163|| `_system/hello-from-hermy.md` | Write-access verification file |
164|| `Inbox/` | Incoming items from iOS Shortcuts, manual file drops |
165|| `Notes/` | Private notes |
166|| `Photos/` | Camera-roll images for batch processing |
167|| `Documents/` | Private documents |
168|| `Projects/` | Project-specific private files |
169|| `Exports/` | State exports, skill exports |
170|| `Archive/` | Stale or completed items |
171|| `work-queue/` | **Planned** — durable task drop zone for worker agents |
172|
173|## 11. Planned Enhancements & Roadmap
174|
175|### Immediate (this weekend)
176|
177|| Item | Type | Priority |
178||---|---|---|
179|| `git tag v0.1-foundation` | Git | P1 |
180|| Nightly tarball backup → OneDrive/Hermy/_backups/ | Cron job | P1 |
181|| Nightly state export → OneDrive/Hermy/_system/state-exports/ | Cron job | P1 |
182|| Worker #1 lane (local llama.cpp via file-queue) | Architecture | P1 |
183|| Inbound dispatch gateway + accident guardrail | Process | P1 |
184|| Protect main branch in GitHub | GitHub config | P1 — needs Josh |
185|| `docs/state/08-resilience-recovery.md` | Doc | P2 |
186|| `git tag v0.2-infra-stable` | Git | P2 |
187|| DO weekly snapshot reminder (cron→Telegram) | Cron | P3 — needs Josh |
188|
189|### Near-term (next 1–2 weeks)
190|
191|| Item | Type |
192||---|---|
193|| Inbound classification with cheap Qwen pre-route | Architecture |
194|| iOS Shortcut intake → Telegram or OneDrive/Inbox | iOS |
195|| Retrieval-first answering (state before model) | Process |
196|| iPad local inference evaluation | Evaluation |
197|| Agent network topology design | Architecture |
198|| Event sourcing architecture sketch | Design |
199|
200|### Medium-term
201|
202|| Item | Type |
203||---|---|
204|| Tailscale | Networking |
205|| Dedicated retrieval/search index | Data |
206|| Task system | Feature |
207|| Contact system | Feature |
208|| Memory/state automatic pruning | Feature |
209|| Capability registry | Architecture |
210|| State export automation | Automation |
211|| DO snapshot automation (if API key added) | Operations |
212|| Multi-agent orchestration (K8s-like worker cluster) | Architecture |
213|
214|### Deferred
215|
216|| Item | Reason |
217||---|---|
218|| Full event sourcing implementation | High complexity; git + backups + state exports already provide 15-min recovery |
219|| Direct Qwen/DashScope account | Redundant with OpenRouter |
220|| Discord, WhatsApp, Signal, etc. gateways | Not needed yet |
221|| Voice calls / phone gateway | Future |
222|| iPad as always-on server | iOS constraints |
223|| Dedicated GPU instance | Not yet justified by load |
224|
225|## 12. Estimated Monthly Costs
226|
227|| Service | Estimated cost | Notes |
228||---|---|---|
229|| DigitalOcean Droplet | ~$15 | 4GB RAM, 110GB disk |
230|| OpenAI (fallback only) | ~$5–15 | Premium-only usage; target minimal |
231|| DeepSeek API | ~$3–10 | Primary model; pay-per-token |
232|| OpenRouter | ~$1–5 | Cheap Qwen + DeepSeek routes |
233|| Gemini API | ~$0–3 | Web extraction; free tier available |
234|| Total estimated | **~$25–50/mo** | Down from ~$50–100+ on OpenAI-only |
235|
236|## 13. Security Boundaries
237|
238|| Rule | Detail |
239||---|---|
240|| Secrets never in repo | Keys stored only in `/opt/data/.env` |
241|| Secrets redacted from output | `security.redact_secrets: true` |
242|| OneDrive access self-limited | Hermy bounded to `OneDrive/Hermy/` unless Josh explicitly authorises broader |
243|| Destructive actions require approval | `approvals.mode: manual` |
244|| Main branch protected | Josh enables protection in GitHub |
245|| No force-push | Hard rule |
246|| Credential names inventoried | Listed in `99-hermes-state-export.md` secrets section |
247|| Health scripts never print keys | `hermy-model-health.py` and `hermy-provider-preflight.py` are designed secret-safe |
248|
249|## 14. Architecture Diagram (text)
250|
251|```text
252|                     Telegram (Josh)
253|                           |
254|                    [ Dispatch Gateway ]
255|                    (classification rule)
256|                           |
257|          ┌────────────────┼────────────────┐
258|          |                |                |
259|    State lookup     Mechanical work    Architecture/personality
260|    (repo/memory)    (cheap route/       (Hermy handles directly)
261|                      worker queue)
262|          |                |
263|     OneDrive/Hermy   Worker #1 (Qwen)
264|                      Worker #2 (DeepSeek)
265|                      Worker #3 (Gemini)
266|```
267|
268|## 15. Open Questions for Reviewer
269|
270|1. Are there security/privacy gaps I'm not seeing in the OneDrive/repo split?
271|2. Does the worker queue pattern (files on OneDrive) scale safely or should we use something lighter?
272|3. Is the multi-agent cluster approach premature given we have exactly one running Hermy instance today?
273|4. Should state export include raw session data or just summaries?
274|5. At what point should we add a separate worker VM vs. colocating workers on the droplet?
275|6. Any single point of failure I'm missing — the gateway is the obvious one, but what else?
276|
277|---
278|
279|*Generated 2026-06-20 for external review. No secrets included.*
280|