# Hermes State Export

## Build Status
Telegram complete. GitHub live.

## Infrastructure
- Host: DigitalOcean Droplet
- OS: Ubuntu 24.04.3 LTS x64
- Docker: Installed and running
- Hermes: Setup in progress

## Networking
- Public IP: 157.230.163.72
- Private IP: 10.46.0.5
- Tailscale: Pending
- Cloudflare: Not configured

## Storage
- Hermes Data Path: /opt/hermes-data
- GitHub Repo: hermes-opps

## Interfaces
- ChatGPT: Active
- Telegram: Complete
- Email: Not configured
- Other: iPad/iPhone command interfaces

## Providers
- Primary LLM: OpenAI
- Backup LLM: None

## Installed Integrations
- Telegram
- GitHub

## Directory Structure
- /opt/hermes-data
- /opt/hermes-data/repo

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
1. GitHub
2. Tailscale
3. Architecture Review Board
4. Capability Standard
5. Memory Design

## Next Action
Implement Tailscale.

## Backlog
- State export automation
- Task system
- Personal memory
- Capability registry
