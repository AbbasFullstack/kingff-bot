import os
from dotenv import load_dotenv
load_dotenv()
import subprocess
import platform
import asyncio
import httpx
import zipfile
import threading
import json
import re
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ================= ENV =================
print("🔧 Abbas AI Day 1-6 Final Loading...")
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
VERCEL_URL = os.getenv("VERCEL_URL", "https://abbas-ai-dashboard.vercel.app")
OWNER_ID = int(os.getenv("OWNER_ID", "8752799745"))
PORT = int(os.getenv("PORT", "8080"))

print(f"BOT_TOKEN: {bool(BOT_TOKEN)} | AI_KEY: {bool(AI_KEY)} | PAT: {bool(GITHUB_PAT)} | Repo: {GITHUB_REPO}")

# ================= PROMPTS =================
AGENT_SYSTEM = """You are Abbas Agent - Autonomous AI Agent by Abbas Hussain (16yo, Islamabad).
Journey: Vie Faucet -> KingFF Faucet -> Full Stack -> Agent!
You THINK, PLAN, ACT using TOOLS.
Tools:
1. shell - {"tool":"shell","cmd":"ls -la"}
2. read - {"tool":"read","file":"bot.py"}
3. write - {"tool":"write","file":"test.txt","content":"hello"}
4. gitpush - {"tool":"gitpush","msg":"update"}
5. deploy - {"tool":"deploy"}
6. restart - {"tool":"restart"}
RULES: Break goal into steps, use tools one by one, speak Roman Urdu/Hinglish, Wispbyte hosting."""

SYSTEM_PROMPT = """You are Abbas Hussain AI - Personal AI by Abbas Hussain, 16yo Full Stack Engineer from Islamabad.
Journey: Vie Faucet -> KingFF Faucet -> Full Stack -> Agent.
Speak Roman Urdu/Hinglish - bro, yaar, zabardast.
Running on Wispbyte + Vercel Live.
Helpful, funny, coding expert."""

MODELS = [
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "dots-studio/dots-3-note-preview:free"
]

# ================= FLASK DASHBOARD - DAY 5 =================
flask_app = Flask(__name__)

@flask_app.route("/")
def dash():
    return f"""
    <html><head><title>Abbas AI Day 6</title>
    <style>body{{font-family:Arial;padding:30px;background:#0f172a;color:#fff}} 
    .card{{background:#1e293b;padding:20px;border-radius:12px;margin:15px 0}} 
    a{{color:#38bdf8}} .badge{{background:#22c55e;padding:4px 10px;border-radius:20px;font-size:12px}}</style>
    </head><body>
    <h1>🤖 Abbas Hussain AI - Day 1 to Day 6 Final</h1>
    <div class="card"><span class="badge">LIVE</span> Wispbyte + Vercel<br>
    <b>Repo:</b> {GITHUB_REPO}<br>
    <b>Vercel:</b> <a href="{VERCEL_URL}">{VERCEL_URL}</a><br>
    <b>Time:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}<br>
    <b>Python:</b> {platform.python_version()}<br>
    </div>
    <div class="card">
    <h3>Day 1-6 Journey</h3>
    Day 0: Vie Faucet 💰<br>
    Day 0.5: KingFF Faucet 🚀<br>
    Day 1-2: GitHub + 24/7 Bot Hosting<br>
    Day 3: Shell + AI Models<br>
    Day 4: GitHub PAT<br>
    Day 5: Vercel Live + Wispbyte Transfer<br>
    Day 6: Agent Mode + /kingff<br>
    Day 6.1: Bugfix + Auto Restart<br>
    </div>
    <div class="card">
    <a href="/api/status">/api/status</a> | <a href="/api/files">/api/files</a> | <a href="/api/agent">/api/agent</a> | <a href="https://github.com/{GITHUB_REPO}">GitHub</a>
    </div>
    </body></html>
    """

@flask_app.route("/api/status")
def api_status():
    return jsonify({
        "status": "online",
        "day": "1-6 Final",
        "version": "Day 6.1 Final",
        "hosting": "Wispbyte",
        "vercel": VERCEL_URL,
        "repo": GITHUB_REPO,
        "python": platform.python_version(),
        "pat": bool(GITHUB_PAT),
        "time": datetime.now().isoformat(),
        "commands": ["/start","/id","/battery","/ls","/run","/ai","/deploy","/backup","/setremote","/gitpush","/uptime","/web","/agent","/kingff","/ping","/help"],
        "journey": "Vie Faucet -> KingFF -> Full Stack -> Agent"
    })

@flask_app.route("/api/files")
def api_files():
    try:
        files = os.listdir(".")
        return jsonify({"files": files, "count": len(files), "time": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)})

