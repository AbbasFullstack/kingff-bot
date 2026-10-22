# Abbas Hussain AI (kingff-bot)

Personal **Telegram AI assistant** — built, pushed from **Termux (Android)**, and running **24/7** on cloud hosting.

> Waterfall Challenge · Day 2 — No laptop. No credit card. Phone → GitHub → live bot.

---

## What it is

A Telegram bot that answers as **Abbas Hussain AI**, powered by free models via [OpenRouter](https://openrouter.ai).

| Feature | Command / behavior |
|--------|---------------------|
| Start | `/start` — status + intro |
| AI chat | `/ai <question>` or any text message |
| Battery (Termux) | `/battery` — device status, or cloud uptime hint |
| Shell | `/shell <cmd>` — local command runner (use carefully) |

**Models (fallback chain):**
1. `minimax/minimax-m3.1-flash:free`
2. `google/gemma-4-26b-a4b:free`

---

## Stack

- **Runtime:** Python 3.11
- **Bot:** python-telegram-bot v21
- **AI:** OpenRouter Chat Completions API
- **Deploy:** Docker · bot-hosting.net (24/7) · optional Fly.io config included
- **Dev machine:** Android + Termux → `git push`

---

## Project structure
kingff-bot/
├── bot.py              # Telegram handlers + OpenRouter client
├── requirements.txt    # Dependencies
├── Dockerfile          # Container image
├── fly.toml            # Optional Fly.io app config
└── .gitignore
---

## Setup (local / Termux)

### 1. Clone

```bash
git clone https://github.com/AbbasFullstack/kingff-bot.git
cd kingff-bot
2. Environment variables
Create a .env file (never commit it):
BOT_TOKEN=your_telegram_bot_token   # from @BotFather
AI_KEY=your_openrouter_api_key      # from openrouter.ai
3. Install & run
pip install -r requirements.txt
python bot.py
You should see: Abbas Hussain AI ONLINE ✅
Deploy with Docker
docker build -t kingff-bot .
docker run -d --name kingff-bot \
  -e BOT_TOKEN="$BOT_TOKEN" \
  -e AI_KEY="$AI_KEY" \
  kingff-bot
bot-hosting.net (how this instance runs 24/7)
Push this repo to GitHub
Connect the repo on bot-hosting.net
Set BOT_TOKEN and AI_KEY in the panel
Start the process — bot stays online without a laptop
Optional: Fly.io
fly.toml is included (app = "kingff-bot-abbas", region sin).
Set secrets then deploy:
fly secrets set BOT_TOKEN=... AI_KEY=...
fly deploy
Security notes
Never commit .env, tokens, or API keys.
/shell runs host commands — keep the bot private or restrict who can talk to it.
Rotate keys if they were ever pasted in chat or screenshots.
Waterfall Challenge log
Day
Date
Milestone
1
13 Oct 2026
Antigravity CLI (agy) installed + login on Termux
2
22 Oct 2026
This bot live 24/7 via Termux → GitHub → bot-hosting.net + Telegram working
Author
Abbas Hussain · Full-Stack / AI builder · Islamabad, Pakistan (Remote)
Portfolio: https://abbas-portfolio-beta.vercel.app
GitHub: https://github.com/AbbasFullstack
LinkedIn: https://linkedin.com/in/abbas-hussain-56a61338b
License
Personal project — use / fork for learning. Give credit if you ship a public fork.
