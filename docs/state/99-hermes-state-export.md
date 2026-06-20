# Hermes State Export

## Build Status
Telegram complete. GitHub live.
- Telegram: Complete
- GitHub: Complete
- Telegram-driven repo editing: Complete
- Architecture Review Board: Complete
- Decisions Log: Complete
- OneDrive private workspace: Complete
- Memory-first cost architecture: Documented
- Model routing / local inference plan: Documented
- Cost Governor skill: Created

## Infrastructure
- Host: DigitalOcean Droplet
- OS: Ubuntu 24.04.3 LTS x64
- Docker: Installed and running
- Hermes: Setup in progress
- OneDrive/Hermy workspace: Active via Microsoft Graph

## Networking
- Public IP: 157.230.163.72
- Private IP: 10.46.0.5
- Tailscale: Pending
- Cloudflare: Not configured

## Storage
- Hermes Data Path: /opt/hermes-data
- GitHub Repo: hermes-opps
- Private Workspace: OneDrive/Hermy

## Interfaces
- ChatGPT: Active
- Telegram: Complete
- Email: Not configured
- Other: iPad/iPhone command interfaces
- Private workspace: OneDrive/Hermy active

## Providers
- Primary LLM: OpenAI
- Backup LLM: None configured
- First cheap-model gateway: OpenRouter configured and smoke-tested
- Cheap auxiliary model route: `qwen/qwen-2.5-7b-instruct` for title generation and compression
- Delegation/subagent route: `deepseek/deepseek-chat-v3-0324` via OpenRouter
- Local inference: iPad/local lane approved for evaluation; not yet configured

## Installed Integrations
- Telegram
- GitHub
- OneDrive / Microsoft Graph

## Directory Structure
- /opt/hermes-data
- /opt/hermes-data/repo
- OneDrive/Hermy/_system
- OneDrive/Hermy/Inbox

## Naming Conventions
- Repo: hermes-opps
- Exports: export-YYYY-MM-DD
- Backups: backup-YYYY-MM-DD

## Secrets Inventory
Name only. Never values.
- OpenAI API key
- Telegram bot token
- GitHub PAT

## Open Decisions
- Memory system design
- Capability specification
- Task system design
- Tailscale implementation

## Current Critical Path
1. Restart/reset Telegram gateway/session so OpenRouter routing config is loaded
2. Model routing validation harness
3. iOS Shortcut intake
4. Retrieval-first memory/state search
5. iPad/local inference evaluation
6. Tailscale
7. Capability Standard
8. Memory Design

## Next Action
Restart the gateway/session, then run the routing validation matrix against OpenRouter cheap routes and premium fallback.

## Backlog
- State export automation
- Task system
- Personal memory
- Capability registry
