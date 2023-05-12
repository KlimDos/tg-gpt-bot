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
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, Updater

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

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE, msg) -> None:
    """Send a message when the command /start is issued."""

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )

    return await update.message.reply_text(
        f"Привет {update.effective_user.full_name}: \n"
        f"{msg}")

async def keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    
    await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.effective_message.id
        )
    # Opening JSON file
    f = open("src/persistance/persistance.json")
    data = json.load(f)
    await update.message.reply_text(
        "Список слов на которые реагирует бот: \n"
        f"{data['init_key_words_list']}")
    f.close

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    
    await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.effective_message.id
        )
    # Opening JSON file
    f = open("src/persistance/persistance.json")
    data = json.load(f)
    await update.message.reply_text(
        "Список слов на которые реагирует бот: \n"
        f"{data['init_key_words_list']}")
    f.close

async def del_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    
    await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.effective_message.id
        )
    # Opening JSON file
    f = open("src/persistance/persistance.json")
    data = json.load(f)
    await update.message.reply_text(
        "Список слов на которые реагирует бот: \n"
        f"{data['init_key_words_list']}")
    f.close



async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """put user to ignored list"""

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )

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
        await context.bot.send_message(
            chat_id=242426387, text=f"User {update.effective_user.id} added to ignored")

async def let_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """put user to ignored list"""

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )
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
        await context.bot.send_message(
            chat_id=242426387, text=f"User {update.effective_user.id} removed from ignored")

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
            # Available AI models
            #models = openai.Model.list()

    # Generate text using the OpenAI API
    promt = message.replace("\n","")
    if matches:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens=1000,
            temperature=0,
            messages= [{"role": "user","content": promt }]
        )
        if response.choices:
            # Replay to to given message
            await update.message.reply_text(
                f"{response['choices'][0]['message']['content']}\n\n"
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
    else:
        logger.info("no keywords found")
    f.close()

def main() -> None:
    """Start the bot."""

    TG_API_TOKEN = os.getenv('TG_API_TOKEN')
    openai.api_key = os.getenv('GPT_API_TOKEN')

    with open(f"about.md", 'r') as f:
        markdown_string = f.read()

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TG_API_TOKEN).build()

    # handle commands
    application.add_handler(CommandHandler("about", lambda update, context: about(update, context, markdown_string)))
    application.add_handler(CommandHandler("keywords", keywords_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("del", del_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("let", let_command))

    # execute reply_to_message func on every message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_msg))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
