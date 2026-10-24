import os, subprocess, requests, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_KEY")
MODELS = ["minimax/minimax-m3.1-flash:free","google/gemma-4-26b-a4b:free"]

ABBAS_PROFILE = """
You are Abbas Hussain AI - Personal AI Assistant created by Abbas Hussain.
Creator: Abbas Hussain (Abbasdev), 16yo, Islamabad, Pakistan, 11th Grade, Full Stack AI Engineer.
Stack: React, Next.js, TypeScript, Node.js, PostgreSQL, MongoDB, Supabase, GCP, AWS, Vercel, Docker.
Projects: DevDesk AI, OpenAPI Forge, VaultX, CryptoWatch.
Goals: LeetCode Contest, Germany Chancenkarte 2027/28, Target Stripe/Shopify/Atlassian.
If asked who are you / kisne banaya: Say You are Abbas Hussain AI, created by Abbas Hussain from Islamabad, 16-year-old Full Stack AI Engineer.
"""

def ask_ai(prompt):
    if not AI_KEY: return "AI_KEY missing"
    for model in MODELS:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {AI_KEY}","Content-Type":"application/json"},
                json={"model": model, "messages": [{"role": "system", "content": ABBAS_PROFILE}, {"role": "user", "content": prompt}]}, timeout=40)
            j=r.json()
            if "choices" in j and j["choices"]: return j["choices"][0]["message"]["content"]
        except: continue
    return "AI Error - try later"

async def start(u,c): await u.message.reply_text("🤖 Abbas Hussain AI ON ✅\nIslamabad ka 16yo Full Stack AI Engineer ne banaya!\n/ai pucho ya normal msg bhejo! 🚀")
async def battery(u,c): await u.message.reply_text(subprocess.getoutput("termux-battery-status 2>&1 || echo 'Fly.io pe 24/7 Online ✅'")[:4000])
async def shell(u,c):
    cmd=u.message.text.replace("/shell","",1).strip()
    if not cmd: await u.message.reply_text("Use: /shell ls"); return
    await u.message.reply_text(f"$ {cmd}\n{subprocess.getoutput(cmd)}"[:4000])
async def ai_cmd(u,c):
    p=u.message.text.replace("/ai","",1).strip()
    if not p: await u.message.reply_text("Use: /ai tum kaun ho?"); return
    tmp=await u.message.reply_text("Soch raha hun... 🤔"); await tmp.edit_text(ask_ai(p)[:4000])
async def handle_all(u,c): await u.message.reply_text(ask_ai(u.message.text)[:4000])

async def main():
    request = HTTPXRequest(connect_timeout=60, read_timeout=60)
    app = Application.builder().token(BOT_TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start)); app.add_handler(CommandHandler("battery", battery))
    app.add_handler(CommandHandler("shell", shell)); app.add_handler(CommandHandler("ai", ai_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    await app.initialize(); await app.start(); await app.updater.start_polling()
    print("Abbas Hussain AI ONLINE ✅")
    while True: await asyncio.sleep(3600)

if __name__ == "__main__": asyncio.run(main())
