import logging

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(name)s - %(message)s', 
    level=logging.INFO
)

from envparse import env
from telegram import Update, constants
from telegram.ext import (filters, Application, ApplicationBuilder, 
                          CommandHandler, MessageHandler, ContextTypes)
from varcache import Varcache

env.read_envfile()

APP_TOKEN = env.str('APP_TOKEN')
TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN')


START_TEXT = """
Welcome to NotifierAlexfomalhaut bot. 
Since it is private, please, provide `APP_TOKEN` to continue.
""".strip()


async def post_init(application: Application):
    application.bot_data['vcache'] = Varcache(dirpath='./data')
    application.bot_data['chats'] = application.bot_data['vcache'].load(
        name='chats', default=set
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=START_TEXT,
        parse_mode=constants.ParseMode.MARKDOWN,
    )


async def message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get chat_id
    chat_id = update.effective_chat.id

    # Check chat_id is not registered
    if chat_id not in application.bot_data['chats']:
        # Interpret given message as token
        token = update.message.text.strip()

        # If token is valid, save the chat
        if token == APP_TOKEN:
            # Add chat_id to chats
            application.bot_data['chats'].add(chat_id)

            # Flush chats to the disk
            application.bot_data['vcache'].save(application.bot_data['chats'])

            # Define response text
            resp = "Token is valid. Now you can receive the notifications."
        else:
            # Define response text
            resp = "Token is not correct. Please, try again."

        # Reply
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=resp,
            parse_mode=constants.ParseMode.MARKDOWN,
        )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN) \
        .post_init(post_init).build()

    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(MessageHandler(filters.ALL, message_command))

    application.run_polling()
