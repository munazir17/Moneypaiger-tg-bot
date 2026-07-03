import os
import sys
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from web3 import Web3
from openai import OpenAI

# Load configuration
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_RPC = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Web3 & OpenAI
w3 = Web3(Web3.HTTPProvider(BASE_RPC))
ai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

if w3.is_connected() and PRIVATE_KEY:
    agent_wallet = w3.eth.account.from_key(PRIVATE_KEY).address
else:
    agent_wallet = "Configuration Error / Not Connected"

# ==================== VERIFIED DEVELOPER DETAILS ====================
DEV_X = "https://x.com/Moneypaiger"
DEV_TG = "@astro789"
DEV_WALLET = "0xE0e0d239853c5F2Fe0a524d544eC9eB71fef486e"
# ====================================================================

# Dictionary to hold separate chat history for every public user
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"🤖 **Welcome {user_name} to Moneypaiger AI Agent!**\n\n"
        "Main Base Chain par completely automated public AI bot hoon. "
        "Aap mujhse crypto markets, smart contracts, ya koi bhi general query pooch sakte hain.\n\n"
        "📌 **Public Commands:**\n"
        "👤 /dev - Developer Identity & Verification\n"
        "💳 /agent_wallet - Agent's On-chain Wallet\n\n"
        "💬 Mujhse baat karne ke liye niche direct message type karein!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def dev_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧠 **Moneypaiger Developer Verification**\n\n"
        f"👤 **Telegram:** {DEV_TG}\n"
        f"💳 **Dev Wallet:** `{DEV_WALLET}`\n\n"
        "Click the buttons below to verify or connect directly with me:"
    )
    keyboard = [
        [InlineKeyboardButton("🐦 Follow Developer on X", url=DEV_X)],
        [InlineKeyboardButton("🔗 View On BaseScan", url=f"https://basescan.org/address/{DEV_WALLET}")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def get_agent_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance_str = "0 ETH"
    if w3.is_connected() and "0x" in agent_wallet:
        try:
            balance_str = f"{w3.from_wei(w3.eth.get_balance(agent_wallet), 'ether'):.4f} ETH"
        except Exception:
            balance_str = "Fetch Error"
    
    text = f"🤖 **Moneypaiger Agent Public Wallet:**\n`{agent_wallet}`\n\n💰 **Current Balance:** {balance_str}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if not ai_client:
        await update.message.reply_text("⚠️ Public AI brain is currently offline.")
        return

    # Initialize session memory for new public users
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system", "content": f"You are Moneypaiger AI, a public crypto agent on Base chain. Developer Telegram is {DEV_TG} and X profile is {DEV_X}. Keep answers precise, smart, and crypto-savvy."}
        ]
    
    # Append user message to history
    user_sessions[user_id].append({"role": "user", "content": user_message})
    
    # Keep history clean (Last 10 messages) to manage memory and API cost
    if len(user_sessions[user_id]) > 10:
        user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-9:]

    thinking = await update.message.reply_text("⚡ Processing request...")
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_sessions[user_id]
        )
        ai_reply = response.choices[0].message.content
        user_sessions[user_id].append({"role": "assistant", "content": ai_reply})
        await thinking.edit_text(ai_reply)
    except Exception as e:
        await thinking.edit_text("❌ Server busy. Please try again in a moment.")

def main():
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN missing!")
        sys.exit(1)
        
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dev", dev_details))
    app.add_handler(CommandHandler("agent_wallet", get_agent_wallet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat))
    
    print("🚀 Autopilot Agent active and ready for public use...")
    app.run_polling()

if __name__ == "__main__":
    main()