@flask_app.route("/api/agent")
def api_agent():
    return jsonify({
        "agent": "Abbas Agent",
        "day": 6,
        "mode": "Autonomous",
        "tools": ["shell","read","write","gitpush","deploy","restart"],
        "status": "ready",
        "hosting": "Wispbyte",
        "example_goals": [
            "README me Day 6 section add kar",
            "bot.py me /hello command add kar",
            "ek file test.py bana aur GitHub push kar"
        ]
    })

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

# ================= HELPERS =================
async def call_ai(prompt, system=SYSTEM_PROMPT):
    if not AI_KEY:
        return "❌ AI_KEY missing! Wispbyte > Variables me AI_KEY add kar"
    for model in MODELS:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1500,
                        "temperature": 0.7
                    }
                )
                data = resp.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
        except Exception:
            continue
    return "⚠️ AI models busy - thodi der baad try kar"

def exec_shell(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = (r.stdout + r.stderr).strip() or "No output"
        if GITHUB_PAT:
            out = out.replace(GITHUB_PAT, "***PAT***")
        return out[:3500]
    except Exception as e:
        return f"Error: {e}"

def read_file_content(fname):
    try:
        if not os.path.exists(fname):
            return f"File {fname} not found"
        with open(fname, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
        if len(data) > 3000:
            data = data[:3000] + "\n...truncated"
        return data
    except Exception as e:
        return f"Read error: {e}"

def write_file_content(fname, content):
    try:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Written {fname} ({len(content)} chars)"
    except Exception as e:
        return f"Write error: {e}"

# ================= AGENT LOOP - DAY 6 =================
async def agent_loop(goal, update):
    history = f"USER GOAL: {goal}\n"
    await update.message.reply_text(f"🤖 Abbas Agent Day 1-6 Final Activated!\n🎯 Goal: {goal}\n🧠 Planning...")

    for step in range(1, 9):
        prompt_text = history + f"\nStep {step}/8. Think and if need tool output JSON. If complete say FINAL ANSWER."
        ai_resp = await call_ai(prompt_text, system=AGENT_SYSTEM)
        
        tool_match = re.search(r'\{[^}]*"tool"[^}]*\}', ai_resp, re.DOTALL)
        if tool_match:
            try:
                tool_json = json.loads(tool_match.group(0))
                tool_name = tool_json.get("tool")
                await update.message.reply_text(f"Step {step}: {ai_resp[:1000]}\n\nTool: {tool_name}")

                result = ""
                if tool_name == "shell":
                    result = exec_shell(tool_json.get("cmd", "ls -la"))
                elif tool_name == "read":
                    result = read_file_content(tool_json.get("file", "bot.py"))
                elif tool_name == "write":
                    result = write_file_content(tool_json.get("file", "test.txt"), tool_json.get("content", ""))
                elif tool_name == "gitpush":
                    exec_shell(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git')
                    msg = tool_json.get("msg", "Day 6 Final Agent update")
                    cmd = f'git config user.email "agent@abbas.com" && git config user.name "Abbas Agent" && git add . && git commit -m "{msg}" || echo "nothing" && git push origin main'
                    result = exec_shell(cmd)
                elif tool_name == "deploy":
                    result = exec_shell("git pull origin main")
                elif tool_name == "restart":
                    await update.message.reply_text("🔄 Agent restarting Wispbyte to apply changes...")
                    os._exit(0)
                else:
                    result = f"Unknown tool {tool_name}"

                await update.message.reply_text(f"Tool Result:\n{result[:3500]}")
                history += f"\nStep {step} AI: {ai_resp[:500]}\nTool {tool_name} -> {result[:1000]}\n"
                if "FINAL" in ai_resp.upper():
                    break
            except Exception as e:
                await update.message.reply_text(f"Tool error: {e}\nAI said: {ai_resp[:1000]}")
                history += f"\nError: {e}\n"
                continue
        else:
            await update.message.reply_text(f"Step {step} - Thinking:\n{ai_resp[:2500]}")
            history += f"\nStep {step} - {ai_resp[:800]}\n"
            if "FINAL" in ai_resp.upper() or "ho gaya" in ai_resp.lower() or "complete" in ai_resp.lower():
                break

    final_summary = await call_ai(f"Goal: {goal}\nHistory: {history}\nGive final summary Roman Urdu/Hinglish.", system=SYSTEM_PROMPT)
    await update.message.reply_text(f"🎉 Agent Mission Complete!\n\n{final_summary}")

# ================= COMMANDS - DAY 1 to DAY 6 =================
# Day 1-2: /start
async def start(u, c):
    await u.message.reply_text(
        f"🤖 **Abbas Hussain AI - Day 1-6 Final ✅**\n\n"
        f"**Repo:** {GITHUB_REPO}\n"
        f"**PAT:** {'✅' if GITHUB_PAT else '❌'}\n"
        f"**Vercel:** {VERCEL_URL}\n"
        f"**Hosting:** Wispbyte 🌐\n"
        f"**Python:** {platform.python_version()}\n\n"
        f"**Day 3:** /id /battery /ls /run /ai\n"
        f"**Day 4:** /deploy /backup /setremote /gitpush /uptime\n"
        f"**Day 5:** /web\n"
        f"**Day 6:** /agent <goal> + /kingff + /ping + /help 🧠🤖\n\n"
        f"**Examples:**\n"
        f"/agent README me Day 6 section add kar\n"
        f"/agent bot.py me /hello add kar\n"
        f"/kingff - Journey\n\n"
        f"KingFF Faucet to Full Stack Agent! 🚀",
        parse_mode='Markdown'
    )

# Day 3: /id
async def get_id(u, c):
    await u.message.reply_text(f"🔑 ID: `{u.effective_user.id}`", parse_mode='Markdown')

# Day 3: /battery
async def battery(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    await u.message.reply_text(
        f"🖥️ **Day 1-6 Final - Wispbyte**\n"
        f"Python: {platform.python_version()}\n"
        f"Platform: {platform.system()} {platform.release()}\n"
        f"Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
        f"PAT: {'✅' if GITHUB_PAT else '❌'}\n"
        f"Vercel: {VERCEL_URL}\n"
        f"Repo: {GITHUB_REPO}\n"
        f"Mode: Agent Final 🧠\n"
        f"Hosting: Wispbyte ✅\n"
        f"Files: {len(os.listdir('.'))}",
        parse_mode='Markdown'
    )

# Day 3: /ls
async def ls_files(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    files = os.listdir(".")
    text = "📁 Files:\n" + "\n".join([f"- {f}" for f in files[:50]])
    await u.message.reply_text(text)

# Day 3: /run
async def run_cmd(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    cmd = " ".join(c.args)
    if not cmd:
        return await u.message.reply_text("Usage: /run ls -la")
    result = exec_shell(cmd)
    await u.message.reply_text(f"$ {cmd}\n{result[:3500]}")

# Day 3: /ai
async def ai_command(u, c):
    q = " ".join(c.args)
    if not q:
        return await u.message.reply_text("Usage: /ai apna sawal likho")
    await u.message.reply_chat_action("typing")
    ans = await call_ai(q)
    await u.message.reply_text(ans)

# Day 4: /deploy
async def deploy(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    await u.message.reply_text("🔄 Pulling from GitHub...")
    result = exec_shell("git pull origin main")
    await u.message.reply_text(result[:3500])

# Day 4: /backup
async def backup(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    await u.message.reply_text("📦 Backup bana raha hun...")
    try:
        with zipfile.ZipFile("backup.zip", "w") as z:
            for fname in ["bot.py", "requirements.txt", "README.md", "Dockerfile", "fly.toml"]:
                if os.path.exists(fname):
                    z.write(fname)
        await u.message.reply_document(open("backup.zip", "rb"), caption="📦 Day 1-6 Final Backup - Wispbyte!")
    except Exception as e:
        await u.message.reply_text(f"Backup error: {e}")

# Day 4: /setremote
async def setremote(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    if not GITHUB_PAT:
        return await u.message.reply_text("❌ GITHUB_PAT not set! Wispbyte > Variables me add kar")
    exec_shell(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git')
    await u.message.reply_text(f"✅ Remote set for {GITHUB_REPO}")

# Day 4: /gitpush
async def gitpush(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    if not GITHUB_PAT:
        return await u.message.reply_text("❌ GITHUB_PAT not set!")
    msg = " ".join(c.args) or "Day 1-6 Final update"
    await u.message.reply_text(f"📤 Pushing: {msg}")
    cmd1 = f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git'
    cmd2 = f'git config user.email "abbas@bot.com" && git config user.name "Abbas AI" && git add . && git commit -m "{msg}" || echo "nothing" && git push origin main'
    exec_shell(cmd1)
    result = exec_shell(cmd2)
    await u.message.reply_text(result[:3500])

# Day 4: /uptime
async def uptime(u, c):
    await u.message.reply_text(f"⏰ Day 1-6 Final - {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {VERCEL_URL} 🌐 - Wispbyte ✅")

# Day 5: /web
async def web_command(u, c):
    await u.message.reply_text(
        f"🌐 **Day 5-6 Vercel + Wispbyte Live!**\n\n"
        f"🔥 Vercel: {VERCEL_URL}\n"
        f"📊 Status: {VERCEL_URL}/api/status\n"
        f"📁 Files: {VERCEL_URL}/api/files\n"
        f"🤖 Agent: {VERCEL_URL}/api/agent\n"
        f"Local: :{PORT}\n"
        f"Hosting: Wispbyte\n"
        f"GitHub: https://github.com/{GITHUB_REPO}",
        parse_mode='Markdown'
    )

# Day 6: /agent
async def agent_command(u, c):
    if u.effective_user.id != OWNER_ID:
        return await u.message.reply_text("❌ Sirf owner agent chala sakta hai! OWNER_ID check kar")
    goal = " ".join(c.args)
    if not goal:
        return await u.message.reply_text(
            "Usage: /agent <goal>\n\n"
            "Examples:\n"
            "/agent README me Day 6 section add kar\n"
            "/agent bot.py me /hello command add kar\n"
            "/agent ek file test.py bana jo hello world print kare\n"
            "/agent Vercel status check kar"
        )
    await agent_loop(goal, u)

# Day 6: /kingff
async def kingff_command(u, c):
    await u.message.reply_text(
        "👑 **KingFF Faucet -> Agent Journey - By Abbas Hussain (16yo)**\n\n"
        "Day 0: Vie Faucet 💰 - Pehla faucet idea\n"
        "Day 0.5: KingFF Faucet 🚀 - Tera apna startup! Users, faucet claim, referral system\n"
        "Day 1: GitHub + 24/7 Bot Hosting - Code ko online laya\n"
        "Day 2: Telegram Bot LIVE - /start working, Full Stack ki shuruaat\n"
        "Day 3: Shell + 3 AI Models + /id /battery /ls /run /ai 🧠\n"
        "Day 4: GitHub PAT - /deploy /backup /setremote /gitpush /uptime 🔑\n"
        "Day 5: Vercel Live Dashboard + Wispbyte Transfer 🌐\n"
        "  https://abbas-ai-dashboard.vercel.app\n"
        "  bot-hosting.net (7 days free) -> Wispbyte (long term)\n"
        "Day 6: OpenClaw Agent - /agent <goal> 🤖 - Khud sochta, plan karta, action leta!\n"
        "Day 6.1: Bugfix Markdown Parse + Auto Restart + /kingff ✅\n\n"
        "16 saal ki umar me, Islamabad se, Vie se KingFF, Bot se Agent!\n"
        "Wispbyte + Vercel + GitHub + AI = Full Stack Engineer! 💪\n\n"
        "Next: Day 7 - Voice Agent + Multi-Agent + Dashboard Pro!",
        parse_mode='Markdown'
    )

# Day 6: /ping
async def ping_command(u, c):
    await u.message.reply_text(f"🏓 Pong! Day 1-6 Final Wispbyte LIVE ✅\n{datetime.now().strftime('%H:%M:%S')} - {VERCEL_URL}")

# Day 6: /help
async def help_command(u, c):
    await u.message.reply_text(
        "📚 **Abbas AI - Day 1-6 Final Commands**\n\n"
        "**Day 3:**\n"
        "/id - Tera Telegram ID\n"
        "/battery - System info (owner only)\n"
        "/ls - Files list (owner)\n"
        "/run <cmd> - Shell command (owner)\n"
        "/ai <sawal> - AI se baat\n\n"
        "**Day 4:**\n"
        "/deploy - GitHub se pull\n"
        "/backup - Backup zip\n"
        "/setremote - PAT se remote set\n"
        "/gitpush <msg> - GitHub push\n"
        "/uptime - Time + Vercel\n\n"
        "**Day 5:**\n"
        "/web - Vercel dashboard\n\n"
        "**Day 6:**\n"
        "/agent <goal> - Autonomous Agent 🤖\n"
        "/kingff - KingFF Journey 👑\n"
        "/ping - Check live\n"
        "/help - Ye list\n\n"
        "Wispbyte + Vercel Live!",
        parse_mode='Markdown'
    )

# Normal chat
async def handle_message(u, c):
    await u.message.reply_chat_action("typing")
    ans = await call_ai(u.message.text)
    await u.message.reply_text(ans)

# ================= MAIN =================
def main():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except:
        pass
    threading.Thread(target=run_flask, daemon=True).start()

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing! Set in Wispbyte > Variables")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    commands = [
        ("start", start),
        ("id", get_id),
        ("battery", battery),
        ("ls", ls_files),
        ("run", run_cmd),
        ("ai", ai_command),
        ("deploy", deploy),
        ("backup", backup),
        ("setremote", setremote),
        ("gitpush", gitpush),
        ("uptime", uptime),
        ("web", web_command),
        ("agent", agent_command),
        ("kingff", kingff_command),
        ("ping", ping_command),
        ("help", help_command),
    ]

    for cmd_name, func in commands:
        app.add_handler(CommandHandler(cmd_name, func))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"✅ Abbas AI ONLINE - Day 1 to Day 6 Final - Python {platform.python_version()}")
    print(f"🌐 Flask on :{PORT} | Vercel: {VERCEL_URL} | Wispbyte Live")
    print(f"👑 KingFF Faucet -> Agent - Ready!")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
