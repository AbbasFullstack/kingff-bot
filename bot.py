import os, sys, asyncio, subprocess, json, time, traceback, random, re
from datetime import datetime
from flask import Flask
from threading import Thread

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

print("Loading Abbas AI Day 10 - ChatGPT Animation + Ultra Voice...")

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_REPO = os.getenv("GITHUB_REPO", "AbbasFullstack/kingff-bot")
OWNER_ID = int(os.getenv("OWNER_ID", "8752799745"))
VERCEL_URL = os.getenv("VERCEL_URL", "https://abbas-ai-dashboard.vercel.app")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY", "")

HAS_TTS = False
HAS_EDGE_TTS = False
HAS_ELEVENLABS = False

if ELEVENLABS_KEY:
    HAS_ELEVENLABS = True
    HAS_TTS = True
    print("ElevenLabs API Key found - Ultra Real Voice Ready!")

try:
    import edge_tts
    HAS_EDGE_TTS = True
    HAS_TTS = True
    print("Edge-TTS OK - Real Human Voice")
except:
    print("Edge-TTS not found")

try:
    from gtts import gTTS
    if not HAS_TTS:
        HAS_TTS = True
    print("gTTS OK - Fallback")
except:
    print("gTTS fail")

try:
    import pydub
    print("pydub OK")
except:
    pass

print(f"BOT_TOKEN: {bool(BOT_TOKEN)} | AI_KEY: {bool(AI_KEY)} | TTS: {HAS_TTS} | ElevenLabs: {HAS_ELEVENLABS}")

if not BOT_TOKEN:
    print("BOT_TOKEN missing!")
    sys.exit(1)

MODELS = [
    "recursive/flint-v1.0:free",
    "nvidia/nemotron-3.5-super-vl:free",
    "dots-studio/dots-3-note-preview:free"
]

AI_MODEL = MODELS[0]
AI_MODEL_FALLBACK = MODELS[1]
AI_MODEL_FALLBACK2 = MODELS[2]

http_client = httpx.AsyncClient(timeout=60.0)

async def call_ai(prompt, is_voice=False):
    if not AI_KEY:
        return "AI_KEY missing bro!"
    headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
    if is_voice:
        system_prompt = "You are Abbas Hussain AI, 16yo Full Stack Engineer from Islamabad. Speak like REAL human friend - Roman Urdu + English mix, natural, warm. For VOICE: talk face-to-face, use natural pauses. No stars or markdown for voice. Keep under 3000 chars. Make it fun!"
    else:
        system_prompt = """You are Abbas Hussain AI - MIRA STYLE CLONE - 16yo Full Stack Engineer, Islamabad.
CRITICAL FORMATTING RULES (Mira style):
1. When user asks 30 Terms - ALWAYS return ONE term per line, like:
1) AI - Artificial Intelligence - Machine ko smart banaya jata hai
2) API - Application Programming Interface - Apps ek dusre se baat karte hain
NEVER return all terms in one line!
2. For advanced features - Use Mira catalog style:
1) Terminal (remote shell)
   • Kya: user ko restricted shell...
   • Kyun: debugging...
   • Kaise: containerized...
   • Security: never expose host...
3. For code/commands - Use code blocks with language
4. Use bullet points •, bold for headings, clean spacing
5. No excessive *** or ___ 
6. Roman Urdu + English mix, friendly, concise"""

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
    return "AI busy hai, thodi der baad try kar bro!"

# === DAY 10: SMART PARSER + DESIGNED UI ===
def parse_terms_from_text(text):
    """MIRA STYLE - Perfect term parser"""
    terms = []
    # Clean markdown mess
    text = text.replace('**', '').replace('* *', ' ').strip()
    # Pattern 1: 1. AI = Artificial Intelligence - Machine...
    # The AI is returning all in one line like "*1. AI = ... *2. API = ..."
    # Split by pattern like *2. or 2.
    # First, normalize: replace "*2." with "\n2."
    text_norm = re.sub(r'\s*\*?(\d+)\.\s*\*?', r'\n\1. ', text)
    lines = text_norm.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match: 1. AI = Artificial... or 1. Backend = Server - side - Data...
        m = re.match(r'^(\d+)\.\s*(.+?)\s*=\s*(.+)$', line)
        if m:
            num, term, desc = m.groups()
            # Clean L- symbol
            desc = desc.replace('└─', '').replace('L-', '').replace('|__', '').strip()
            # Remove trailing *2. etc that got merged
            desc = re.split(r'\s*\*?\d+\.\s*', desc)[0]
            terms.append((num.strip(), term.strip()[:50], desc.strip()[:200]))
        else:
            # Try: 1. Term - Definition
            m2 = re.match(r'^(\d+)\.\s*(.+?)\s*-\s*(.+)$', line)
            if m2:
                num, term, desc = m2.groups()
                terms.append((num.strip(), term.strip()[:50], desc.strip()[:200]))
    return terms


