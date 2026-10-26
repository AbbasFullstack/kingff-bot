import os
from dotenv import load_dotenv
load_dotenv()
import subprocess, platform, asyncio, httpx, zipfile, threading, json, re
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Try voice libs - if not installed, fallback
try:
    from gtts import gTTS
    HAS_TTS = True
except:
    HAS_TTS = False

# ENV
print("🔧 Abbas AI Day 7.2 Voice Agent Loading...")
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "") or AI_KEY  # Try AI_KEY as OpenAI key too
GITHUB_PAT = os.getenv("GITHUB_PAT", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
VERCEL_URL = os.getenv("VERCEL_URL", "https://abbas-ai-dashboard.vercel.app")
OWNER_ID = int(os.getenv("OWNER_ID", "8752799745"))
PORT = int(os.getenv("PORT", "8080"))

print(f"BOT_TOKEN: {bool(BOT_TOKEN)} | AI_KEY: {bool(AI_KEY)} | PAT: {bool(GITHUB_PAT)} | TTS: {HAS_TTS}")

AGENT_SYSTEM = """You are Abbas Agent - Autonomous AI Agent by Abbas Hussain (16yo, Islamabad).
Journey: Vie Faucet -> KingFF Faucet -> Full Stack -> Voice Agent!
You THINK, PLAN, ACT using TOOLS.
Tools:
1. shell - {"tool":"shell","cmd":"ls -la"}
2. read - {"tool":"read","file":"bot.py"}
3. write - {"tool":"write","file":"test.txt","content":"hello"}
4. gitpush - {"tool":"gitpush","msg":"update"}
5. deploy - {"tool":"deploy"}
6. restart - {"tool":"restart"}
RULES: Break goal into steps, use tools, speak Roman Urdu/Hinglish, Wispbyte."""

SYSTEM_PROMPT = """You are Abbas Hussain AI - Personal AI by Abbas Hussain, 16yo Full Stack Engineer, Islamabad.
Journey: Vie Faucet -> KingFF Faucet -> Full Stack -> Voice Agent Day 7.
Speak Roman Urdu/Hinglish - bro, yaar, zabardast. Wispbyte + Vercel Live. Helpful, funny, coding expert."""

MODELS = ["recursive/flint-v1.0:free","nvidia/nemotron-3.5-super-vl:free","dots-studio/dots-3-note-preview:free"]

# FLASK - DAY 5 + DAY 7
flask_app = Flask(__name__)

@flask_app.route("/")
def dash():
    return f"""
    <html><head><title>Abbas AI Day 7 Voice</title>
    <style>body{{font-family:Arial;padding:30px;background:#0f172a;color:#fff}} 
    .card{{background:#1e293b;padding:20px;border-radius:12px;margin:15px 0}} 
    a{{color:#38bdf8}} .badge{{background:#22c55e;padding:4px 10px;border-radius:20px;font-size:12px}} .voice{{background:#7c3aed}}</style>
    </head><body>
    <h1>🎤 Abbas AI Day 7.2 Voice Agent</h1>
    <div class="card"><span class="badge">LIVE</span> <span class="badge voice">VOICE AGENT</span> Wispbyte + Vercel<br>
    <b>Repo:</b> {GITHUB_REPO}<br><b>Vercel:</b> <a href="{VERCEL_URL}">{VERCEL_URL}</a><br>
    <b>Time:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}<br><b>Python:</b> {platform.python_version()}<br><b>TTS:</b> {HAS_TTS}</div>
    <div class="card"><h3>Day 1-7 Journey</h3>
    Day 0: Vie Faucet<br>Day 0.5: KingFF Faucet<br>Day 1-2: GitHub + Bot<br>Day 3: Shell + AI<br>Day 4: GitHub PAT<br>Day 5: Vercel + Wispbyte<br>Day 6: Agent Mode + /kingff<br>Day 7: Voice Agent + /voice + Voice Messages 🎤</div>
    <div class="card"><a href="/api/status">/api/status</a> | <a href="/api/files">/api/files</a> | <a href="/api/agent">/api/agent</a> | <a href="/api/voice">/api/voice</a> | <a href="https://github.com/{GITHUB_REPO}">GitHub</a></div>
    </body></html>
    """

@flask_app.route("/api/status")
def api_status():
    return jsonify({"status":"online","day":"1-7 Voice","version":"Day 7.2 Voice Agent","hosting":"Wispbyte","vercel":VERCEL_URL,"repo":GITHUB_REPO,"python":platform.python_version(),"pat":bool(GITHUB_PAT),"tts":HAS_TTS,"time":datetime.now().isoformat(),"commands":["/start","/id","/battery","/ls","/run","/ai","/deploy","/backup","/setremote","/gitpush","/uptime","/web","/agent","/kingff","/ping","/help","/voice"],"journey":"Vie Faucet -> KingFF -> Full Stack -> Agent -> Voice Agent","voice":True})

@flask_app.route("/api/files")
def api_files():
    return jsonify({"files": os.listdir("."), "count": len(os.listdir("."))})

@flask_app.route("/api/agent")
def api_agent():
    return jsonify({"agent":"Abbas Agent Day 7 Voice","day":7,"tools":["shell","read","write","gitpush","deploy","restart"],"voice":True})

@flask_app.route("/api/voice")
def api_voice():
    return jsonify({"voice_agent":"Active","day":7,"features":["Voice Message Transcription","Text-to-Speech Reply","/voice command","Agent via Voice","TTS"],"tts":HAS_TTS,"how_to_use":"Send voice message in Telegram bot, it will transcribe and act as agent"})

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

# HELPERS
async def call_ai(prompt, system=SYSTEM_PROMPT):
    if not AI_KEY:
        return "AI_KEY missing! Wispbyte > Variables me AI_KEY add kar"
    for model in MODELS:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post("https://openrouter.ai/api/v1/chat/completions",headers={"Authorization": f"Bearer {AI_KEY}","Content-Type":"application/json"},json={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"max_tokens":1500,"temperature":0.7})
                data = resp.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
        except:
            continue
    return "Models busy - thodi der baad try kar"

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
        with open(fname,'r',encoding='utf-8',errors='ignore') as f:
            data = f.read()
        if len(data) > 3000:
            data = data[:3000] + "...truncated"
        return data
    except Exception as e:
        return f"Read error: {e}"

def write_file_content(fname, content):
    try:
        with open(fname,'w',encoding='utf-8') as f:
            f.write(content)
        return f"Written {fname} ({len(content)} chars)"
    except Exception as e:
        return f"Write error: {e}"

# VOICE - TTS
def text_to_voice(text, filename="voice_reply.mp3"):
    try:
        if not HAS_TTS:
            return None
        # Clean text for TTS - remove markdown, limit length
        clean = re.sub(r'\*\*|__|`|\[.*?\]\(.*?\)', '', text)
        clean = clean[:500]  # Limit for voice
        tts = gTTS(text=clean, lang='en', slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"TTS error: {e}")
        return None

# VOICE - STT (Transcription via OpenAI Whisper)
async def transcribe_voice(file_path):
    # Try OpenRouter Whisper or OpenAI Whisper
    try:
        # Try OpenRouter audio transcription
        async with httpx.AsyncClient(timeout=60) as client:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'audio/ogg')}
                data = {'model': 'openai/whisper-large-v3'}
                headers = {"Authorization": f"Bearer {AI_KEY}"}
                # Try OpenRouter
                resp = await client.post("https://openrouter.ai/api/v1/audio/transcriptions", headers=headers, files=files, data=data)
                if resp.status_code == 200:
                    j = resp.json()
                    return j.get("text", "") or j.get("transcription", "")
                # Try OpenAI direct if OPENAI_KEY different
                if OPENAI_KEY and OPENAI_KEY != AI_KEY:
                    headers2 = {"Authorization": f"Bearer {OPENAI_KEY}"}
                    resp2 = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers2, files=files, data={"model":"whisper-1"})
                    if resp2.status_code == 200:
                        return resp2.json().get("text","")
    except Exception as e:
        print(f"Transcription error: {e}")
    return ""

