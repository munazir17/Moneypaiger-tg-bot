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

# ==================== DEVELOPER DETAILS ====================
DEV_X = "https://x.com/Moneypaiger"
DEV_TG = "@astro789"
DEV_WALLET = "0xE0e0d239853c5F2Fe0a524d544eC9eB71fef486e"
# ===========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 **Welcome to Base AI Agent (Autopilot Deployed)!**\n\n"
        "Main Base Chain par completely automated framework par chal raha hoon.\n\n"
        "📌 **Commands:**\n"
        "👤 /dev - Developer Identity & Verification\n"
        "💳 /agent_wallet - Agent's On-chain Wallet\n"
        "💬 Type any message to chat with my AI brain!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def dev_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧠 **Verified Developer Info**\n\n"
        f"👤 **Telegram:** {DEV_TG}\n"
        f"💳 **Dev Wallet:** `{DEV_WALLET}`\n\n"
        "Click the buttons below to verify or connect:"
    )
    keyboard = [
        [InlineKeyboardButton("🐦 Follow on X", url=DEV_X)],
        [InlineKeyboardButton("🔗 BaseScan Explorer", url=f"https://basescan.org/address/{DEV_WALLET}")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def get_agent_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance_str = "0 ETH"
    if w3.is_connected() and "0x" in agent_wallet:
        try:
            balance_str = f"{w3.from_wei(w3.eth.get_balance(agent_wallet), 'ether'):.4f} ETH"
        except Exception:
            balance_str = "Error fetching balance"
    
    text = f"🤖 **Agent Wallet:** `{agent_wallet}`\n💰 **Current Balance:** {balance_str}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ai_client:
        await update.message.reply_text("⚠️ OpenAI API Key sequence missing.")
        return
    
    thinking = await update.message.reply_text("🤔 Analytical processing...")
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a Base Chain AI Agent named Moneypaiger. Developer Telegram: {DEV_TG}. Developer X: {DEV_X}."},
                {"role": "user", "content": update.message.text}
            ]
        )
        await thinking.edit_text(response.choices[0].message.content)
    except Exception as e:
        await thinking.edit_text(f"❌ Execution Error: {str(e)}")

def main():
    if not TOKEN:
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN missing!")
        sys.exit(1)
        
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dev", dev_details))
    app.add_handler(CommandHandler("agent_wallet", get_agent_wallet))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_chat))
    
    print("🚀 Autopilot Agent active on Base Chain...")
    app.run_polling()

if __name__ == "__main__":
    main()
