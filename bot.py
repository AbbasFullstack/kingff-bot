import os
from dotenv import load_dotenv
load_dotenv()
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

print("Wispbyte env loading...")
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
VERCEL_URL = os.getenv("VERCEL_URL", "https://abbas-ai-dashboard.vercel.app")
OWNER_ID = int(os.getenv("OWNER_ID", "8752799745"))
print(f"Env check - BOT_TOKEN: {bool(BOT_TOKEN)}, AI_KEY: {bool(AI_KEY)}, PAT: {bool(GITHUB_PAT)}")

SYSTEM_PROMPT = """You are Abbas Hussain AI - by Abbas Hussain, 16yo Full Stack Engineer from Islamabad. Journey: KingFF Faucet -> Full Stack. Speak Roman Urdu/Hinglish. Running on Wispbyte Day 5 Vercel Live."""

MODELS = ["recursive/flint-v1.0:free","nvidia/nemotron-3.5-super-vl:free","dots-studio/dots-3-note-preview:free"]

flask_app = Flask(__name__)
@flask_app.route("/")
def dash():
    return f"<h1>Abbas AI Day 5 Wispbyte</h1><p>Live at {VERCEL_URL}</p><p><a href='/api/status'>API</a></p>"
@flask_app.route("/api/status")
def api():
    return jsonify({"status":"online","day":5,"hosting":"Wispbyte","vercel":VERCEL_URL,"repo":GITHUB_REPO,"time":datetime.now().isoformat()})
@flask_app.route("/api/files")
def apif():
    return jsonify({"files": os.listdir("."), "count": len(os.listdir("."))})
def run_flask():
    port=int(os.getenv("PORT","8080"))
    flask_app.run(host="0.0.0.0",port=port,debug=False,use_reloader=False)

async def call_ai(t):
    if not AI_KEY: return "AI_KEY missing"
    for m in MODELS:
        try:
            async with httpx.AsyncClient(timeout=45) as c:
                r=await c.post("https://openrouter.ai/api/v1/chat/completions",headers={"Authorization": f"Bearer {AI_KEY}","Content-Type":"application/json"},json={"model":m,"messages":[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":t}],"max_tokens":1000})
                d=r.json()
                if "choices" in d: return d["choices"][0]["message"]["content"]
        except: continue
    return "Busy"

async def start(u,c):
    pat="✅" if GITHUB_PAT else "❌"
    await u.message.reply_text(f"🤖 **Day 5 Wispbyte Live ✅**\nRepo: {GITHUB_REPO}\nPAT: {pat}\nVercel: {VERCEL_URL}\nHosting: Wispbyte 🌐\n\nDay 3: /id /battery /ls /run /ai\nDay 4: /deploy /backup /setremote /gitpush /uptime\nDay 5: /web\n\nKingFF Faucet to Full Stack! 🚀",parse_mode='Markdown')
async def get_id(u,c): await u.message.reply_text(f"🔑 ID: `{u.effective_user.id}`",parse_mode='Markdown')
async def battery(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text(f"🖥️ **Wispbyte Day 5**\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\nPAT: {'✅' if GITHUB_PAT else '❌'}\nVercel: {VERCEL_URL} 🌐\nHosting: Wispbyte ✅",parse_mode='Markdown')
async def ls_files(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text("📁 Files:\n" + "\n".join([f"- {f}" for f in os.listdir(".")]))
async def run_cmd(u,c):
    if u.effective_user.id!=OWNER_ID: return
    cmd=" ".join(c.args)
    if not cmd: return await u.message.reply_text("Usage: /run ls -la")
    try:
        r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=25)
        out=(r.stdout+r.stderr).strip() or "No output"
        if GITHUB_PAT: out=out.replace(GITHUB_PAT,"***PAT***")
        if len(out)>3500: out=out[:3500]
        await u.message.reply_text(f"💻 `$ {cmd}`\n```\n{out}\n```",parse_mode='Markdown')
    except Exception as e: await u.message.reply_text(f"Error: {e}")
async def ai_command(u,c):
    q=" ".join(c.args)
    if not q: return
    await u.message.reply_chat_action("typing")
    await u.message.reply_text(await call_ai(q))
async def deploy(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text("🔄 Pulling...")
    r=subprocess.run("git pull origin main",shell=True,capture_output=True,text=True,timeout=30)
    await u.message.reply_text(f"✅ Deploy:\n```\n{(r.stdout+r.stderr)[:3500]}\n```",parse_mode='Markdown')
async def backup(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text("📦 Backup...")
    with zipfile.ZipFile("backup.zip","w") as z:
        for f in ["bot.py","requirements.txt","README.md"]:
            if os.path.exists(f): z.write(f)
    await u.message.reply_document(open("backup.zip","rb"),caption="📦 Wispbyte Backup!")
async def setremote(u,c):
    if u.effective_user.id!=OWNER_ID: return
    if not GITHUB_PAT: return await u.message.reply_text("❌ GITHUB_PAT not set!")
    subprocess.run(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git',shell=True,timeout=10)
    await u.message.reply_text(f"✅ Remote set for {GITHUB_REPO}")
async def gitpush(u,c):
    if u.effective_user.id!=OWNER_ID: return
    if not GITHUB_PAT: return await u.message.reply_text("❌ GITHUB_PAT not set!")
    msg=" ".join(c.args) or "Wispbyte update"
    await u.message.reply_text(f"📤 Pushing: {msg}")
    subprocess.run(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git',shell=True,timeout=10)
    cmds=f'git config user.email "abbas@bot.com" && git config user.name "Abbas AI" && git add . && git commit -m "{msg}" || echo "nothing" && git push origin main'
    r=subprocess.run(cmds,shell=True,capture_output=True,text=True,timeout=40)
    out=(r.stdout+r.stderr)[:3500]
    if GITHUB_PAT: out=out.replace(GITHUB_PAT,"***PAT***")
    await u.message.reply_text(f"✅ Push:\n```\n{out}\n```",parse_mode='Markdown')
async def uptime(u,c): await u.message.reply_text(f"⏰ Wispbyte Day 5 - {datetime.now()} - {VERCEL_URL} 🌐")
async def web_command(u,c): await u.message.reply_text(f"🌐 **Day 5 Wispbyte + Vercel Live!**\n\n🔥 Vercel: {VERCEL_URL}\nLocal: :8080\nHosting: Wispbyte\n\nGitHub: https://github.com/{GITHUB_REPO}",parse_mode='Markdown')
async def handle_message(u,c):
    await u.message.reply_chat_action("typing")
    await u.message.reply_text(await call_ai(u.message.text))
def main():
    try: asyncio.set_event_loop(asyncio.new_event_loop())
    except: pass
    threading.Thread(target=run_flask,daemon=True).start()
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing! Set in Wispbyte > Variables")
        return
    app=Application.builder().token(BOT_TOKEN).build()
    for cmd,fn in [("start",start),("id",get_id),("battery",battery),("ls",ls_files),("run",run_cmd),("ai",ai_command),("deploy",deploy),("backup",backup),("setremote",setremote),("gitpush",gitpush),("uptime",uptime),("web",web_command)]:
        app.add_handler(CommandHandler(cmd,fn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_message))
    print(f"Abbas AI ONLINE ✅ Wispbyte Day 5 - Python {platform.python_version()}")
    app.run_polling(allowed_updates=Update.ALL_TYPES,drop_pending_updates=True)
if __name__=="__main__": main()