# AGENT LOOP
async def agent_loop(goal, update):
    history = f"USER GOAL: {goal}\n"
    await update.message.reply_text(f"🤖 Abbas Agent Day 7 Voice Final Activated!\n🎯 Goal: {goal}\n🧠 Planning...")

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
                    msg = tool_json.get("msg", "Day 7 Voice update")
                    cmd = f'git config user.email "agent@abbas.com" && git config user.name "Abbas Agent" && git add . && git commit -m "{msg}" || echo "nothing" && git push origin main'
                    result = exec_shell(cmd)
                elif tool_name == "deploy":
                    result = exec_shell("git pull origin main")
                elif tool_name == "restart":
                    await update.message.reply_text("🔄 Agent restarting Wispbyte...")
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
            if "FINAL" in ai_resp.upper() or "ho gaya" in ai_resp.lower():
                break
    final_summary = await call_ai(f"Goal: {goal}\nHistory: {history}\nGive final summary Roman Urdu/Hinglish.", system=SYSTEM_PROMPT)
    await update.message.reply_text(f"🎉 Agent Mission Complete!\n\n{final_summary}")
    # Voice reply too
    if HAS_TTS:
        vf = text_to_voice(final_summary)
        if vf and os.path.exists(vf):
            try:
                await update.message.reply_voice(open(vf, 'rb'), caption="🎤 Voice Reply")
            except:
                pass

