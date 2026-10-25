import os
from dotenv import load_dotenv
load_dotenv()
import subprocess, platform, asyncio, httpx, zipfile, threading, json, re
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN=os.getenv("BOT_TOKEN")
AI_KEY=os.getenv("AI_KEY")
GITHUB_PAT=os.getenv("GITHUB_PAT","")
GITHUB_REPO=os.getenv("GITHUB_REPO","AbbasFullstack/kingff-bot")
VERCEL_URL=os.getenv("VERCEL_URL","https://abbas-ai-dashboard.vercel.app")
OWNER_ID=int(os.getenv("OWNER_ID","8752799745"))

AGENT_SYSTEM = """You are Abbas Agent - Autonomous AI Agent by Abbas Hussain (16yo, Islamabad).
Journey: Vie Faucet -> KingFF Faucet -> Full Stack -> Now Agent!

You are NOT just a chatbot. You are an AGENT who can THINK, PLAN, and ACT using TOOLS.

Available TOOLS (output JSON when you need to use a tool):
1. {"tool":"shell","cmd":"ls -la"} - Run shell command
2. {"tool":"read","file":"bot.py"} - Read file content (first 2000 chars)
3. {"tool":"write","file":"test.txt","content":"hello"} - Write/create file
4. {"tool":"gitpush","msg":"Day 6 Agent update"} - Push to GitHub
5. {"tool":"deploy"} - Pull from GitHub

RULES:
- When user gives a GOAL, break it into 3-5 steps, then execute step by step using tools.
- Always output your THINKING first, then TOOL JSON if needed.
- After tool result, continue planning.
- Keep responses in Roman Urdu/Hinglish: bro, yaar, zabardast.
- You are running on Wispbyte + Vercel Live.
"""

SYSTEM_PROMPT = """You are Abbas Hussain AI - Personal AI by Abbas Hussain, 16yo Full Stack Engineer from Islamabad. Journey: KingFF Faucet -> Full Stack. Speak Roman Urdu/Hinglish. Day 6 Agent Mode. Running on Wispbyte."""

MODELS = ["recursive/flint-v1.0:free","nvidia/nemotron-3.5-super-vl:free","dots-studio/dots-3-note-preview:free"]

flask_app = Flask(__name__)
@flask_app.route("/")
def dash(): return f"<h1>Abbas Agent Day 6</h1><p>Wispbyte Live</p><p>Vercel: {VERCEL_URL}</p><a href='/api/status'>Status</a> | <a href='/api/agent'>Agent API</a>"
@flask_app.route("/api/status")
def api(): return jsonify({"status":"online","day":6,"mode":"Agent","hosting":"Wispbyte","vercel":VERCEL_URL,"repo":GITHUB_REPO,"time":datetime.now().isoformat()})
@flask_app.route("/api/files")
def apif(): return jsonify({"files": os.listdir("."), "count": len(os.listdir("."))})
@flask_app.route("/api/agent")
def api_agent(): return jsonify({"agent":"Abbas Agent","day":6,"tools":["shell","read","write","gitpush","deploy"],"status":"ready","mission":"From Bot to Agent"})
def run_flask():
    port=int(os.getenv("PORT","8080"))
    flask_app.run(host="0.0.0.0",port=port,debug=False,use_reloader=False)

async def call_ai(prompt, system=SYSTEM_PROMPT):
    if not AI_KEY: return "AI_KEY missing"
    for m in MODELS:
        try:
            async with httpx.AsyncClient(timeout=60) as c:
                r=await c.post("https://openrouter.ai/api/v1/chat/completions",headers={"Authorization": f"Bearer {AI_KEY}","Content-Type":"application/json"},json={"model":m,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"max_tokens":1500,"temperature":0.7})
                d=r.json()
                if "choices" in d: return d["choices"][0]["message"]["content"]
        except: continue
    return "Models busy"

def exec_shell(cmd):
    try:
        if GITHUB_PAT and GITHUB_PAT in cmd: cmd_display=cmd.replace(GITHUB_PAT,"***PAT***")
        else: cmd_display=cmd
        r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=30)
        out=(r.stdout+r.stderr).strip() or "No output"
        if GITHUB_PAT: out=out.replace(GITHUB_PAT,"***PAT***")
        return f"$ {cmd_display}\n{out[:3000]}"
    except Exception as e: return f"Error: {e}"

