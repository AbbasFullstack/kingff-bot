import os
import subprocess
import platform
import asyncio
import httpx
import zipfile
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- ENV VARS ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
OWNER_ID_STR = os.getenv("OWNER_ID", "0")
try:
    OWNER_ID = int(OWNER_ID_STR)
except:
    OWNER_ID = 0

if OWNER_ID == 0:
    OWNER_ID = 8234567890  # <-- APNA TELEGRAM ID YAHAN DAAL DE

# --- System Prompt ---
SYSTEM_PROMPT = """You are Abbas Hussain AI - Personal AI Assistant created by Abbas Hussain.
Abbas Hussain: 16 years old, Full Stack AI Engineer from Islamabad, Pakistan.
Projects: DevDesk AI, OpenAPI Forge, VaultX, CryptoWatch, KingFF Bot (OpenClaw).
Speak in Roman Urdu / Hinglish mix.
Expert: Python, Next.js, Termux, AI, Telegram Bots, Deployment.
Running 24/7 on bot-hosting.net - Day 4.
"""

MODELS = [
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "dots-studio/dots-3-note-preview:free"
]

async def call_ai(user_text: str) -> str:
    if not AI_KEY:
        return "❌ AI_KEY missing!"
    for model_name in MODELS:
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {AI_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/AbbasFullstack/kingff-bot",
                        "X-Title": "Abbas Hussain AI - Day 4"
                    },
                    json={
                        "model": model_name.strip(),
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_text}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }
                )
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            continue
    return "😅 Teen models busy hain, 30 sec baad try karo!"

# --- DAY 3 COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Abbas Hussain AI ONLINE ✅ - Day 4 Final**\n\n"
        "Created by Abbas Hussain (16yo - Islamabad)\n\n"
        "⚡ Models: Flint + Nemotron + DOTS (Auto Fallback)\n\n"
        "**Day 3:**\n"
        "/id - Telegram ID\n"
        "/battery - Server Status\n"
        "/ls - Files\n"
        "/run <cmd> - Shell\n"
        "/ai <sawal> - AI Chat\n\n"
        "**Day 4 NEW:**\n"
        "/deploy - GitHub Pull\n"
        "/backup - Zip Backup\n"
        "/gitpush <msg> - GitHub Push\n"
        "/uptime - Uptime\n\n"
        "Direct message bhejo, AI reply dega!",
        parse_mode='Markdown'
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔑 Teri ID: `{update.effective_user.id}`", parse_mode='Markdown')

async def battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    info = f"🖥️ **Day 4 Server**\nOS: {platform.system()} {platform.release()}\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\nModels: Flint, Nemotron, DOTS ✅\nUptime: 24/7"
    await update.message.reply_text(info, parse_mode='Markdown')

async def ls_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    files = os.listdir(".")
    await update.message.reply_text("📁 Files:\n" + "\n".join([f"- {f}" for f in files]))

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    cmd = " ".join(context.args)
    if not cmd:
        await update.message.reply_text("Usage: /run ls -la")
        return
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        out = (r.stdout + r.stderr).strip() or "No output"
        if len(out) > 3500: out = out[:3500] + "\n...truncated"
        await update.message.reply_text(f"💻 `$ {cmd}`\n\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = " ".join(context.args)
    if not q:
        await update.message.reply_text("Usage: /ai tum kaun ho?")
        return
    await update.message.reply_chat_action("typing")
    reply = await call_ai(q)
    await update.message.reply_text(reply)

# --- DAY 4 NEW COMMANDS ---
async def deploy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    await update.message.reply_text("🔄 GitHub se pull kar raha hun...")
    try:
        r = subprocess.run("git pull origin main", shell=True, capture_output=True, text=True, timeout=30)
        out = (r.stdout + r.stderr)[:3500] or "Already up to date"
        await update.message.reply_text(f"✅ **Deploy Result:**\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Deploy Error: {e}")

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    await update.message.reply_text("📦 Backup bana raha hun...")
    try:
        # Create zip
        with zipfile.ZipFile("backup.zip", "w") as zipf:
            for fname in ["bot.py", "requirements.txt", "README.md", "fly.toml", ".gitignore"]:
                if os.path.exists(fname):
                    zipf.write(fname)
        await update.message.reply_document(document=open("backup.zip","rb"), caption="📦 Day 4 Backup Ready!")
    except Exception as e:
        await update.message.reply_text(f"❌ Backup Error: {e}")

async def gitpush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    msg = " ".join(context.args) or "Day 4 update from Telegram"
    await update.message.reply_text(f"📤 Pushing to GitHub: {msg}")
    try:
        cmds = f'git config user.email "abbas@bot.com" && git config user.name "Abbas AI" && git add . && git commit -m "{msg}" && git push origin main'
        r = subprocess.run(cmds, shell=True, capture_output=True, text=True, timeout=30)
        out = (r.stdout + r.stderr)[:3500]
        await update.message.reply_text(f"✅ Push Result:\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Push Error: {e}")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = f"⏰ **Day 4 Uptime**\n{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\nRunning 24/7 on bot-hosting.net\nPython {platform.python_version()} | {platform.system()}"
    await update.message.reply_text(info, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    reply = await call_ai(update.message.text)
    await update.message.reply_text(reply)

def main():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except:
        pass
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("battery", battery))
    app.add_handler(CommandHandler("ls", ls_files))
    app.add_handler(CommandHandler("run", run_cmd))
    app.add_handler(CommandHandler("ai", ai_command))
    # Day 4
    app.add_handler(CommandHandler("deploy", deploy))
    app.add_handler(CommandHandler("backup", backup))
    app.add_handler(CommandHandler("gitpush", gitpush))
    app.add_handler(CommandHandler("uptime", uptime))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Abbas Hussain AI ONLINE ✅ - Day 4 Final - Full Code")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