# COMMANDS
async def start(u, c):
    await u.message.reply_text(
        f"🤖 **Abbas AI - Day 7.2 Voice Agent FINAL FIXED ✅**\n\n"
        f"**Repo:** {GITHUB_REPO}\n**PAT:** {'✅' if GITHUB_PAT else '❌'}\n**Vercel:** {VERCEL_URL}\n"
        f"**Hosting:** Wispbyte 🌐\n**Python:** {platform.python_version()}\n**TTS:** {'✅' if HAS_TTS else '❌'}\n\n"
        f"**Day 3:** /id /battery /ls /run /ai\n**Day 4:** /deploy /backup /setremote /gitpush /uptime\n"
        f"**Day 5:** /web\n**Day 6:** /agent <goal> + /kingff + /ping + /help\n**Day 7 NEW:** /voice + Voice Messages 🎤🧠\n\n"
        f"**Day 7 Features:**\n🎤 Voice bhej - Agent sunega!\n🔊 Voice me jawab dega!\n🧠 Bol ke /agent goal de sakta hai!\n\n"
        f"**Examples:**\n/voice - Voice agent guide\nVoice msg: 'README me Day 7 add kar'\n/agent + voice combo!\n\nKingFF to Voice Agent! 🚀",
        parse_mode='Markdown'
    )

async def get_id(u, c):
    await u.message.reply_text(f"🔑 ID: `{u.effective_user.id}`", parse_mode='Markdown')

