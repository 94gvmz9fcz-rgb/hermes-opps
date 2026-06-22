# Hosting & Delivery — Enhancement Tracker

> **Status:** 🔴 Blocked — see below
> **Filed:** 2026-06-22

## Problem

GitHub Pages on a free account **requires the repo to be public**. We made the repo public to enable Pages (gallery + dashboard), but this is not ideal long-term because:

- The repo contains proprietary system design docs
- Branch names, issue references, and project structure are visible
- Private repo is the right default for our operating model

## Current Workaround

Repo is public for now. Pages is live at `https://94gvmz9fcz-rgb.github.io/hermes-opps/`. No credentials or secrets are in the repo (vault is local), so the risk is limited — but it's a compromise.

## Better Paths to Evaluate

### Path A: Cloudflare Pages (Recommended)
- Free tier: unlimited sites, 500 builds/month, 1GB storage
- Supports private repos via direct GitHub integration
- Custom domain support
- Global CDN (fast everywhere)
- **Downside:** Need a Cloudflare account setup (~10 min)

### Path B: Netlify
- Free tier: 100GB bandwidth, 300 min build/month
- Also supports private repos
- Slightly more polished UI
- **Downside:** Same setup overhead, slightly lower free tier than Cloudflare

### Path C: Keep GitHub Pages + Accept Public Repo
- Zero additional setup
- Works now
- **Risk:** Proprietary design docs are visible. Acceptable for now but not ideal.

## Recommendation

Review when you have 15 minutes to set up a Cloudflare or Netlify account. The swap is:
1. Create account → link GitHub repo (private) → point at gh-pages branch
2. Update DNS (optional, for custom domain)
3. Verify gallery + dashboard URLs work
4. Set repo back to private

**Total time:** ~15 min for Cloudflare, ~10 min for Netlify

## Links
- Cloudflare Pages: https://pages.cloudflare.com/
- Netlify: https://www.netlify.com/
