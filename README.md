<div align="center">

# ⚡ Abbas Hussain AI
### `kingff-bot` · Personal Telegram Assistant

**Built on Android · Pushed from Termux · Live 24/7 on the cloud**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI-000000?style=for-the-badge)](https://openrouter.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-24%2F7%20LIVE-22c55e?style=for-the-badge)](https://github.com/AbbasFullstack/kingff-bot)

> Waterfall Challenge · Day 2  
> No laptop. No credit card. Phone → GitHub → production bot.

[Portfolio](https://abbas-portfolio-beta.vercel.app) · [GitHub](https://github.com/AbbasFullstack) · [LinkedIn](https://linkedin.com/in/abbas-hussain-56a61338b)

</div>

---

## ✨ What is this?

A **Telegram AI assistant** that talks as **Abbas Hussain AI** — powered by free models through OpenRouter, containerized with Docker, and kept online 24/7 without a PC.

| | Feature | How |
|---|---------|-----|
| 🚀 | Start bot | `/start` |
| 🤖 | Chat with AI | `/ai <question>` **or** any normal message |
| 🔋 | Battery / uptime | `/battery` |
| 💻 | Shell runner | `/shell <cmd>` *(use carefully)* |

**Model fallback chain**

```
minimax/minimax-m3.1-flash:free
        ↓ (if fail)
google/gemma-4-26b-a4b:free
```

---

## 🧱 Stack

```text
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│  Telegram   │───▶│  bot.py      │───▶│  OpenRouter AI │
│  (users)    │◀───│  handlers    │◀───│  free models   │
└─────────────┘    └──────────────┘    └────────────────┘
                          │
                          ▼
                   Docker / cloud
                   bot-hosting.net
```

- **Language:** Python 3.11  
- **Bot SDK:** `python-telegram-bot` v21  
- **AI API:** OpenRouter Chat Completions  
- **Deploy:** Docker · bot-hosting.net · optional Fly.io  
- **Built on:** Android + Termux → `git push`

---

## 📁 Project structure

```text
kingff-bot/
├── bot.py              # Telegram handlers + AI client
├── requirements.txt    # Dependencies
├── Dockerfile          # Production image
├── fly.toml            # Optional Fly.io config
├── .gitignore
└── README.md           # You are here
```

---

## ⚡ Quick start

### 1 · Clone

```bash
git clone https://github.com/AbbasFullstack/kingff-bot.git
cd kingff-bot
```

### 2 · Secrets

Create `.env` *(never commit this file)*:

```env
BOT_TOKEN=your_telegram_bot_token_from_BotFather
AI_KEY=your_openrouter_api_key
```

### 3 · Run

```bash
pip install -r requirements.txt
python bot.py
```

Terminal should print:

```text
Abbas Hussain AI ONLINE ✅
```

---

## 🐳 Docker

```bash
docker build -t kingff-bot .

docker run -d --name kingff-bot \
  -e BOT_TOKEN="$BOT_TOKEN" \
  -e AI_KEY="$AI_KEY" \
  kingff-bot
```

---

## ☁️ 24/7 deploy (bot-hosting.net)

This is how the live instance runs — **from a phone**:

1. Push this repo to GitHub  
2. Connect the repo on **bot-hosting.net**  
3. Add `BOT_TOKEN` + `AI_KEY` in the panel  
4. Start process → bot stays online without a laptop  

### Optional · Fly.io

`fly.toml` is ready (`app = kingff-bot-abbas`, region `sin`):

```bash
fly secrets set BOT_TOKEN=... AI_KEY=...
fly deploy
```

---

## 🔐 Security

- Never commit `.env`, tokens, or API keys  
- `/shell` executes host commands — keep the bot private or restrict access  
- Rotate keys if they ever appeared in screenshots or chat  

---

## 📅 Waterfall Challenge

| Day | Date | Milestone | Status |
|-----|------|-----------|--------|
| **1** | 13 Oct 2026 | Antigravity CLI (`agy`) on Termux — install + login | ✅ |
| **2** | 22 Oct 2026 | Abbas Hussain AI live 24/7 · Termux → GitHub → bot-hosting · Telegram working | ✅ |

---

## 👤 Author

**Abbas Hussain**  
Full-Stack Developer · AI builder · Islamabad, Pakistan (Remote)

| | |
|--|--|
| 🌐 | [abbas-portfolio-beta.vercel.app](https://abbas-portfolio-beta.vercel.app) |
| 💻 | [github.com/AbbasFullstack](https://github.com/AbbasFullstack) |
| 🔗 | [LinkedIn](https://linkedin.com/in/abbas-hussain-56a61338b) |

---

<div align="center">

**Shipped under constraints.**  
Phone only · Termux · GitHub · Cloud · Live.

`Made with focus · AbbasFullstack`

</div>
