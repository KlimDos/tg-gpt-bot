#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Bot to reply to Telegram messages which contains key words from given list.
Replays are based on openai text models
https://platform.openai.com/docs/api-reference/completions/create

Usage:
"""

import logging
import os

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import openai
import json
from dotenv import load_dotenv
#import asyncio

load_dotenv()
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a few command handlers.
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE, msg) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()} "
        f"{msg}",
        reply_markup=ForceReply(selective=True),
    )
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    # Opening JSON file
    f = open("src/persistance/persistance.json")
    data = json.load(f)

    await update.message.reply_text("Список слов на которые реагирует бот: \n"
                                    f"{data['init_key_words_list']}")
    
    f.close


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """put user to ignored list"""

    # Opening JSON file
    with open("src/persistance/persistance.json","r+") as f:
        data = json.load(f)
        data['ignore_users'].append(update.effective_user.id)
        data['ignore_users'] = list(set(data['ignore_users']))
        # cleanup file
        f.seek(0)
        f.truncate()
        json.dump(data, f, ensure_ascii=False)
        f.close()
        logger.info(f"User {update.effective_user.id} added to ignored")

async def let_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """put user to ignored list"""

    # Opening JSON file
    with open("src/persistance/persistance.json","r+") as f:
        data = json.load(f)
        data['ignore_users'].remove(update.effective_user.id)
        # cleanup file
        f.seek(0)
        f.truncate()
        json.dump(data, f, ensure_ascii=False)
        f.close()
        logger.info(f"User {update.effective_user.id} removed from ignored")


# Function to be called when messages are received
async def process_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    message = update.message.text
    logger.info(
        f"User {update._effective_user.id} {update._effective_user.full_name} message: {message}")

    # Opening JSON file
    f = open("src/persistance/persistance.json")
    data = json.load(f)

    if update.effective_user.id in data['ignore_users']:
        logger.info(f"{update.effective_user.id} in ignore_users")
        return

    # In case any init key words in message, respond to msg
    matches = []
    for elem in data['init_key_words_list']:
        if elem in message.lower():
            matches.append(elem)
            logger.info(f"Found: {elem} in {message}")
    #if any(print(elem) in message for elem in data['init_key_words_list']):
            # Available AI models
            #models = openai.Model.list()

    # Specify the prompt and parameters for generating text
    # Generate text using the OpenAI API
    if matches:
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=message,
                max_tokens=1000,
                temperature=0
                )

        if response.choices:
            # Replay to to given message
            await update.message.reply_text(
                f"{response.choices[0].text}\n\n"
                f"matches: {matches} tokens: {response['usage']['total_tokens']}")
            await context.bot.send_message(chat_id=242426387, text=""
                f"prompt tokens: {response['usage']['prompt_tokens']} "
                f"completion tokens: {response['usage']['completion_tokens']} "
                f"total tokens spent: {response['usage']['total_tokens']} ")
            logger.info(
                "Respond sent "
                f"prompt tokens: {response['usage']['prompt_tokens']} "
                f"completion tokens: {response['usage']['completion_tokens']} "
                f"total tokens spent: {response['usage']['total_tokens']} ")
        else:
            await context.bot.send_message(chat_id=242426387, text=f"Error generating text: {response.error}")
    f.close()

# async def send_tg_log(msg: str, app: Application):
#       return await app.bot.send_message(chat_id=242426387, text=msg)

# def sync_func(app):
#     print('Start sync_func')
#     # Запуск асинхронной функции
#     asyncio.run(async_func(app))
#     print('End sync_func')

# async def async_func(app: Application):
#     print('Start async_func')
#     await app.bot.send_message(chat_id=242426387, text='msg')
#     print('End async_func')

def main() -> None:
    """Start the bot."""
    TG_API_TOKEN = os.getenv('TG_API_TOKEN')
    # Set your OpenAI API key
    openai.api_key = os.getenv('GPT_API_TOKEN')

    with open(f"readme.md", 'r') as f:
        markdown_string = f.read()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TG_API_TOKEN).build()

    application.add_handler(CommandHandler("about", lambda update, context: about(update, context, markdown_string)))
    application.add_handler(CommandHandler("keywords", help_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("let", let_command))
    # execute reply_to_message func on every message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_msg))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    asyncio.run(application.bot.send_message(chat_id=242426387, text="msg"))


if __name__ == "__main__":
    main()
