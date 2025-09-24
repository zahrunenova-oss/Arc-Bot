# Arc-Bot v1: Arkadian Grove Ceremonial Steward

## Overview
Arc-Bot v1 handles initiation rituals for The Arkadian Grove:
- Auto-assigns Pilgrim role on join.
- Sends DM for Name | Intent | Node Location.
- Relays responses to #ritual-onboarding.
- Logs receipts to #ledger via webhook.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   - DISCORD_TOKEN: Bot token from Discord Developer Portal
   - WEBHOOK_URL: FastAPI webhook endpoint (e.g., http://your-service/ledger)
   - PORT: 8000
3. Run: `python arc_bot.py`
4. Invite bot to server via OAuth2 URL (scopes: bot, applications.commands).

## Commands
- /apply: Modal for role application.
- /ritual: Button to schedule initiation (replace with your Calendly link).

## Hosting
Use Railway or Render for free hosting. Push to GitHub, connect, and deploy.

## Notes
- Replace Calendly link in /ritual command.
- Ledger is in-memory; swap with Joplin or DB for persistence.
