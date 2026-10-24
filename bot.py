import os
import subprocess
import platform
import asyncio
import httpx
import zipfile
import threading
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
OWNER_ID = int(os.getenv("OWNER_ID", "8752799745"))

# --- System Prompt - KingFF Journey ---
SYSTEM_PROMPT = """You are Abbas Hussain AI - Personal AI Assistant created by Abbas Hussain.
Abbas Hussain: 16 years old, Full Stack AI Engineer from Islamabad, Pakistan.
Journey: Started with KingFF Faucet (first website for earning) - made own faucet website - now Full Stack AI Engineer.
Projects: KingFF Faucet, DevDesk AI, OpenAPI Forge, VaultX, CryptoWatch, KingFF Bot (OpenClaw).
Speak in Roman Urdu / Hinglish mix like Abbas: bro, yaar, zabardast.
Expert: Python, Next.js, Termux, AI, Telegram Bots, Flask, Deployment, Waterfall Model.
Running 24/7 on bot-hosting.net - Day 5 Web Dashboard Live.
"""

MODELS = [
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "dots-studio/dots-3-note-preview:free"
]

# ===================== DAY 5 WEB DASHBOARD =====================
flask_app = Flask(__name__)

@flask_app.route("/")
def dashboard():
    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Abbas Hussain AI - Day 5</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{background:#0a0e1a;color:#e2e8f0;font-family:'Segoe UI',monospace;padding:20px;max-width:900px;margin:auto;}}
.card{{background:#1a2332;border:1px solid #2d3748;border-radius:16px;padding:22px;margin:18px 0;box-shadow:0 4px 20px rgba(0,0,0,0.3);}}
h1{{color:#60a5fa;font-size:28px;}}h3{{color:#93c5fd;margin-top:0;}}
.status{{color:#4ade80;font-weight:bold;}}.badge{{background:#2563eb;padding:5px 12px;border-radius:20px;font-size:12px;}}
a{{color:#60a5fa;text-decoration:none;}}a:hover{{text-decoration:underline;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:15px;}}@media(max-width:600px){{.grid{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<h1>🤖 Abbas Hussain AI - Day 5 Live Dashboard</h1>
<div class="card">
<h3>👨‍💻 Founder: Abbas Hussain (16yo - Islamabad)</h3>
<p><b>Journey:</b> Vie Faucet se earning → KingFF Faucet (own faucet website) → Full Stack AI Engineer 🚀</p>
<p><b>Projects:</b> KingFF Faucet, DevDesk AI, OpenAPI Forge, VaultX, CryptoWatch, KingFF Bot (OpenClaw)</p>
<p><b>Quote:</b> "Faucet chordiya nahi, seekh ke level up kiya!"</p>
</div>
<div class="grid">
<div class="card">
<h3>🖥️ Server Status</h3>
<p>OS: {platform.system()} {platform.release()}</p>
<p>Python: {platform.python_version()}</p>
<p>Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
<p>Uptime: <span class="status">24/7 Running ✅</span></p>
<p>Repo: <a href="https://github.com/{GITHUB_REPO}" target="_blank">{GITHUB_REPO}</a></p>
<p>PAT: {'✅ Set' if GITHUB_PAT else '❌ Not Set'}</p>
</div>
<div class="card">
<h3>🧠 AI Models</h3>
<p>Flint v1.0 <span class="badge">Free</span></p>
<p>Nemotron 3.5 Super VL <span class="badge">Free</span></p>
<p>DOTS 3 Note Preview <span class="badge">Free</span></p>
<p>Mode: Auto Fallback</p>
</div>
</div>
<div class="card">
<h3>🚀 Waterfall Progress</h3>
<p>✅ Day 1: Termux + Antigravity CLI</p>
<p>✅ Day 2: GitHub + bot-hosting.net 24/7 LIVE</p>
<p>✅ Day 3: Shell Control (/run) + 3 AI Models</p>
<p>✅ Day 4: GitHub Automation + PAT (Push from Telegram)</p>
<p>🔥 Day 5: Web Dashboard (You are here!)</p>
<p>⏳ Day 6: Portfolio Website Integration</p>
</div>
<div class="card">
<h3>📡 API Endpoints</h3>
<p>🏠 <a href="/">/</a> - This Dashboard</p>
<p>📊 <a href="/api/status">/api/status</a> - JSON Status</p>
<p>📁 <a href="/api/files">/api/files</a> - File List</p>
<p>💬 Telegram: @AbbasHussainAI_bot</p>
</div>
<div class="card" style="text-align:center;opacity:0.8;">
<p>Built with ❤️ by Abbas Hussain - From KingFF Faucet to Full Stack Engineer</p>
<p>Islamabad, Pakistan 🇵🇰</p>
</div>
<script>setInterval(()=>{{fetch('/api/status').then(r=>r.json()).then(d=>console.log('Live',d))}},15000);</script>
</body>
</html>
"""

@flask_app.route("/api/status")
def api_status():
    return jsonify({
        "status": "online",
        "day": 5,
        "version": "Day 5 Full Complete",
        "founder": "Abbas Hussain",
        "age": 16,
        "city": "Islamabad",
        "journey": "Vie Faucet -> KingFF Faucet -> Full Stack AI Engineer",
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "time": datetime.now().isoformat(),
        "repo": GITHUB_REPO,
        "pat_set": bool(GITHUB_PAT),
        "models": MODELS,
        "uptime": "24/7",
        "features": ["shell", "ai", "github_pat", "backup", "web_dashboard"]
    })

@flask_app.route("/api/files")
def api_files():
    try:
        files = os.listdir(".")
        return jsonify({"files": files, "count": len(files), "time": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)})

def run_flask():
    port = int(os.getenv("PORT", "8080"))
    print(f"🌐 Web Dashboard starting on port {port} - Day 5 Full")
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ===================== AI CALL =====================
async def call_ai(user_text: str) -> str:
    if not AI_KEY:
        return "❌ AI_KEY missing! Environment me AI_KEY add karo."
    for model_name in MODELS:
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {AI_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": f"https://github.com/{GITHUB_REPO}",
                        "X-Title": "Abbas Hussain AI Day 5 Full"
                    },
                    json={
                        "model": model_name.strip(),
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_text}
                        ],
                        "max_tokens": 1200,
                        "temperature": 0.7
                    }
                )
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    print(f"✅ Model Working: {model_name}")
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ Model {model_name} error: {e}")
            continue
    return "😅 Yaar teeno models busy hain, 30 sec baad phir try karo!"

# ===================== TELEGRAM COMMANDS - FULL =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pat_status = "✅ Set" if GITHUB_PAT else "❌ Not Set"
    await update.message.reply_text(
        f"🤖 **Abbas Hussain AI - Day 5 Full Complete ✅**\n\n"
        f"👨‍💻 Founder: Abbas Hussain (16yo - Islamabad)\n"
        f"🚀 Journey: Vie Faucet → KingFF Faucet → Full Stack Engineer\n\n"
        f"📦 **Repo:** {GITHUB_REPO}\n"
        f"🔐 **PAT:** {pat_status}\n"
        f"🌐 **Web:** Running on :8080\n\n"
        f"**--- Day 3 Commands ---**\n"
        f"/id - Apni Telegram ID\n"
        f"/battery - Server Status (Linux, Python, Time, PAT)\n"
        f"/ls - File List\n"
        f"/run <cmd> - Shell (e.g. /run ls -la)\n"
        f"/ai <sawal> - AI Chat\n\n"
        f"**--- Day 4 Commands ---**\n"
        f"/deploy - GitHub se Pull\n"
        f"/backup - Backup.zip\n"
        f"/setremote - PAT se GitHub Remote Set\n"
        f"/gitpush <msg> - Telegram se GitHub Push\n"
        f"/uptime - Uptime\n\n"
        f"**--- Day 5 NEW ---**\n"
        f"/web - Live Web Dashboard Link\n\n"
        f"💬 Direct message bhejo, AI reply dega!",
        parse_mode='Markdown'
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔑 Teri Telegram ID: `{update.effective_user.id}`", parse_mode='Markdown')

async def battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized! Sirf owner.")
        return
    pat = "✅ Set" if GITHUB_PAT else "❌ Not Set"
    info = (
        f"🖥️ **Day 5 Full Server Status**\n"
        f"OS: {platform.system()} {platform.release()}\n"
        f"Python: {platform.python_version()}\n"
        f"Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
        f"Repo: {GITHUB_REPO}\n"
        f"PAT: {pat}\n"
        f"Web: Running on :8080 🌐\n"
        f"Models: Flint, Nemotron, DOTS ✅\n"
        f"Uptime: 24/7\n"
        f"Journey: KingFF Faucet → Full Stack"
    )
    await update.message.reply_text(info, parse_mode='Markdown')

async def ls_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    try:
        files = os.listdir(".")
        text = "📁 **Files:**\n" + "\n".join([f"- {f}" for f in files])
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized! Sirf owner.")
        return
    cmd = " ".join(context.args)
    if not cmd:
        await update.message.reply_text("Usage: /run ls -la\nExamples:\n/run python --version\n/run cat bot.py | head -20")
        return
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
        output = (result.stdout + result.stderr).strip() or "No output (success)"
        if GITHUB_PAT:
            output = output.replace(GITHUB_PAT, "***PAT***")
        if len(output) > 3500:
            output = output[:3500] + "\n...truncated"
        safe_cmd = cmd.replace(GITHUB_PAT, "***PAT***") if GITHUB_PAT else cmd
        await update.message.reply_text(f"💻 `$ {safe_cmd}`\n\n```\n{output}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("Usage: /ai tum kaun ho?\nYa direct message bhejo!")
        return
    await update.message.reply_chat_action("typing")
    reply = await call_ai(question)
    await update.message.reply_text(reply)

async def deploy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    await update.message.reply_text("🔄 GitHub se pull kar raha hun...")
    try:
        r = subprocess.run("git pull origin main", shell=True, capture_output=True, text=True, timeout=30)
        out = (r.stdout + r.stderr)[:3500] or "Already up to date"
        if GITHUB_PAT:
            out = out.replace(GITHUB_PAT, "***PAT***")
        await update.message.reply_text(f"✅ **Deploy Result:**\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Deploy Error: {e}")

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    await update.message.reply_text("📦 Backup bana raha hun...")
    try:
        with zipfile.ZipFile("backup.zip", "w") as zipf:
            for fname in ["bot.py", "requirements.txt", "README.md", "fly.toml", ".gitignore", "Dockerfile"]:
                if os.path.exists(fname):
                    zipf.write(fname)
        await update.message.reply_document(document=open("backup.zip", "rb"), caption="📦 Day 5 Full Backup Ready!")
    except Exception as e:
        await update.message.reply_text(f"❌ Backup Error: {e}")

async def setremote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not GITHUB_PAT:
        await update.message.reply_text("❌ GITHUB_PAT Environment me nahi hai! Pehle Environment me GITHUB_PAT add karo.\nKey: GITHUB_PAT\nValue: ghp_xxx...")
        return
    try:
        url = f"https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git"
        subprocess.run(f'git remote set-url origin {url}', shell=True, capture_output=True, text=True, timeout=15)
        await update.message.reply_text(f"✅ **Remote set with PAT for {GITHUB_REPO}**\nAb /gitpush kaam karega!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Setremote Error: {e}")

async def gitpush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not GITHUB_PAT:
        await update.message.reply_text("❌ GITHUB_PAT nahi hai! Environment me GITHUB_PAT add karo phir /setremote chalao.")
        return
    msg = " ".join(context.args) or "Day 5 Full update from Telegram"
    await update.message.reply_text(f"📤 Pushing to GitHub: {msg}")
    try:
        subprocess.run(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git', shell=True, timeout=10)
        cmds = f'git config user.email "abbas@bot.com" && git config user.name "Abbas AI" && git add . && git commit -m "{msg}" || echo "nothing to commit" && git push origin main'
        r = subprocess.run(cmds, shell=True, capture_output=True, text=True, timeout=40)
        out = (r.stdout + r.stderr)[:3500]
        if GITHUB_PAT:
            out = out.replace(GITHUB_PAT, "***PAT***")
        await update.message.reply_text(f"✅ **Push Result:**\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Push Error: {e}")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pat = "✅ Set" if GITHUB_PAT else "❌ Not Set"
    info = (
        f"⏰ **Day 5 Uptime Full**\n"
        f"{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
        f"Running 24/7 on bot-hosting.net\n"
        f"Python {platform.python_version()} | {platform.system()}\n"
        f"Repo: {GITHUB_REPO}\n"
        f"PAT: {pat}\n"
        f"Web Dashboard: :8080 🌐\n"
        f"Journey: KingFF Faucet → Full Stack"
    )
    await update.message.reply_text(info, parse_mode='Markdown')

async def web_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    port = os.getenv("PORT", "8080")
    await update.message.reply_text(
        f"🌐 **Day 5 Web Dashboard LIVE!**\n\n"
        f"Local: http://localhost:{port}\n"
        f"API Status: http://localhost:{port}/api/status\n"
        f"API Files: http://localhost:{port}/api/files\n\n"
        f"bot-hosting.net pe public URL hoga to wahan bhi khulega!\n\n"
        f"🚀 **From KingFF Faucet to Full Stack Engineer!**\n"
        f"Your first startup → Now OpenClaw Bot!",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    await update.message.reply_chat_action("typing")
    reply = await call_ai(text)
    await update.message.reply_text(reply)

def main():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception:
        pass

    # Start Flask Web Dashboard (Day 5)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Day 5 Web Dashboard thread started")

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing! Set in bot-hosting.net > Environment")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("battery", battery))
    app.add_handler(CommandHandler("ls", ls_files))
    app.add_handler(CommandHandler("run", run_cmd))
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("deploy", deploy))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("setremote", setremote))
    app.add_handler(CommandHandler("gitpush", gitpush))
    app.add_handler(CommandHandler("uptime", uptime))
    app.add_handler(CommandHandler("web", web_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"Abbas Hussain AI ONLINE ✅ Day 5 Full Complete - KingFF to Full Stack - Python {platform.python_version()}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