async def battery(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    await u.message.reply_text(f"🖥️ **Day 7.2 Voice Agent - Wispbyte**\nPython: {platform.python_version()}\nTime: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\nPAT: {'✅' if GITHUB_PAT else '❌'}\nVercel: {VERCEL_URL}\nRepo: {GITHUB_REPO}\nMode: Voice Agent 🎤\nTTS: {'✅' if HAS_TTS else '❌'}\nFiles: {len(os.listdir('.'))}", parse_mode='Markdown')

async def ls_files(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    files = os.listdir(".")
    await u.message.reply_text("📁 Files:\n" + "\n".join([f"- {f}" for f in files[:50]]))

async def run_cmd(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    cmd = " ".join(c.args)
    if not cmd:
        return await u.message.reply_text("Usage: /run ls -la")
    await u.message.reply_text(f"$ {cmd}\n{exec_shell(cmd)[:3500]}")

async def ai_command(u, c):
    q = " ".join(c.args)
    if not q:
        return await u.message.reply_text("Usage: /ai apna sawal likho")
    await u.message.reply_chat_action("typing")
    ans = await call_ai(q)
    await u.message.reply_text(ans)
    if HAS_TTS:
        vf = text_to_voice(ans)
        if vf and os.path.exists(vf):
            try:
                await u.message.reply_voice(open(vf, 'rb'))
            except:
                pass

async def deploy(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    await u.message.reply_text("🔄 Pulling...")
    await u.message.reply_text(exec_shell("git pull origin main")[:3500])

async def backup(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    await u.message.reply_text("📦 Backup...")
    try:
        with zipfile.ZipFile("backup.zip","w") as z:
            for fname in ["bot.py","requirements.txt","README.md"]:
                if os.path.exists(fname):
                    z.write(fname)
        await u.message.reply_document(open("backup.zip","rb"), caption="📦 Day 7 Voice Backup!")
    except Exception as e:
        await u.message.reply_text(f"Backup error: {e}")

async def setremote(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    if not GITHUB_PAT:
        return await u.message.reply_text("❌ GITHUB_PAT not set!")
    exec_shell(f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git')
    await u.message.reply_text(f"✅ Remote set for {GITHUB_REPO}")

async def gitpush(u, c):
    if u.effective_user.id != OWNER_ID:
        return
    if not GITHUB_PAT:
        return await u.message.reply_text("❌ GITHUB_PAT not set!")
    msg = " ".join(c.args) or "Day 7 Voice update"
    await u.message.reply_text(f"📤 Pushing: {msg}")
    cmd1 = f'git remote set-url origin https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git'
    cmd2 = f'git config user.email "agent@abbas.com" && git config user.name "Abbas Agent" && git add . && git commit -m "{msg}" || echo "nothing" && git push origin main'
    exec_shell(cmd1)
    await u.message.reply_text(exec_shell(cmd2)[:3500])

async def uptime(u, c):
    await u.message.reply_text(f"⏰ Day 7.2 Voice Agent - {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} - {VERCEL_URL} 🌐 - Wispbyte ✅🎤")

async def web_command(u, c):
    await u.message.reply_text(f"🌐 **Day 7 Voice + Vercel Live!**\nVercel: {VERCEL_URL}\nStatus: {VERCEL_URL}/api/status\nVoice API: {VERCEL_URL}/api/voice\nLocal: :{PORT}\nHosting: Wispbyte\nGitHub: https://github.com/{GITHUB_REPO}", parse_mode='Markdown')

async def agent_command(u, c):
    if u.effective_user.id != OWNER_ID:
        return await u.message.reply_text("❌ Sirf owner!")
    goal = " ".join(c.args)
    if not goal:
        return await u.message.reply_text("Usage: /agent <goal>\n/agent README me Day 7 add kar")
    await agent_loop(goal, u)

async def kingff_command(u, c):
    await u.message.reply_text(
        "👑 **KingFF -> Voice Agent Journey - By Abbas Hussain (16yo)**\n\n"
        "Day 0: Vie Faucet 💰\nDay 0.5: KingFF Faucet 🚀\nDay 1: GitHub + 24/7 Hosting\nDay 2: Telegram Bot LIVE\n"
        "Day 3: Shell + 3 AI Models + /id /battery /ls /run /ai 🧠\nDay 4: GitHub PAT - /deploy /backup /setremote /gitpush /uptime 🔑\n"
        "Day 5: Vercel Live Dashboard + Wispbyte Transfer 🌐\nDay 6: OpenClaw Agent - /agent <goal> 🤖\n"
        "Day 6.1: Bugfix Markdown + Auto Restart + /kingff ✅\nDay 7: Voice Agent - /voice + Voice Messages 🎤 - Bol ke command de, Agent sunega, voice me jawab dega!\n\n"
        "16 saal, Islamabad se, Vie se KingFF, Bot se Agent se Voice Agent! Wispbyte + Vercel + GitHub + AI + Voice = Full Stack Engineer! 💪",
        parse_mode='Markdown'
    )

async def ping_command(u, c):
    await u.message.reply_text(f"🏓 Pong! Day 7 Voice Wispbyte LIVE ✅\n{datetime.now().strftime('%H:%M:%S')} - {VERCEL_URL} 🎤")

async def help_command(u, c):
    await u.message.reply_text(
        "📚 **Abbas AI - Day 1-7 Voice Final Commands**\n\n"
        "Day 3:\n/id - ID\n/battery - System info\n/ls - Files\n/run <cmd> - Shell\n/ai <sawal> - AI\n\n"
        "Day 4:\n/deploy - Pull\n/backup - Zip\n/setremote - PAT set\n/gitpush <msg> - Push\n/uptime - Time\n\n"
        "Day 5:\n/web - Vercel\n\nDay 6:\n/agent <goal> - Agent 🤖\n/kingff - Journey 👑\n/ping - Live\n/help - List\n\n"
        "Day 7 NEW:\n/voice - Voice Agent Guide 🎤\n🎤 Voice Message bhejo - Agent sunega!\n🔊 Voice reply bhi dega!\n\nWispbyte + Voice Live!",
        parse_mode='Markdown'
    )

async def voice_command(u, c):
    # Day 7.2 - /voice now also acts as AGENT if goal contains action keywords
    text = " ".join(c.args) if c.args else ""
    if text:
        await u.message.reply_chat_action("typing")
        # Check if it's an agent task
        lower = text.lower()
        agent_keywords = ["bana", "add kar", "create", "file", "readme", "bot.py", "command", "push", "deploy", "edit", "section", "journey", "update", "likh", "write"]
        is_agent_task = any(k in lower for k in agent_keywords)
        
        if is_agent_task:
            await u.message.reply_text(f"🎤 Voice command: {text}\n🤖 Agent mode detected! 🧠 Planning...")
            await agent_loop(text, u)
            return
        else:
            await u.message.reply_text(f"🎤 Voice command: {text}\n🧠 Soch raha hun...")
            ans = await call_ai(text)
            await u.message.reply_text(ans)
            if HAS_TTS:
                vf = text_to_voice(ans)
                if vf and os.path.exists(vf):
                    try:
                        await u.message.reply_voice(open(vf, 'rb'), caption="🎤 Voice Reply - Day 7.2")
                        try:
                            os.remove(vf)
                        except:
                            pass
                    except Exception as e:
                        await u.message.reply_text(f"TTS send error: {e}")
            return

    # No text - show guide
    tts_status = "✅ gTTS installed" if HAS_TTS else "❌ pip install gTTS"
    await u.message.reply_text(
        f"🎤 **Day 7.2 Voice Agent - Guide**\n\n"
        f"**Kaise use kare:**\n"
        f"1. 🎙️ Telegram me Voice Message button dabao aur bolo:\n"
        f"   'README me Day 7 section add kar'\n"
        f"   'Meri journey bata'\n"
        f"   'Battery dikha'\n\n"
        f"2. 🤖 Agent voice ko text me convert karega (Whisper)\n"
        f"3. 🧠 Phir us goal pe Agent mode chalega\n"
        f"4. 🔊 Jawab text + voice dono me dega!\n\n"
        f"**Text se bhi:**\n"
        f"/voice Bhai yaar aik kaam karoo\n"
        f"/voice README me Day 7 add kar\n"
        f"Ye ab text + voice dono dega! FIXED!\n\n"
        f"**Requirements:**\n"
        f"TTS: {tts_status}\n"
        f"STT: OpenRouter Whisper (AI_KEY se)\n\n"
        f"Wispbyte pe Voice Agent LIVE! 🎤🚀",
        parse_mode='Markdown'
    )

# VOICE MESSAGE HANDLER - DAY 7
async def handle_voice(u, c):
    if u.effective_user.id != OWNER_ID:
        await u.message.reply_text("❌ Voice agent sirf owner ke liye! OWNER_ID check kar")
        return

    await u.message.reply_text("🎤 Voice received! Transcribing... ⏳")
    try:
        # Get file
        voice_file = await u.message.voice.get_file() if u.message.voice else await u.message.audio.get_file()
        file_path = f"voice_{u.message.message_id}.ogg"
        await voice_file.download_to_drive(file_path)
        
        # Transcribe
        transcribed = await transcribe_voice(file_path)
        
        # Cleanup file
        try:
            os.remove(file_path)
        except:
            pass

        if not transcribed or len(transcribed.strip()) < 2:
            # Fallback - transcription fail but still reply with AI + voice
            await u.message.reply_text(
                "⚠️ Voice transcribe nahi ho paya (Whisper API need OPENAI_API_KEY).\n\n"
                "Lekin maine voice receive kar li hai! ✅\n"
                "Day 7.2 Fix: Ab /voice <text> bhi kaam karega!\n\n"
                "Try karo:\n"
                "/voice Bhai yaar aik kaam karoo\n"
                "Ya dobara voice bhejo thoda slow aur clear bol ke!\n\n"
                "Demo voice reply bhej raha hun!"
            )
            if HAS_TTS:
                demo_text = "Voice agent Day Seven live hai bro! Aapka voice message receive ho gaya hai! Ab aap text me /voice likh ke bhi baat kar sakte ho! KingFF se Voice Agent tak ka safar!"
                vf = text_to_voice(demo_text)
                if vf and os.path.exists(vf):
                    try:
                        await u.message.reply_voice(open(vf, 'rb'), caption="🎤 Day 7.2 Demo Voice Reply - Fallback")
                        try:
                            os.remove(vf)
                        except:
                            pass
                    except Exception as e:
                        await u.message.reply_text(f"Voice error: {e}")
            return

        await u.message.reply_text(f"🎤 **Transcribed:**\n`{transcribed}`\n\n🧠 Agent soch raha hai...", parse_mode='Markdown')

        # If transcribed text looks like a goal, run agent loop, else normal AI
        lower = transcribed.lower()
        if any(x in lower for x in ["bana", "add kar", "create", "file", "readme", "bot.py", "command", "push", "deploy", "journey", "battery", "kingff"]):
            # Run as agent goal
            await agent_loop(transcribed, u)
        else:
            # Normal chat + voice reply
            await u.message.reply_chat_action("typing")
            ans = await call_ai(transcribed)
            await u.message.reply_text(ans)
            if HAS_TTS:
                vf = text_to_voice(ans)
                if vf and os.path.exists(vf):
                    try:
                        await u.message.reply_voice(open(vf, 'rb'), caption="🎤 Voice Reply")
                    except Exception as e:
                        print(f"Voice send error: {e}")

    except Exception as e:
        await u.message.reply_text(f"❌ Voice handle error: {e}\n\nTry /voice for guide")

async def handle_message(u, c):
    await u.message.reply_chat_action("typing")
    ans = await call_ai(u.message.text)
    await u.message.reply_text(ans)

def main():
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except:
        pass
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing!")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    cmds = [("start",start),("id",get_id),("battery",battery),("ls",ls_files),("run",run_cmd),("ai",ai_command),("deploy",deploy),("backup",backup),("setremote",setremote),("gitpush",gitpush),("uptime",uptime),("web",web_command),("agent",agent_command),("kingff",kingff_command),("ping",ping_command),("help",help_command),("voice",voice_command)]
    for n,f in cmds:
        app.add_handler(CommandHandler(n,f))
    # Voice handler - Day 7
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print(f"✅ Abbas AI ONLINE - Day 7.2 Voice Agent Fixed - Python {platform.python_version()}")
    print(f"🌐 Flask :{PORT} | Vercel {VERCEL_URL} | Wispbyte | TTS {HAS_TTS} | Voice Agent LIVE 🎤")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
