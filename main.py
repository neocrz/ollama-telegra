from conf import TOKEN
import logging
import json  
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

LLM_API_URL = 'http://localhost:11434/api/generate'  # Replace with the correct API URL

# Default LLM model
current_model = "orca-mini"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = generate_response(user_input)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def generate_response(user_input):
    payload = {
        "model": current_model,  # Use the current LLM model
        "prompt": user_input
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response_lines = response.text.strip().split('\n')
        concatenated_response = "".join([json.loads(line)["response"] for line in response_lines if "response" in json.loads(line)])
        return concatenated_response

    except Exception as e:
        return f"Error: {str(e)}"

async def change_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_model
    new_model = context.args[0]  # Get the model name from the command
    current_model = new_model
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"LLM model changed to {new_model}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), msg)
    change_model_handler = CommandHandler('model', change_model)

    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    application.add_handler(change_model_handler)

    application.run_polling()