def format_designed_response(text, query=""):
    """MIRA STYLE - Best Design, no bekar formatting"""
    if not text or len(text.strip()) == 0:
        return "Khali jawab, dobara try karo!"
    lower_q = (query.lower() if query else "")
    lower_t = text.lower()
    
    # === MIRA STYLE FOR 30 TERMS ===
    is_terms = any(k in lower_q or k in lower_t for k in ["30 terms", "full stack terms", "terms batao", "frontend", "mira"])
    if is_terms:
        terms = parse_terms_from_text(text)
        if len(terms) >= 3:
            # Mira style: Compact, bullet points, bold headings
            designed = "📚 *30 Full Stack Terms*\n\n"
            for num, term, desc in terms[:30]:
                term_clean = term.strip()
                desc_clean = desc.strip()
                # Mira style: 1) Term (bold) - definition
                designed += f"*{num}) {term_clean}*\n"
                designed += f"   • {desc_clean}\n\n"
            designed += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            designed += "💡 *Tip:* Interview me kaam ayega!\n"
            return designed
        else:
            # Fallback: Clean the messy text
            clean = text.replace('**', '').replace('└─', '').replace('L─', '')
            clean = re.sub(r'\s*\*(\d+)\.', r'\n\n*\1.', clean)
            clean = re.sub(r'\n{3,}', '\n\n', clean)
            designed = "📚 *30 Full Stack Terms*\n\n" + clean[:3500]
            return designed
    
    # === MIRA STYLE FOR ADVANCED FEATURES / GENERAL ===
    if any(k in lower_q for k in ["advance feature", "terminal", "browser access", "agent"]):
        # Mira style catalog
        # Check if already in Mira format (has "Kya:", "Kyun:", "Kaise:")
        if "Kya:" in text or "Kyun:" in text:
            # Already Mira-like, just clean and format
            designed = text
            designed = designed.replace('•', '  •')
            return designed[:4000]
    
    # === MIRA STYLE FOR OPENROUTER LIMIT / CODE ===
    if "rate_limit" in lower_t or "curl" in lower_t or "API_KEY" in text:
        # This is code - format with proper code blocks + explanations
        # Extract parts
        designed = "🔍 *OpenRouter API Limit Check*\n\n"
        designed += text[:3500]
        # Ensure code blocks have language
        designed = designed.replace('```bash', '```bash\n').replace('```python', '```python\n').replace('```js', '```javascript\n')
        return designed
    
    # === MIRA STYLE FOR TERMINAL ===
    if "total" in lower_t and "drwx" in lower_t:
        # This is ls output, will be handled in terminal_command
        return text
    
    # General: Mira clean style
    if len(text) > 300:
        # Clean up the bekar stars
        clean = text.replace('***', '').replace('___', '')
        # Limit excessive bold
        designed = clean[:3500]
        return designed
    
    return text


def clean_agent_output_for_user(text):
    if not text:
        return ""
    text = re.sub(r'<tool\s+\w+>.*?</tool>', '', text, flags=re.DOTALL)
    text = re.sub(r'<tool.*?</tool>', '', text, flags=re.DOTALL)
    text = re.sub(r'\{\s*"cmd"\s*:\s*".*?"\s*\}', '', text, flags=re.DOTALL)
    text = re.sub(r'<thinking>\s*Step \d+.*?Thinking:\s*', '', text, flags=re.DOTALL)
    text = re.sub(r'</thinking>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def format_code_block_with_copy(text):
    if '```' in text:
        return text
    if any(x in text.lower() for x in ['bot.py', 'requirements', 'shell:', 'exit:', '$ ', 'total ', 'drwx']):
        return f"```\n{text[:3000]}\n```"
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
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'#{1,6}\s?', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'<tool.*?</tool>', '', text, flags=re.DOTALL)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    if len(text) > 3800:
        text = text[:3800] + ". Bas itna hi bro!"
    return text.strip()

