import os
import subprocess
import platform
import asyncio
import httpx
import zipfile
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
OWNER_ID_STR = os.getenv("OWNER_ID", "0")
try:
    OWNER_ID = int(OWNER_ID_STR)
except:
    OWNER_ID = 8752799745

if OWNER_ID == 0:
    OWNER_ID = 8752799745

SYSTEM_PROMPT = """You are Abbas Hussain AI - Personal AI Assistant by Abbas Hussain, 16yo Full Stack AI Engineer from Islamabad. Projects: DevDesk AI, OpenAPI Forge, VaultX, CryptoWatch, KingFF Bot. Speak Roman Urdu/Hinglish mix. Running 24/7 on bot-hosting.net Day 4."""

MODELS = [
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "dots-studio/dots-3-note-preview:free"
]

async def call_ai(text: str) -> str:
    if not AI_KEY:
        return "❌ AI_KEY missing!"
    for m in MODELS:
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                r = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {AI_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": f"https://github.com/{GITHUB_REPO}",
                        "X-Title": "Abbas Hussain AI"
                    },
                    json={
                        "model": m.strip(),
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": text}
                        ],
                        "max_tokens": 1000
                    }
                )
                d = r.json()
                if "choices" in d and len(d["choices"]) > 0:
                    return d["choices"][0]["message"]["content"]
        except:
            continue
    return "😅 Models busy, 30 sec baad try karo!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pat_status = "✅ PAT Set" if GITHUB_PAT else "❌ PAT Not Set"
    await update.message.reply_text(
        f"🤖 **Abbas Hussain AI Day 4.1 - PAT Enabled**\n\n"
        f"ID: {update.effective_user.id}\n"
        f"GitHub: {GITHUB_REPO}\n"
        f"PAT: {pat_status}\n\n"
        f"**Day 3:** /id /battery /ls /run /ai\n"
        f"**Day 4:** /deploy /backup /gitpush /uptime /setremote\n",
        parse_mode='Markdown'
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔑 Teri ID: `{update.effective_user.id}`", parse_mode='Markdown')

async def battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    pat = "✅ Set" if GITHUB_PAT else "❌ Not Set - Add GITHUB_PAT in Environment"
    info = f"🖥️ **Day 4.1 Server**\nOS: {platform.system()} {platform.release()}\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\nRepo: {GITHUB_REPO}\nPAT: {pat}\nModels: Flint, Nemotron, DOTS ✅"
    await update.message.reply_text(info, parse_mode='Markdown')

async def ls_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    files = os.listdir(".")
    await update.message.reply_text("📁 Files:\n" + "\n".join([f"- {f}" for f in files]))

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    cmd = " ".join(context.args)
    if not cmd: 
        await update.message.reply_text("Usage: /run ls -la")
        return
    # Hide PAT in logs
    safe_cmd = cmd.replace(GITHUB_PAT, "***PAT***") if GITHUB_PAT else cmd
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=25)
        out = (r.stdout + r.stderr).strip() or "No output"
        if GITHUB_PAT: out = out.replace(GITHUB_PAT, "***PAT***")
        if len(out) > 3500: out = out[:3500] + "\n...truncated"
        await update.message.reply_text(f"💻 `$ {safe_cmd}`\n\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = " ".join(context.args)
    if not q: return
    await update.message.reply_chat_action("typing")
    await update.message.reply_text(await call_ai(q))

async def deploy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text("🔄 GitHub pull...")
    try:
        r = subprocess.run("git pull origin main", shell=True, capture_output=True, text=True, timeout=30)
        out = (r.stdout + r.stderr)[:3500] or "Up to date"
        if GITHUB_PAT: out = out.replace(GITHUB_PAT, "***PAT***")
        await update.message.reply_text(f"✅ Deploy:\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    await update.message.reply_text("📦 Backup...")
    try:
        with zipfile.ZipFile("backup.zip", "w") as z:
            for f in ["bot.py", "requirements.txt", "README.md", "fly.toml", ".gitignore", "Dockerfile"]:
                if os.path.exists(f): z.write(f)
        await update.message.reply_document(open("backup.zip","rb"), caption="📦 Day 4.1 Backup!")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def setremote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not GITHUB_PAT:
        await update.message.reply_text("❌ GITHUB_PAT Environment me nahi hai! Pehle Environment me GITHUB_PAT add karo.")
        return
    try:
        url = f"https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git"
        r = subprocess.run(f'git remote set-url origin {url}', shell=True, capture_output=True, text=True, timeout=15)
        await update.message.reply_text(f"✅ Remote set with PAT for {GITHUB_REPO}\nAb /gitpush kaam karega!", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def gitpush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    msg = " ".join(context.args) or "Day 4.1 update from Telegram"
    if not GITHUB_PAT:
        await update.message.reply_text("❌ GITHUB_PAT nahi hai! Environment me GITHUB_PAT add karo phir /setremote chalao.")
        return
    await update.message.reply_text(f"📤 Pushing: {msg}")
    try:
        # Ensure remote uses PAT
        subprocess.run(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git', shell=True, timeout=10)
        cmds = f'git config user.email "abbas@bot.com" && git config user.name "Abbas AI" && git add . && git commit -m "{msg}" || echo "nothing to commit" && git push origin main'
        r = subprocess.run(cmds, shell=True, capture_output=True, text=True, timeout=40)
        out = (r.stdout + r.stderr)[:3500]
        if GITHUB_PAT: out = out.replace(GITHUB_PAT, "***PAT***")
        await update.message.reply_text(f"✅ Push:\n```\n{out}\n```", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Push Error: {e}")

async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pat = "✅ PAT Set" if GITHUB_PAT else "❌ PAT Missing"
    info = f"⏰ **Day 4.1 Uptime**\n{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n24/7 bot-hosting.net\nPython {platform.python_version()}\nRepo: {GITHUB_REPO}\nPAT: {pat}"
    await update.message.reply_text(info, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    await update.message.reply_text(await call_ai(update.message.text))

def main():
    try: asyncio.set_event_loop(asyncio.new_event_loop())
    except: pass
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print(f"Abbas AI ONLINE ✅ Day 4.1 PAT Enabled - Repo: {GITHUB_REPO}")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
