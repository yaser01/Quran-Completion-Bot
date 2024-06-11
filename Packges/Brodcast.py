import asyncio
import logging

from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from Startup.Text import Text


async def send_completed_message_to_users(finished_parts_dict: dict, khatma_opener_user_id,
                                          context: ContextTypes.DEFAULT_TYPE):
    user_ids = finished_parts_dict.keys()
    for user_id in user_ids:
        try:
            message_text = Text.create_finished_khatma_text_for_user(finished_parts_dict[user_id],
                                                                     is_message_to_admin=False)
            await context.bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.MARKDOWN_V2)
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(0.3)
    if khatma_opener_user_id not in user_ids:
        try:
            message_text = Text.create_finished_khatma_text_for_user(list(finished_parts_dict.values())[0],
                                                                     is_message_to_admin=True)
            await context.bot.send_message(chat_id=khatma_opener_user_id, text=message_text,
                                           parse_mode=ParseMode.MARKDOWN_V2)
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(0.3)


async def send_canceled_khatma_message_to_users(parts_dict: dict, khatma_opener_user_id,
                                                context: ContextTypes.DEFAULT_TYPE):
    user_ids = parts_dict.keys()
    for user_id in user_ids:
        try:
            message_text = Text.create_canceled_khatma_text_for_user(parts_dict[user_id])
            await context.bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.MARKDOWN_V2)
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(0.3)
    if khatma_opener_user_id not in user_ids:
        try:
            message_text = Text.create_canceled_khatma_text_for_user(list(parts_dict.values())[0],
                                                                     is_message_to_admin=True)
            await context.bot.send_message(chat_id=khatma_opener_user_id, text=message_text,
                                           parse_mode=ParseMode.MARKDOWN_V2)
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(0.3)