async def text_to_voice_edge(text, filename="voice_reply.mp3"):
    try:
        clean_text = clean_for_speech(text)
        if not clean_text or len(clean_text.strip()) < 3:
            clean_text = "Bro, kaam ho gaya hai, check kar lo!"
        lower = clean_text.lower()
        is_funny = any(w in lower for w in ['haha', 'hehe', 'lol', 'maza', 'mast', 'wah', 'hahaha'])
        is_excited = any(w in lower for w in ['awesome', 'amazing', 'wow', 'zabardast', 'mubarak'])
        is_sad = any(w in lower for w in ['sad', 'sorry', 'galti', 'error', 'fail', 'afsoos'])
        is_serious = any(w in lower for w in ['important', 'warning', 'dhyaan', 'security', 'danger'])
        
        if HAS_ELEVENLABS and ELEVENLABS_KEY:
            try:
                voice_id = "21m00Tcm4TlvDq8ikWAM"
                stability = 0.5
                similarity = 0.8
                style = 0.5
                if is_funny:
                    stability = 0.3
                    style = 0.8
                elif is_sad:
                    stability = 0.8
                    style = 0.2
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(
                        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                        headers={"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"},
                        json={
                            "text": clean_text[:2500],
                            "model_id": "eleven_multilingual_v2",
                            "voice_settings": {"stability": stability, "similarity_boost": similarity, "style": style, "use_speaker_boost": True}
                        }
                    )
                    if resp.status_code == 200:
                        with open(filename, 'wb') as f:
                            f.write(resp.content)
                        print(f"ElevenLabs Voice: {filename}")
                        return filename
            except Exception as e:
                print(f"ElevenLabs error: {e}")
        
        voice = "en-US-AriaNeural"
        if is_funny:
            style = "cheerful"
            rate = "+10%"
            pitch = "+5%"
        elif is_excited:
            style = "excited"
            rate = "+15%"
            pitch = "+8%"
        elif is_sad:
            style = "sad"
            rate = "-10%"
            pitch = "-5%"
        elif is_serious:
            style = "serious"
            rate = "-5%"
            pitch = "-2%"
        else:
            style = "chat"
            rate = "+5%"
            pitch = "+0%"
        
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="{voice}">
        <mstts:express-as style="{style}">
            <prosody rate="{rate}" pitch="{pitch}">
                {clean_text}
            </prosody>
        </mstts:express-as>
    </voice>