def read_file_content(fname):
    try:
        if not os.path.exists(fname): return f"File {fname} not found"
        with open(fname,'r',encoding='utf-8',errors='ignore') as f: data=f.read()
        if len(data)>2000: data=data[:2000]+"\n...truncated"
        return data
    except Exception as e: return f"Read error: {e}"

def write_file_content(fname, content):
    try:
        with open(fname,'w',encoding='utf-8') as f: f.write(content)
        return f"✅ Written {fname} ({len(content)} chars)"
    except Exception as e: return f"Write error: {e}"

async def agent_loop(goal, update):
    """Day 6 Agent Loop - Think -> Act -> Observe"""
    history = f"USER GOAL: {goal}\n\n"
    await update.message.reply_text(f"🤖 **Abbas Agent Day 6 Activated!**\n\n🎯 Goal: {goal}\n\n🧠 Planning...")

    for step in range(1, 8):  # Max 7 steps
        prompt = f"{history}\nYou are on step {step}/7. Think what to do next. If you need a tool, output JSON exactly like {{\"tool\":\"shell\",\"cmd\":\"ls -la\"}} or {{\"tool\":\"read\",\"file\":\"bot.py\"}} etc. If goal is complete, say FINAL ANSWER."
        
        ai_resp = await call_ai(prompt, system=AGENT_SYSTEM)
        
        # Check for tool JSON
        tool_match = re.search(r'\{[^}]*"tool"[^}]*\}', ai_resp, re.DOTALL)
        if tool_match:
            try:
                tool_json = json.loads(tool_match.group(0))
                tool_name = tool_json.get("tool")
                await update.message.reply_text(f"**Step {step}:** {ai_resp[:800]}\n\n🔧 **Tool:** `{tool_name}`", parse_mode='Markdown')
                
                result = ""
                if tool_name == "shell":
                    result = exec_shell(tool_json.get("cmd","ls"))
                elif tool_name == "read":
                    result = read_file_content(tool_json.get("file","bot.py"))
                elif tool_name == "write":
                    result = write_file_content(tool_json.get("file","test.txt"), tool_json.get("content",""))
                elif tool_name == "gitpush":
                    exec_shell(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git')
                    result = exec_shell(f'git config user.email "agent@abbas.com" && git config user.name "Abbas Agent" && git add . && git commit -m "{tool_json.get("msg","Day 6 Agent")}" || echo "nothing" && git push origin main')
                elif tool_name == "deploy":
                    result = exec_shell("git pull origin main")
                else:
                    result = f"Unknown tool {tool_name}"
                
                await update.message.reply_text(f"📟 **Tool Result:**\n```\n{result[:3000]}\n```", parse_mode='Markdown')
                history += f"\nStep {step} - AI: {ai_resp[:500]}\nTool: {tool_name} -> Result: {result[:1000]}\n"
                
                # Check if final
                if "FINAL" in ai_resp.upper() or step == 7:
                    break
            except Exception as e:
                await update.message.reply_text(f"⚠️ Tool parse error: {e}\nAI said: {ai_resp[:1000]}")
                history += f"\nTool error: {e}\n"
                continue
        else:
            # No tool, just thinking/final
            await update.message.reply_text(f"**Step {step} - Thinking:**\n{ai_resp[:3000]}", parse_mode='Markdown')
            history += f"\nStep {step} - {ai_resp[:1000]}\n"
            if "FINAL" in ai_resp.upper() or "ho gaya" in ai_resp.lower() or "complete" in ai_resp.lower():
                break

    final_summary = await call_ai(f"Goal: {goal}\nHistory: {history}\n\nGive final summary in Roman Urdu/Hinglish - what was done, what is result.", system=SYSTEM_PROMPT)
    await update.message.reply_text(f"🎉 **Agent Mission Complete!**\n\n{final_summary}", parse_mode='Markdown')

# Commands
async def start(u,c):
    await u.message.reply_text(f"🤖 **Day 6 Wispbyte Agent Live ✅**\nRepo: {GITHUB_REPO}\nPAT: {'✅' if GITHUB_PAT else '❌'}\nVercel: {VERCEL_URL}\nHosting: Wispbyte 🌐\n\n**Day 3:** /id /battery /ls /run /ai\n**Day 4:** /deploy /backup /setremote /gitpush /uptime\n**Day 5:** /web\n**Day 6 NEW:** /agent <goal> 🧠🤖\n\n**Example:**\n/agent mere README me Day 6 Agent section add kar\n/agent bot.py me ek naya /hello command add kar\n\nKingFF Faucet to Agent! 🚀",parse_mode='Markdown')
async def get_id(u,c): await u.message.reply_text(f"🔑 ID: `{u.effective_user.id}`",parse_mode='Markdown')
async def battery(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text(f"🖥️ **Day 6 Agent - Wispbyte**\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\nPAT: {'✅' if GITHUB_PAT else '❌'}\nVercel: {VERCEL_URL}\nMode: Agent 🧠\nHosting: Wispbyte ✅",parse_mode='Markdown')
async def ls_files(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text("📁 Files:\n" + "\n".join([f"- {f}" for f in os.listdir(".")]))
async def run_cmd(u,c):
    if u.effective_user.id!=OWNER_ID: return
    cmd=" ".join(c.args)
    if not cmd: return await u.message.reply_text("Usage: /run ls -la")
    r=exec_shell(cmd)
    await u.message.reply_text(f"```\n{r[:3500]}\n```",parse_mode='Markdown')
async def ai_command(u,c):
    q=" ".join(c.args)
    if not q: return
    await u.message.reply_chat_action("typing")
    await u.message.reply_text(await call_ai(q))
async def deploy(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text("🔄 Pulling...")
    await u.message.reply_text(f"```\n{exec_shell('git pull origin main')[:3500]}\n```",parse_mode='Markdown')
async def backup(u,c):
    if u.effective_user.id!=OWNER_ID: return
    await u.message.reply_text("📦 Backup...")
    with zipfile.ZipFile("backup.zip","w") as z:
        for f in ["bot.py","requirements.txt","README.md"]:
            if os.path.exists(f): z.write(f)
    await u.message.reply_document(open("backup.zip","rb"),caption="📦 Day 6 Agent Backup!")
async def setremote(u,c):
    if u.effective_user.id!=OWNER_ID: return
    if not GITHUB_PAT: return await u.message.reply_text("❌ GITHUB_PAT not set!")
    exec_shell(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git')
    await u.message.reply_text(f"✅ Remote set for {GITHUB_REPO}")
async def gitpush(u,c):
    if u.effective_user.id!=OWNER_ID: return
    if not GITHUB_PAT: return await u.message.reply_text("❌ GITHUB_PAT not set!")
    msg=" ".join(c.args) or "Day 6 Agent update"
    await u.message.reply_text(f"📤 Pushing: {msg}")
    cmd_str = f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git && git config user.email "agent@abbas.com" && git config user.name "Abbas Agent" && git add . && git commit -m "{msg}" || echo "nothing" && git push origin main'
    res = exec_shell(cmd_str)
    await u.message.reply_text(f"```\n{res[:3500]}\n```",parse_mode='Markdown')
async def uptime(u,c): await u.message.reply_text(f"⏰ Day 6 Agent - {datetime.now()} - {VERCEL_URL} 🌐 - Wispbyte")
async def web_command(u,c): await u.message.reply_text(f"🌐 **Day 6 Agent + Vercel Live!**\nVercel: {VERCEL_URL}\nHosting: Wispbyte\nAgent API: {VERCEL_URL}/api/agent\n\nGitHub: https://github.com/{GITHUB_REPO}",parse_mode='Markdown')
async def agent_command(u,c):
    if u.effective_user.id!=OWNER_ID: return await u.message.reply_text("❌ Sirf owner agent chala sakta hai!")
    goal=" ".join(c.args)
    if not goal: return await u.message.reply_text("Usage: /agent <goal>\n\nExamples:\n/agent README me Day 6 section add kar\n/agent bot.py me /hello command add kar\n/agent Vercel dashboard ka status check kar\n/agent ek naya file test.py bana jo hello world print kare")
    await agent_loop(goal, u)

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
    for cmd,fn in [("start",start),("id",get_id),("battery",battery),("ls",ls_files),("run",run_cmd),("ai",ai_command),("deploy",deploy),("backup",backup),("setremote",setremote),("gitpush",gitpush),("uptime",uptime),("web",web_command),("agent",agent_command)]:
        app.add_handler(CommandHandler(cmd,fn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_message))
    print(f"Abbas Agent ONLINE ✅ Day 6 Wispbyte - Python {platform.python_version()}")
    app.run_polling(allowed_updates=Update.ALL_TYPES,drop_pending_updates=True)

if __name__=="__main__": main()
                                                                        
