import os, sys, asyncio, subprocess, json, time, traceback, random, re
from datetime import datetime
from flask import Flask
from threading import Thread

# Fix for Python 3.14 no current loop
try:
    asyncio.set_event_loop(asyncio.new_event_loop())
except:
    pass

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

print("🔧 Abbas AI Day 8.1 Designed + Real Human Voice Loading...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
OWNER_ID = int(os.getenv("OWNER_ID", "8752799745"))
VERCEL_URL = os.getenv("VERCEL_URL", "https://abbas-ai-dashboard.vercel.app")

HAS_TTS = False
HAS_EDGE_TTS = False
try:
    import edge_tts
    HAS_EDGE_TTS = True
    HAS_TTS = True
    print(f"✅ Edge-TTS OK - REAL Human Voice Ready!")
except Exception as e:
    print(f"⚠️ Edge-TTS not found: {e}")

try:
    from gtts import gTTS
    if not HAS_EDGE_TTS:
        HAS_TTS = True
    print(f"✅ gTTS OK - Fallback")
except Exception as e:
    print(f"❌ gTTS fail: {e}")

try:
    import pydub
    print("✅ pydub OK")
except:
    pass

print(f"BOT_TOKEN: {bool(BOT_TOKEN)} | AI_KEY: {bool(AI_KEY)} | PAT: {bool(GITHUB_PAT)} | TTS: {HAS_TTS}")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN missing!")
    sys.exit(1)

MODELS = [
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "dots-studio/dots-3-note-preview:free"
]

http_client = httpx.AsyncClient(timeout=60.0)

# === AI CALL ===
async def call_ai(prompt, is_voice=False):
    if not AI_KEY:
        return "❌ AI_KEY missing bro! Env var set kar!"
    
    headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
    
    if is_voice:
        system_prompt = """You are Abbas Hussain AI, 16yo Full Stack AI Engineer from Islamabad. 
Speak like REAL human friend - Roman Urdu + English mix, natural, warm.
For VOICE replies: Talk like face-to-face, use "Arre bro... Dekho", "Yaar samjho", "Matlab..."
No ** stars ** or markdown for voice. Keep under 3000 chars. Make it fun to listen!
You're built by AbbasFullstack."""
    else:
        system_prompt = """You are Abbas Hussain AI, Full Stack AI Engineer, friendly, Roman Urdu + English mix.
You are inside Telegram bot KingFF Bot. Built by AbbasFullstack, 16yo Islamabad.
Helpful, concise. Use markdown when needed.
If user asks list like 30 terms, give clean numbered list: Term = Meaning - Explanation"""

    msgs = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    
    for model in MODELS:
        try:
            data = {"model": model, "messages": msgs, "max_tokens": 2500}
            r = await http_client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            if r.status_code == 200:
                j = r.json()
                if "choices" in j and len(j["choices"]) > 0:
                    content = j["choices"][0]["message"]["content"]
                    if content and len(content.strip()) > 0:
                        return content
        except Exception as e:
            print(f"AI {model} error: {e}")
            continue
    
    return "❌ Yaar AI thoda busy hai, 10 sec baad try kar bro! 🔥"

# === DAY 8.1: REAL DESIGNED UI + SMART PARSER ===
def parse_terms_from_text(text):
    import re as re2
    terms = []
    pattern = r'(?:^|\n|\s)(\d+)\.\s*([^\n,]+?)\s*[–\-—]\s*([^\n]+?)(?=\s*\d+\.\s*|\Z)'
    matches = re2.findall(pattern, text, re2.DOTALL)
    if matches:
        for num, term, desc in matches:
            terms.append((num.strip(), term.strip()[:60], desc.strip()[:150]))
    else:
        parts = re2.split(r'\s*\d+\.\s*', text)
        if len(parts) > 5:
            for i, part in enumerate(parts[1:], start=1):
                if not part.strip():
                    continue
                if '–' in part:
                    term, desc = part.split('–', 1)
                elif ' - ' in part:
                    term, desc = part.split(' - ', 1)
                elif '-' in part:
                    term, desc = part.split('-', 1)
                else:
                    term = part[:30]
                    desc = part[30:120]
                terms.append((str(i), term.strip()[:60], desc.strip()[:150]))
    return terms

def format_designed_response(text, query=""):
    import re as re2
    if not text or len(text.strip()) == 0:
        return "Khali jawab, dobara try karo bro!"
    lower_q = (query.lower() if query else "")
    lower_t = text.lower()
    is_terms = any(k in lower_q or k in lower_t for k in ["30 terms", "full stack terms", "terms batao", "frontend"])
    if is_terms:
        terms = parse_terms_from_text(text)
        if len(terms) >= 5:
            designed = "📚 *30 Full Stack Terms - Abbas AI*\n"
            designed += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for num, term, desc in terms[:30]:
                term_clean = term.strip().rstrip(',').rstrip('.')
                desc_clean = desc.strip().rstrip(',').rstrip('.')
                desc_clean = re2.sub(r',\s*\d+\.$', '', desc_clean)
                designed += f"*{num}. {term_clean}*\n"
                designed += f"   └─ {desc_clean}\n\n"
            designed += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            designed += "💡 *Interview Tip:* Yaad kar lo bro! 🔥\n"
            designed += "🎤 Voice: /voice 30 Terms batao\n"
            designed += "👨‍💻 AbbasFullstack (16yo, Islamabad) 🇵🇰"
            return designed
        else:
            pretty = re2.sub(r'\s*(\d+)\.\s*', r'\n\n*\1. ', text)
            designed = "📚 *30 Full Stack Terms*\n"
            designed += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            designed += pretty
            designed += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━"
            return designed
    if len(text) > 400:
        designed = "💬 *Abbas AI Reply*\n"
        designed += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        designed += text
        designed += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━"
        return designed
    return text

def clean_for_speech(text):
    if not text:
        return "Bro, kaam ho gaya hai, check kar lo!"
    terms = parse_terms_from_text(text)
    if len(terms) >= 5:
        hindi_nums = ["Pehla", "Dusra", "Teesra", "Chautha", "Paanchva", "Chhata", "Saatva", "Aathva", "Nauva", "Dasva"]
        voice_text = "Arre bro, dekho yeh 30 full stack terms hain, dhyaan se suno. "
        for i, (num, term, desc) in enumerate(terms[:30]):
            if i < 10:
                prefix = hindi_nums[i] if i < len(hindi_nums) else f"Number {num}"
            else:
                prefix = f"Number {num}"
            voice_text += f"{prefix}, {term}, {desc}. "
            if (i+1) % 5 == 0:
                voice_text += " ... "
        voice_text += " Bas itna hi bro, ye sab yaad kar lo!"
        return voice_text
    import re as re2
    text = re2.sub(r'```.*?```', '', text, flags=re2.DOTALL)
    text = re2.sub(r'`[^`]*`', '', text)
    text = re2.sub(r'\*\*', '', text)
    text = re2.sub(r'#{1,6}\s?', '', text)
    text = re2.sub(r'<[^>]+>', '', text)
    text = re2.sub(r'<tool.*?</tool>', '', text, flags=re2.DOTALL)
    text = re2.sub(r'https?://\S+', '', text)
    text = text.replace("🔥"," ").replace("🚀"," ").replace("😎","").replace("🤖","").replace("🎤","")
    text = re2.sub(r'\n+', '. ', text)
    text = re2.sub(r'\s+', ' ', text)
    if len(text) > 3800:
        text = text[:3800] + ". Bas itna hi bro!"
    return text.strip()

async def text_to_voice_edge(text, filename="voice_reply.mp3"):
    try:
        clean_text = clean_for_speech(text)
        if not clean_text or len(clean_text.strip()) < 3:
            clean_text = "Bro, kaam ho gaya hai, check kar lo!"
        voice = "en-US-GuyNeural"
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(filename)
        print(f"✅ Edge-TTS saved: {filename}")
        return filename
    except Exception as e:
        print(f"Edge-TTS error: {e}")
        try:
            from gtts import gTTS
            tts = gTTS(clean_text[:4000], lang='en', tld='com', slow=False)
            tts.save(filename)
            return filename
        except:
            return None

def text_to_voice_sync(text, filename="voice_reply.mp3"):
    try:
        clean_text = clean_for_speech(text)
        from gtts import gTTS
        tts = gTTS(clean_text[:4000], lang='en', tld='com', slow=False)
        tts.save(filename)
        return filename
    except:
        return None

def text_to_voice(text, filename="voice_reply.mp3"):
    return text_to_voice_sync(text, filename)

# === FLASK ===
# === FLASK ===
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return f"Abbas AI Day 8.1 Designed + Real Human Voice LIVE! TTS:{HAS_TTS} | {datetime.now()}"

@app_flask.route('/health')
def health():
    return {"status":"ok","tts":HAS_TTS,"day":"7.4 Human Voice"}

def run_flask():
    try:
        app_flask.run(host='0.0.0.0', port=8080, debug=False)
    except:
        pass

# === SECURITY ===
def is_owner(uid):
    return uid == OWNER_ID

def owner_only(func):
    async def wrapper(update, context):
        if not is_owner(update.effective_user.id):
            await update.message.reply_text(f"❌ Owner only! Your ID: {update.effective_user.id}")
            return
        return await func(update, context)
    return wrapper

# === AGENT LOOP ===
async def agent_loop(goal, message):
    """Autonomous agent that does file tasks"""
    try:
        await message.reply_text(f"🤖 Abbas Agent Day 8.1 Activated!\n🎯 Goal: {goal}\n🧠 Planning...")
        
        # Get file list for context
        try:
            files = os.listdir('.')
            files_str = ", ".join(files[:20])
        except:
            files_str = "unknown"

        system = f"""You are Abbas Agent - autonomous file editor. You work in Wispbyte container at /home/container.
Current files: {files_str}
Goal: {goal}

You must think step-by-step and use tools:
<tool shell>{{"cmd":"ls -la"}}</tool> to list files
<tool read>{{"path":"README.md"}}</tool> to read
<tool write>{{"path":"README.md","content":"..."}}</tool> to write
<tool gitpush>{{"msg":"commit msg"}}</tool> to push

RULES:
- Do ls -la first
- Read before write
- For README edits, read README.md then write updated version
- Always finish with final summary
- Keep thinking in Roman Urdu + English mix like Abbas
- Steps: Step 1 - Thinking: ... then tool
"""

        prompt = f"Goal: {goal}\n\nStart! First do ls -la to see files."

        full_history = [{"role":"system","content":system},{"role":"user","content":prompt}]
        final_summary = ""

        for step in range(1, 9):
            try:
                # Call AI for next step
                headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
                data = {"model": MODELS[0], "messages": full_history, "max_tokens": 2000}
                r = await http_client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if r.status_code != 200:
                    data["model"] = MODELS[1]
                    r = await http_client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                
                if r.status_code == 200:
                    j = r.json()
                    ai_text = j["choices"][0]["message"]["content"]
                    full_history.append({"role":"assistant","content":ai_text})
                    
                    await message.reply_text(f"Step {step} - Thinking:\n{ai_text[:800]}")

                    # Parse tools
                    shell_match = re.search(r'<tool shell>\s*(\{.*?\})\s*</tool>', ai_text, re.DOTALL)
                    read_match = re.search(r'<tool read>\s*(\{.*?\})\s*</tool>', ai_text, re.DOTALL)
                    write_match = re.search(r'<tool write>\s*(\{.*?\})\s*</tool>', ai_text, re.DOTALL)
                    git_match = re.search(r'<tool gitpush>\s*(\{.*?\})\s*</tool>', ai_text, re.DOTALL)

                    if shell_match:
                        try:
                            cmd_data = json.loads(shell_match.group(1))
                            cmd = cmd_data.get("cmd","ls -la")
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                            out = (result.stdout + result.stderr)[:1500]
                            full_history.append({"role":"user","content":f"Tool shell output:\n{out}"})
                            await message.reply_text(f"🔧 Shell: {cmd}\n{out[:500]}")
                        except Exception as e:
                            full_history.append({"role":"user","content":f"Shell error: {e}"})

                    if read_match:
                        try:
                            read_data = json.loads(read_match.group(1))
                            path = read_data.get("path","")
                            if os.path.exists(path):
                                with open(path,'r',encoding='utf-8',errors='ignore') as f:
                                    content = f.read()[:3000]
                                full_history.append({"role":"user","content":f"File {path}:\n{content}"})
                                await message.reply_text(f"📖 Read {path} ({len(content)} chars)")
                            else:
                                full_history.append({"role":"user","content":f"File {path} not found, files: {files_str}"})
                        except Exception as e:
                            full_history.append({"role":"user","content":f"Read error: {e}"})

                    if write_match:
                        try:
                            # Extract write content more safely
                            write_json_str = write_match.group(1)
                            # Try json parse
                            write_data = json.loads(write_json_str)
                            path = write_data.get("path","")
                            write_content = write_data.get("content","")
                            if path and write_content:
                                with open(path,'w',encoding='utf-8') as f:
                                    f.write(write_content)
                                full_history.append({"role":"user","content":f"Wrote {path} OK ({len(write_content)} chars)"})
                                await message.reply_text(f"✅ Wrote {path}")
                        except Exception as e:
                            # Try manual extraction
                            try:
                                m = re.search(r'"path"\s*:\s*"([^"]+)"', write_json_str)
                                path = m.group(1) if m else "README.md"
                                # Content between "content":" and last " }
                                # Simple fallback
                                full_history.append({"role":"user","content":f"Write parse error: {e} - trying to continue"})
                            except:
                                full_history.append({"role":"user","content":f"Write error: {e}"})

                    if git_match:
                        try:
                            git_data = json.loads(git_match.group(1))
                            msg = git_data.get("msg", f"Agent: {goal[:50]}")
                            # Git push
                            subprocess.run("git add .", shell=True, timeout=10)
                            subprocess.run(f'git commit -m "{msg}"', shell=True, timeout=10)
                            if GITHUB_PAT:
                                subprocess.run(f"git push https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git main", shell=True, timeout=20)
                            else:
                                subprocess.run("git push origin main", shell=True, timeout=20)
                            full_history.append({"role":"user","content":"Git push done!"})
                            await message.reply_text("🚀 Git push done!")
                        except Exception as e:
                            full_history.append({"role":"user","content":f"Git push error: {e}"})

                    # Check if final
                    if "final summary" in ai_text.lower() or "mission complete" in ai_text.lower() or step == 8:
                        final_summary = ai_text
                        break

                    if step == 8:
                        final_summary = ai_text
                else:
                    await message.reply_text(f"❌ AI error: {r.status_code}")
                    break
            except Exception as e:
                await message.reply_text(f"Agent step {step} error: {e}\n{traceback.format_exc()[:500]}")
                break

        if not final_summary:
            final_summary = f"Goal {goal} pe kaam kiya, check files bro!"

        # Final message
        await message.reply_text(f"🎉 Agent Mission Complete!\n\n{final_summary[:3000]}")
        
        # Voice reply human-like
        if HAS_TTS and final_summary:
            vf = text_to_voice(final_summary)
            if vf and os.path.exists(vf):
                try:
                    await message.reply_voice(open(vf, 'rb'), caption="🎤 Agent Voice Summary - Human Style!")
                    try:
                        os.remove(vf)
                    except:
                        pass
                except Exception as e:
                    await message.reply_text(f"Voice error: {e}")
    except Exception as e:
        await message.reply_text(f"❌ Agent error: {e}\n{traceback.format_exc()[:800]}")

# === COMMANDS ===
async def start_command(u, c):
    await u.message.reply_text(
        f"🚀 Abbas AI - Day 8.1 Designed + Real Human Voice FINAL FIXED ✅\n\n"
        f"👋 Salam bro! Main Abbas Hussain AI!\n"
        f"Day 8.1 - Human-like Voice + Normal Chat Fixed!\n\n"
        f"Commands:\n"
        f"/start - Ye message\n"
        f"/id - Apna ID\n"
        f"/ai <sawal> - AI se pucho\n"
        f"/agent <goal> - Agent file tasks\n"
        f"/voice <text> - Voice reply + Agent mode\n"
        f"/battery, /ls, /run, /uptime, /web\n"
        f"/deploy, /backup, /gitpush\n\n"
        f"Normal text bhi kaam karega! Jaise:\n"
        "30 Terms batao\n\n"
        f"TTS: {'✅' if HAS_TTS else '❌'} | Wispbyte LIVE 🎤",
        parse_mode='Markdown'
    )

async def id_command(u, c):
    await u.message.reply_text(f"🆔 Your ID: {u.effective_user.id}\nName: {u.effective_user.first_name}")

async def ai_command(u, c):
    text = " ".join(c.args) if c.args else ""
    if not text:
        await u.message.reply_text("Use: /ai <sawal>\nExample: /ai 30 Full Stack terms batao")
        return
    await u.message.reply_chat_action("typing")
    ans = await call_ai(text, is_voice=False)
    if not ans or len(ans.strip()) == 0:
        ans = "❌ Khali jawab aaya, dobara try kar bro!"
    # Split if long
    designed = format_designed_response(ans, text)
    if len(designed) > 4000:
        for i in range(0, len(designed), 4000):
            chunk = designed[i:i+4000]
            if chunk.strip():
                try:
                    await u.message.reply_text(chunk, parse_mode='Markdown')
                except:
                    await u.message.reply_text(chunk)
    else:
        try:
            await u.message.reply_text(designed, parse_mode='Markdown')
        except:
            await u.message.reply_text(designed)

async def agent_command(u, c):
    if not is_owner(u.effective_user.id):
        await u.message.reply_text("❌ Owner only!")
        return
    goal = " ".join(c.args) if c.args else ""
    if not goal:
        await u.message.reply_text("Use: /agent <goal>\nExample: /agent README me Day 8.1 section add kar")
        return
    await agent_loop(goal, u.message)

async def voice_command(u, c):
    text = " ".join(c.args) if c.args else ""
    if text:
        # Check if agent task
        lower = text.lower()
        agent_keywords = ["bana", "add kar", "create", "file", "readme", "bot.py", "command", "push", "deploy", "edit", "section", "update", "likh", "write", "journey"]
        is_agent_task = any(k in lower for k in agent_keywords)
        
        if is_agent_task:
            if not is_owner(u.effective_user.id):
                await u.message.reply_text("❌ Agent owner only!")
                return
            await u.message.reply_text(f"🎤 Voice: {text}\n🤖 Agent mode! Planning...")
            await agent_loop(text, u.message)
            return
        else:
            await u.message.reply_chat_action("typing")
            await u.message.reply_text(f"🎤 Voice command: {text}\n🧠 Soch raha hun human style me...")
            ans = await call_ai(text, is_voice=True)
            if not ans or len(ans.strip()) == 0:
                ans = "Bro samajh gaya! Full Stack ka safar jaari hai!"
            await u.message.reply_text(ans)
            if HAS_TTS:
                vf = text_to_voice(ans)
                if vf and os.path.exists(vf):
                    try:
                        await u.message.reply_voice(open(vf, 'rb'), caption="🎤 Voice Reply - Human Style Day 8.1")
                        try:
                            os.remove(vf)
                        except:
                            pass
                    except Exception as e:
                        await u.message.reply_text(f"TTS error: {e}")
            return

    # No text - guide
    await u.message.reply_text(
        f"🎤 Day 8.1 Voice Agent Guide\n\n"
        f"Text se:\n"
        f"/voice 30 Terms batao - Voice reply\n"
        f"/voice README me add kar - Agent + Voice\n\n"
        f"Voice message: Mic dabake bolo!\n\n"
        f"TTS: {'✅' if HAS_TTS else '❌'} LIVE!",
        parse_mode='Markdown'
    )

# Other commands
async def battery_command(u, c):
    try:
        r = subprocess.run("termux-battery-status 2>/dev/null || echo '{}'", shell=True, capture_output=True, text=True)
        await u.message.reply_text(f"🔋 Battery: {r.stdout[:500]}")
    except:
        await u.message.reply_text("🔋 Battery info not available on Wispbyte")

async def ls_command(u, c):
    path = " ".join(c.args) if c.args else "."
    try:
        out = subprocess.run(f"ls -la {path}", shell=True, capture_output=True, text=True, timeout=5).stdout
        await u.message.reply_text(f"📁 {path}:\n{out[:3000]}")
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")

@owner_only
async def run_command(u, c):
    cmd = " ".join(c.args) if c.args else ""
    if not cmd:
        await u.message.reply_text("Use: /run <cmd>")
        return
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        out = (r.stdout + r.stderr)[:3500]
        await u.message.reply_text(f"🔧 {cmd}\n{out or 'No output'}")
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")

async def uptime_command(u, c):
    await u.message.reply_text(f"⏰ Uptime: {time.time()}\nDay 8.1 Human Voice LIVE! TTS:{HAS_TTS}")

async def web_command(u, c):
    await u.message.reply_text(f"🌐 Dashboard: {VERCEL_URL}\nFlask: :8080")

@owner_only
async def deploy_command(u, c):
    try:
        r = subprocess.run("git pull origin main", shell=True, capture_output=True, text=True, timeout=20)
        await u.message.reply_text(f"📥 Deploy:\n{r.stdout[:2000]}\n{r.stderr[:500]}")
    except Exception as e:
        await u.message.reply_text(f"Deploy error: {e}")

@owner_only
async def backup_command(u, c):
    try:
        subprocess.run("zip -r backup.zip *.py *.md 2>/dev/null", shell=True, timeout=10)
        await u.message.reply_text("💾 Backup created!")
    except Exception as e:
        await u.message.reply_text(f"Backup error: {e}")

@owner_only
async def gitpush_command(u, c):
    msg = " ".join(c.args) if c.args else "Update by Abbas AI Day 8.1"
    try:
        subprocess.run("git add .", shell=True, timeout=10)
        subprocess.run(f'git commit -m "{msg}"', shell=True, timeout=10)
        if GITHUB_PAT:
            r = subprocess.run(f"git push https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git main", shell=True, capture_output=True, text=True, timeout=20)
        else:
            r = subprocess.run("git push origin main", shell=True, capture_output=True, text=True, timeout=20)
        await u.message.reply_text(f"🚀 Push:\n{r.stdout[:1500]}\n{r.stderr[:500]}")
    except Exception as e:
        await u.message.reply_text(f"Push error: {e}")

async def ping_command(u, c):
    await u.message.reply_text("🏓 Pong! Day 8.1 Human Voice LIVE!")

async def help_command(u, c):
    await u.message.reply_text("/start /id /ai /agent /voice /battery /ls /run /uptime /web /deploy /backup /gitpush /ping /help /kingff")

async def kingff_command(u, c):
    await u.message.reply_text("👑 KingFF Bot - From KingFF Faucet to Voice Agent! Journey: Termux -> Fly.io -> bot-hosting.net -> Wispbyte -> Vercel Dashboard LIVE! Built by AbbasFullstack 16yo Islamabad!")

# === NORMAL TEXT HANDLER - FIX FOR 30 TERMS ===
async def handle_text(u, c):
    text = u.message.text.strip()
    if not text or len(text) < 2:
        return
    await u.message.reply_chat_action("typing")
    ans = await call_ai(text, is_voice=False)
    if not ans or len(ans.strip()) == 0:
        ans = "Bro samajh gaya! Bolo kya chahiye?"
    if len(ans.strip()) == 0:
        ans = "Yaar jawab khali aaya, dobara pucho bro!"
    designed = format_designed_response(ans, text)
    if len(designed) > 4000:
        for i in range(0, len(designed), 4000):
            chunk = designed[i:i+4000]
            if chunk.strip():
                try:
                    await u.message.reply_text(chunk, parse_mode='Markdown')
                except:
                    await u.message.reply_text(chunk)
    else:
        try:
            await u.message.reply_text(designed, parse_mode='Markdown')
        except:
            await u.message.reply_text(designed)

async def handle_voice(u, c):
    try:
        await u.message.reply_text("🎤 Voice message mili! Transcribe kar raha hun... Day 8.1 me Whisper API optional hai, demo voice bhej raha hun!")
        if HAS_TTS:
            demo = "Bro voice message receive ho gayi hai! Day 8.1 Designed + Real Human Voice live hai! Ab normal text bhi kaam karega jaise 30 terms batao, aur voice bhi human jaisi ayegi! KingFF se leke Voice Agent tak ka safar!"
            vf = text_to_voice(demo)
            if vf and os.path.exists(vf):
                await u.message.reply_voice(open(vf, 'rb'), caption="🎤 Day 8.1 Voice Reply")
                try:
                    os.remove(vf)
                except:
                    pass
    except Exception as e:
        await u.message.reply_text(f"Voice error: {e}")

# === MAIN ===
async def main():
    Thread(target=run_flask, daemon=True).start()
    print(f"✅ Abbas AI ONLINE - Day 8.1 Designed + Real Human Voice - Python {sys.version.split()[0]}")
    print(f"🌐 Flask :8080 | Vercel {VERCEL_URL} | Wispbyte | TTS {HAS_TTS} | Voice Agent LIVE 🎤")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("agent", agent_command))
    app.add_handler(CommandHandler("voice", voice_command))
    app.add_handler(CommandHandler("battery", battery_command))
    app.add_handler(CommandHandler("ls", ls_command))
    app.add_handler(CommandHandler("run", run_command))
    app.add_handler(CommandHandler("uptime", uptime_command))
    app.add_handler(CommandHandler("web", web_command))
    app.add_handler(CommandHandler("deploy", deploy_command))
    app.add_handler(CommandHandler("backup", backup_command))
    app.add_handler(CommandHandler("gitpush", gitpush_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kingff", kingff_command))

    # Normal text handler - MUST be before voice handler, with filter for non-command text
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    print("🤖 Polling started - Day 8.1 Human Voice Ready!")
    # Keep alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
    except Exception as e:
        print(f"Crash: {e}\n{traceback.format_exc()}")
        time.sleep(5)
        try:
            asyncio.run(main())
        except:
            pass