</speak>"""
        try:
            communicate = edge_tts.Communicate(ssml, voice)
            await communicate.save(filename)
            return filename
        except:
            communicate = edge_tts.Communicate(clean_text, voice)
            await communicate.save(filename)
            return filename
    except Exception as e:
        print(f"Voice error: {e}")
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

def detect_emotion_for_log(text):
    lower = text.lower()
    if any(w in lower for w in ['haha', 'lol', 'maza']):
        return "Cheerful/Laugh"
    elif any(w in lower for w in ['awesome', 'wow']):
        return "Excited"
    elif any(w in lower for w in ['sad', 'sorry', 'error']):
        return "Sad"
    elif any(w in lower for w in ['important', 'warning']):
        return "Serious"
    else:
        return "Friendly/Chat"

# === SANDBOX TERMINAL ===
TERMINAL_BLACKLIST = [
    'rm -rf /', 'rm -rf /*', ':(){:|:&};:', 'mkfs', 'dd if=', '>/dev/sda',
    'shutdown', 'reboot', 'poweroff', 'halt',
    'sudo rm', 'sudo mkfs', 'chmod 777 /', 'chown -R', 'mv / /*',
    'curl | sh', 'wget | sh', 'bash -i', 'nc -l',
    '> /etc/passwd', '> /etc/shadow', 'fork bomb', 'while true; do',
    'rm -rf ~', 'rm -rf /home', 'rm -rf /root'
]

def is_safe_command(cmd):
    lower = cmd.lower().strip()
    for bad in TERMINAL_BLACKLIST:
        if bad.lower() in lower:
            return False, f"Blocked: {bad}"
    if lower.startswith('sudo ') and any(x in lower for x in ['rm', 'mkfs', 'dd', 'chmod', 'chown', 'mv']):
        return False, "Sudo destructive blocked"
    if '>' in lower and any(x in lower for x in ['/etc/', '/dev/', '/boot/', '/proc/', '/sys/']):
        return False, "Redirect to system path blocked"
    return True, "OK"

def run_shell_command(cmd, timeout=15):
    is_safe, reason = is_safe_command(cmd)
    if not is_safe:
        return f"Blocked: {reason}\nCommand: {cmd}", 1
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=os.getcwd())
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        if not output:
            output = f"Executed (exit {result.returncode}) - No output"
        else:
            output = f"$ {cmd}\n━━━━━━━━━━━━━━━━━━━━━━━━━\n{output}\n━━━━━━━━━━━━━━━━━━━━━━━━━\nExit: {result.returncode}"
        if len(output) > 3500:
            output = output[:3500] + "\n... truncated"
        return output, result.returncode
    except Exception as e:
        return f"Error: {e}", 1

# === FLASK ===
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return f"Abbas AI Day 10 LIVE! TTS:{HAS_TTS} ElevenLabs:{HAS_ELEVENLABS} | {datetime.now()}"

@app_flask.route('/health')
def health():
    return {"status":"ok","tts":HAS_TTS,"elevenlabs":HAS_ELEVENLABS,"day":"10"}

def run_flask():
    try:
        app_flask.run(host='0.0.0.0', port=8080, debug=False)
    except:
        pass

def is_owner(uid):
    return uid == OWNER_ID

def owner_only(func):
    async def wrapper(update, context):
        if not is_owner(update.effective_user.id):
            await update.message.reply_text(f"Owner only! Your ID: {update.effective_user.id}")
            return
        return await func(update, context)
    return wrapper

# === DAY 10: CHATGPT ANIMATION ===
async def send_typing_animation(message_obj, full_text, delay=0.025):
    """DAY 8.1: ChatGPT Smooth Typing - Single Message Edit + Blinking Cursor"""
    try:
        displayed = ""
        words = full_text.split()
        # Smoother: 2 words at a time
        chunk_size = 2
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            displayed += chunk + " "
            # Blinking cursor
            cursor = "▌" if (i // chunk_size) % 2 == 0 else " "
            preview = displayed + cursor
            if len(preview) > 3800:
                preview = preview[-3800:]
            try:
                await message_obj.edit_text(preview)
            except:
                try:
                    await message_obj.edit_text(preview[:4000])
                except:
                    pass
            await asyncio.sleep(delay)
        # Final without cursor
        try:
            await message_obj.edit_text(full_text[:4000], parse_mode='Markdown')
        except:
            await message_obj.edit_text(full_text[:4000])
    except Exception as e:
        print(f"Typing error: {e}")
        try:
            await message_obj.edit_text(full_text[:4000])
        except:
            pass

async def animate_thinking_box_smooth(message_obj, query_text, duration=3):
    """MIRA STYLE Thinking - Clean, small bubble with timer like Mira"""
    try:
        start = asyncio.get_event_loop().time()
        idx = 0
        while asyncio.get_event_loop().time() - start < duration:
            elapsed = int(asyncio.get_event_loop().time() - start)
            # Mira style: Simple, clean, with timer
            if idx % 2 == 0:
                txt = f"🌟 Thinking\n{elapsed}s"
            else:
                txt = f"💭 Thinking\n{elapsed}s"
            try:
                await message_obj.edit_text(txt)
            except:
                pass
            await asyncio.sleep(0.7)
            idx += 1
    except:
        pass

async def send_typing_animation_mira(message_obj, full_text, delay=0.02):
    """MIRA STYLE - No typing cursor mess, direct clean edit"""
    try:
        # Mira doesn't do word-by-word, it types then shows full
        # We will do: show typing... then final
        await message_obj.edit_text("🌟 Thinking... 1s")
        await asyncio.sleep(0.5)
        # Final clean
        await message_obj.edit_text(full_text[:4000], parse_mode='Markdown')
    except:
        try:
            await message_obj.edit_text(full_text[:4000])
        except:
            pass



# === COMMANDS ===
async def start_command(u, c):
    tts_type = "ElevenLabs Ultra Real" if HAS_ELEVENLABS else ("Edge-TTS Real Human" if HAS_EDGE_TTS else "gTTS")
    msg = (
        "🚀 Abbas AI - Day 10 ChatGPT Animation + Ultra Voice\n\n"
        "Day 10 - ChatGPT Typing + Thinking Box + Real Voice!\n\n"
        f"Voice: {tts_type}\n\n"
        "Commands:\n"
        "/terminal <cmd> - Sandbox Terminal\n"
        "/ai <sawal> - AI + Designed + Typing Animation\n"
        "/agent <goal> - Agent + Clean Output\n"
        "/voice <text> - Emotional Real Voice\n"
        "/update - Hot update guide\n"
        "/hotfix voice <emotion> - Test voice\n\n"
        "Try:\n"
        "/terminal ls -la\n"
        "/ai 30 Terms batao\n\n"
        f"Day 10 LIVE | {tts_type}"
    )
    await u.message.reply_text(msg)

async def id_command(u, c):
    await u.message.reply_text(f"Your ID: {u.effective_user.id}\nName: {u.effective_user.first_name}")

async def ai_command(u, c):
    text = " ".join(c.args) if c.args else ""
    if not text:
        await u.message.reply_text("Use: /ai <sawal>\nExample: /ai 30 Full Stack terms batao")
        return
    thinking = await u.message.reply_text("Thinking...\n```\nPROCESSING\n```", parse_mode='Markdown')
    for i in range(2):
        try:
            await thinking.edit_text(f"Thinking step {i+1}...\n```\n{text[:20]}\n```", parse_mode='Markdown')
            await asyncio.sleep(0.6)
        except:
            pass
    ans = await call_ai(text, is_voice=False)
    if not ans or len(ans.strip()) == 0:
        ans = "Khali jawab, dobara try karo!"
    designed = format_designed_response(ans, text)
    designed = clean_agent_output_for_user(designed)
    if '```' not in designed and len(designed) > 200:
        if any(x in designed.lower() for x in ['bot.py', 'def ', 'import ', 'shell:', 'exit:']):
            designed = f"```\n{designed[:3500]}\n```"
    try:
        await send_typing_animation(thinking, designed, delay=0.02)
    except:
        try:
            await thinking.edit_text(designed[:4000], parse_mode='Markdown')
        except:
            await thinking.edit_text(designed[:4000])

async def terminal_command(u, c):
    if not is_owner(u.effective_user.id):
        await u.message.reply_text("Terminal owner only! Security")
        return
    cmd = " ".join(c.args) if c.args else ""
    if not cmd:
        await u.message.reply_text(
            "💻 *Day 10 Sandbox Terminal*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Use: /terminal <command>\n\n"
            "✅ Safe Examples:\n"
            "`/terminal ls -la`\n"
            "`/terminal pwd`\n"
            "`/terminal cat bot.py | head -20`\n"
            "`/terminal git status`\n"
            "`/terminal python3 --version`\n"
            "`/terminal df -h`\n\n"
            "❌ Blocked: rm -rf /, sudo mkfs\n",
            parse_mode='Markdown'
        )
        return
    await u.message.reply_chat_action("typing")
    msg = await u.message.reply_text(f"💻 Executing: `{cmd}`", parse_mode='Markdown')
    output, code = run_shell_command(cmd, timeout=20)
    try:
        if len(output) > 3500:
            filename = f"terminal_{int(time.time())}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            await u.message.reply_document(open(filename, 'rb'), filename=filename, caption=f"Terminal: {cmd} (Exit: {code})")
            try:
                os.remove(filename)
            except:
                pass
            await msg.delete()
        else:
            await send_typing_animation(msg, f"```\n{output}\n```", delay=0.01)
    except:
        await u.message.reply_text(output[:4000])

async def shell_command(u, c):
    await terminal_command(u, c)

async def exec_command(u, c):
    await terminal_command(u, c)

async def update_command(u, c):
    if not is_owner(u.effective_user.id):
        await u.message.reply_text("Owner only!")
        return
    await u.message.reply_text(
        "🔥 *Day 10 HOT UPDATE - GitHub jaye bina!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Method 1: Direct Download (Best!)*\n"
        "`/terminal curl -sL https://raw.githubusercontent.com/AbbasFullstack/kingff-bot/main/bot.py -o bot.py && ls -lh bot.py`\n\n"
        "*Method 2: Git Pull*\n"
        "`/deploy` → Git se latest pull!\n\n"
        "*Method 3: ElevenLabs Setup*\n"
        "1. https://elevenlabs.io → Free API Key lo\n"
        "2. Wispbyte Env me add karo: ELEVENLABS_API_KEY=your_key\n"
        "3. Restart → Ultra Real Voice!\n\n"
        "💡 Fastest: Main file dunga, tu /terminal me paste karna!",
        parse_mode='Markdown'
    )

async def hotfix_command(u, c):
    if not is_owner(u.effective_user.id):
        return
    cmd = " ".join(c.args) if c.args else ""
    if not cmd:
        await u.message.reply_text(
            "🔧 *Hotfix Commands*\n\n"
            "`/hotfix voice cheerful` - Test cheerful\n"
            "`/hotfix voice sad` - Test sad\n"
            "`/hotfix voice excited` - Test excited\n"
            "`/hotfix update_bot <url>` - Download bot.py\n",
            parse_mode='Markdown'
        )
        return
    if cmd.startswith('voice'):
        emotion = cmd.split('voice')[-1].strip()
        test_texts = {
            'cheerful': "Hahaha bro! Wah kya baat hai! Maza aa gaya! Full stack engineer ban gaye!",
            'excited': "Wow bro! Zabardast! Day 10 complete ho gaya! Terminal LIVE hai!",
            'sad': "Sorry bro, thoda error aa gaya tha, lekin ab fix kar diya hai, afsoos mat karo...",
            'serious': "Dhyaan se suno bro, yeh security ka mamla hai, important hai, carefully karna.",
            'friendly': "Arre yaar bro, dekho aise karte hain, simple hai, main samjha deta hun!"
        }
        test_text = test_texts.get(emotion, test_texts['friendly'])
        await u.message.reply_text(f"Testing voice: {emotion}\nText: {test_text}")
        try:
            vf = await text_to_voice_edge(test_text, f"test_{emotion}.mp3")
            if vf:
                await u.message.reply_voice(open(vf, 'rb'), caption=f"{emotion} - {detect_emotion_for_log(test_text)}")
                try:
                    os.remove(vf)
                except:
                    pass
        except Exception as e:
            await u.message.reply_text(f"Voice test error: {e}")
    elif cmd.startswith('update_bot'):
        parts = cmd.split()
        if len(parts) >= 2:
            url = parts[1]
            await u.message.reply_text(f"Downloading bot.py from: {url}")
            output, code = run_shell_command(f"curl -sL {url} -o bot.py && wc -l bot.py", timeout=15)
            await u.message.reply_text(f"```\n{output[:3500]}\n```", parse_mode='Markdown')

async def voice_command(u, c):
    text = " ".join(c.args) if c.args else ""
    if text:
        lower = text.lower()
        agent_keywords = ["bana", "add kar", "create", "file", "readme", "bot.py", "command", "push", "deploy", "edit", "section", "update", "likh", "write", "journey"]
        is_agent_task = any(k in lower for k in agent_keywords)
        if is_agent_task:
            if not is_owner(u.effective_user.id):
                await u.message.reply_text("Agent owner only!")
                return
            await u.message.reply_text(f"Voice: {text}\nAgent mode! Day 10 Clean!")
            await agent_loop(text, u.message)
            return
        else:
            thinking = await u.message.reply_text("Thinking... Real human style...", parse_mode='Markdown')
            ans = await call_ai(text, is_voice=True)
            if not ans or len(ans.strip()) == 0:
                ans = "Bro samajh gaya! Full Stack ka safar jaari hai!"
            designed = format_designed_response(ans, text)
            designed = clean_agent_output_for_user(designed)
            try:
                await send_typing_animation(thinking, designed, delay=0.02)
            except:
                await thinking.edit_text(designed[:4000])
            if HAS_TTS:
                try:
                    if HAS_EDGE_TTS or HAS_ELEVENLABS:
                        vf = await text_to_voice_edge(ans, "voice_day10.mp3")
                    else:
                        vf = text_to_voice_sync(ans, "voice_day10.mp3")
                    if vf and os.path.exists(vf):
                        await u.message.reply_voice(open(vf, 'rb'), caption=f"Day 10 Emotional Voice - {detect_emotion_for_log(ans)}")
                        try:
                            os.remove(vf)
                        except:
                            pass
                except Exception as e:
                    await u.message.reply_text(f"Voice error: {e}")
            return
    await u.message.reply_text(
        "🎤 Day 10 Voice Agent Guide\n\n"
        "Text se:\n"
        "/voice 30 Terms batao - Designed + Real Voice\n"
        "/voice README me add kar - Agent + Voice\n\n"
        "Voice message: Mic dabake bolo!\n"
        f"TTS: {'ElevenLabs Ultra Real' if HAS_ELEVENLABS else ('Edge-TTS Real Human' if HAS_EDGE_TTS else 'gTTS')} LIVE!"
    )

async def battery_command(u, c):
    try:
        r = subprocess.run("termux-battery-status 2>/dev/null || echo '{}'", shell=True, capture_output=True, text=True)
        await u.message.reply_text(f"Battery: {r.stdout[:500]}")
    except:
        await u.message.reply_text("Battery info not available on Wispbyte")

async def ls_command(u, c):
    path = " ".join(c.args) if c.args else "."
    try:
        out = subprocess.run(f"ls -la {path}", shell=True, capture_output=True, text=True, timeout=5).stdout
        await u.message.reply_text(f"```\n{out[:3000]}\n```", parse_mode='Markdown')
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")

async def run_command(u, c):
    if not is_owner(u.effective_user.id):
        await u.message.reply_text("Owner only!")
        return
    cmd = " ".join(c.args) if c.args else ""
    if not cmd:
        await u.message.reply_text("Use: /run <cmd>")
        return
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        out = (r.stdout + r.stderr)[:3500]
        await u.message.reply_text(f"```\n{out or 'No output'}\n```", parse_mode='Markdown')
    except Exception as e:
        await u.message.reply_text(f"Error: {e}")

async def uptime_command(u, c):
    await u.message.reply_text(f"Uptime: {time.time()}\nDay 10 ChatGPT Animation LIVE! TTS:{HAS_TTS} ElevenLabs:{HAS_ELEVENLABS}")

async def web_command(u, c):
    await u.message.reply_text(f"Dashboard: {VERCEL_URL}\nFlask: :8080")

async def deploy_command(u, c):
    if not is_owner(u.effective_user.id):
        await u.message.reply_text("Owner only!")
        return
    try:
        r = subprocess.run("git pull origin main", shell=True, capture_output=True, text=True, timeout=20)
        await u.message.reply_text(f"Deploy:\n```\n{r.stdout[:2000]}\n{r.stderr[:500]}\n```", parse_mode='Markdown')
    except Exception as e:
        await u.message.reply_text(f"Deploy error: {e}")

async def backup_command(u, c):
    if not is_owner(u.effective_user.id):
        return
    try:
        subprocess.run("zip -r backup.zip *.py *.md 2>/dev/null", shell=True, timeout=10)
        await u.message.reply_text("Backup created!")
    except Exception as e:
        await u.message.reply_text(f"Backup error: {e}")

async def gitpush_command(u, c):
    if not is_owner(u.effective_user.id):
        return
    msg = " ".join(c.args) if c.args else "Update by Abbas AI Day 10"
    try:
        subprocess.run("git add .", shell=True, timeout=10)
        subprocess.run(f'git commit -m "{msg}"', shell=True, timeout=10)
        if GITHUB_PAT:
            r = subprocess.run(f"git push https://{GITHUB_PAT}@github.com/{GITHUB_REPO}.git main", shell=True, capture_output=True, text=True, timeout=20)
        else:
            r = subprocess.run("git push origin main", shell=True, capture_output=True, text=True, timeout=20)
        await u.message.reply_text(f"Push:\n```\n{r.stdout[:1500]}\n{r.stderr[:500]}\n```", parse_mode='Markdown')
    except Exception as e:
        await u.message.reply_text(f"Push error: {e}")

async def ping_command(u, c):
    await u.message.reply_text("Pong! Day 10 ChatGPT Animation LIVE!")

async def help_command(u, c):
    await u.message.reply_text("/start /id /ai /agent /voice /terminal /update /hotfix /ls /run /uptime /web /deploy /backup /gitpush /ping /help")

async def kingff_command(u, c):
    await u.message.reply_text("KingFF Bot - From Faucet to Day 10 ChatGPT Animation! Built by AbbasFullstack 16yo Islamabad!")

async def handle_text(u, c):
    text = u.message.text.strip()
    if not text or len(text) < 2:
        return
    thinking = await u.message.reply_text("Thinking...\n```\nPROCESSING\n```", parse_mode='Markdown')
    for i in range(2):
        try:
            await thinking.edit_text(f"Thinking step {i+1}...\n```\n{text[:20]}\n```", parse_mode='Markdown')
            await asyncio.sleep(0.5)
        except:
            pass
    ans = await call_ai(text, is_voice=False)
    if not ans or len(ans.strip()) == 0:
        ans = "Bro samajh gaya! Bolo kya chahiye?"
    designed = format_designed_response(ans, text)
    designed = clean_agent_output_for_user(designed)
    try:
        await send_typing_animation(thinking, designed, delay=0.02)
    except:
        try:
            await thinking.edit_text(designed[:4000], parse_mode='Markdown')
        except:
            await thinking.edit_text(designed[:4000])

async def handle_voice(u, c):
    try:
        await u.message.reply_text("Voice message mili! Transcribe kar raha hun... Day 10 me demo voice bhej raha hun!")
        if HAS_TTS:
            demo = "Bro voice message receive ho gayi hai! Day 10 ChatGPT Animation + Emotional Voice live hai!"
            if HAS_EDGE_TTS or HAS_ELEVENLABS:
                vf = await text_to_voice_edge(demo, "voice_demo.mp3")
            else:
                vf = text_to_voice_sync(demo, "voice_demo.mp3")
            if vf and os.path.exists(vf):
                await u.message.reply_voice(open(vf, 'rb'), caption="Day 10 Voice Reply")
                try:
                    os.remove(vf)
                except:
                    pass
    except Exception as e:
        await u.message.reply_text(f"Voice error: {e}")

async def agent_loop(goal, message):
    if not is_owner(message.from_user.id):
        await message.reply_text("Agent owner only!")
        return
    thinking_msg = await message.reply_text("Thinking...\n```\nPROCESSING GOAL\n```", parse_mode='Markdown')
    tools_desc = "Tools: write_file(path, content), read_file(path), list_files(), git_status(), git_push(message), terminal(command)"
    system_prompt = f"You are Abbas AI Agent Day 10. Goal: {goal}\n{tools_desc}\nRules: Think step by step, use tools, max 8 steps, final summary clean no tool JSON leaks. If security update, check .gitignore for .env"
    history = [{"role": "user", "content": f"Goal: {goal}. Start."}]
    final_summary = ""
    max_steps = 8
    for step in range(max_steps):
        try:
            await thinking_msg.edit_text(f"Step {step+1} - Thinking...\n```\n{goal[:30]}\n```", parse_mode='Markdown')
        except:
            pass
        try:
            import httpx
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-6:])
            response = None
            for model in MODELS:
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}, json={"model": model, "messages": messages, "max_tokens": 1000})
                        if resp.status_code == 200:
                            data = resp.json()
                            response = data['choices'][0]['message']['content']
                            break
                except:
                    continue
            if not response:
                response = "Agent: Task completed"
        except Exception as e:
            await thinking_msg.edit_text(f"Agent error: {e}")
            return
        tool_used = False
        observation = ""
        try:
            if "write_file" in response.lower():
                m = re.search(r'write_file.*?path.*?["\'](.*?)["\']', response, re.DOTALL)
                if m:
                    path = m.group(1)
                    # Try to extract content
                    cm = re.search(r'content.*?["\'](.*?)["\']', response, re.DOTALL)
                    content = cm.group(1) if cm else "Test content"
                    try:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        observation = f"Wrote {path} ({len(content)} chars)"
                    except Exception as e:
                        observation = f"Write error: {e}"
                    tool_used = True
            elif "read_file" in response.lower():
                m = re.search(r'read_file.*?path.*?["\'](.*?)["\']', response)
                if m:
                    path = m.group(1)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            cont = f.read()[:3000]
                        observation = f"Read {path}: {cont[:2000]}"
                    except Exception as e:
                        observation = f"Read error: {e}"
                    tool_used = True
            elif "list_files" in response.lower():
                try:
                    files = os.listdir('.')
                    observation = f"Files: {', '.join(files[:20])}"
                except Exception as e:
                    observation = f"List error: {e}"
                tool_used = True
            elif "terminal" in response.lower():
                m = re.search(r'(?:terminal|shell).*?["\'](.*?)["\']', response)
                if m:
                    cmd = m.group(1)
                    out, code = run_shell_command(cmd, timeout=15)
                    observation = f"Terminal {cmd} -> Exit {code}: {out[:1500]}"
                    tool_used = True
            elif "git_status" in response.lower():
                out, code = run_shell_command("git status --short", timeout=10)
                observation = f"Git status: {out[:1500]}"
                tool_used = True
            elif "git_push" in response.lower():
                m = re.search(r'git_push.*?["\'](.*?)["\']', response)
                msg = m.group(1) if m else f"Agent: {goal}"
                out, code = run_shell_command(f'git add . && git commit -m "{msg}" && git push', timeout=20)
                observation = f"Git push: {out[:1500]}"
                tool_used = True
        except Exception as e:
            observation = f"Tool parse error: {e}"
        if tool_used:
            history.append({"role": "assistant", "content": response})
            history.append({"role": "user", "content": f"Tool result: {observation}\nContinue or finish."})
            clean_obs = clean_agent_output_for_user(observation)
            if clean_obs:
                formatted = format_code_block_with_copy(clean_obs)
                try:
                    await message.reply_text(f"Step {step+1}:\n{formatted}", parse_mode='Markdown')
                except:
                    await message.reply_text(f"Step {step+1}: {clean_obs[:3000]}")
        else:
            final_summary = clean_agent_output_for_user(response)
            break
        await asyncio.sleep(0.5)
    try:
        await thinking_msg.edit_text("Agent Complete! Preparing final...", parse_mode='Markdown')
        await asyncio.sleep(0.5)
        await thinking_msg.delete()
    except:
        pass
    if not final_summary:
        final_summary = f"Agent finished {step+1} steps for: {goal}"
    final_summary = clean_agent_output_for_user(final_summary)
    final_summary = final_summary.replace('<tool', '').replace('</tool>', '').replace('{"cmd"', '')
    final_msg = await message.reply_text("Typing... ▌", parse_mode='Markdown')
    designed_final = format_designed_response(final_summary, goal)
    if len(designed_final) > 100:
        await send_typing_animation(final_msg, f"🎉 *Agent Mission Complete!*\n\n{designed_final[:3500]}", delay=0.02)
    else:
        try:
            await final_msg.edit_text(f"🎉 *Agent Mission Complete!*\n\n{designed_final[:3500]}", parse_mode='Markdown')
        except:
            await final_msg.edit_text(f"Agent Complete: {designed_final[:3500]}")
    if HAS_TTS and final_summary:
        try:
            if HAS_EDGE_TTS or HAS_ELEVENLABS:
                vf = await text_to_voice_edge(final_summary, "voice_agent_day10.mp3")
            else:
                vf = text_to_voice_sync(final_summary, "voice_agent_day10.mp3")
            if vf and os.path.exists(vf):
                await message.reply_voice(open(vf, 'rb'), caption=f"Day 10 Voice - {detect_emotion_for_log(final_summary)}")
                try:
                    os.remove(vf)
                except:
                    pass
        except Exception as e:
            print(f"Agent voice error: {e}")

async def main():
    Thread(target=run_flask, daemon=True).start()
    print(f"Abbas AI ONLINE - Day 10 ChatGPT Animation + Ultra Voice - Python {sys.version.split()[0]}")
    print(f"Flask :8080 | Vercel {VERCEL_URL} | TTS {HAS_TTS} ElevenLabs {HAS_ELEVENLABS} | Terminal LIVE")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("agent", agent_loop))
    app.add_handler(CommandHandler("voice", voice_command))
    app.add_handler(CommandHandler("terminal", terminal_command))
    app.add_handler(CommandHandler("shell", shell_command))
    app.add_handler(CommandHandler("exec", exec_command))
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
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CommandHandler("hotfix", hotfix_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    print("Polling started - Day 10 Ready!")
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
