import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Startup.Keyboards import Keyboards
from Startup.Text import Text
from Startup.UserStates import UserStates

load_dotenv()
PHOTO_ABOUT_ID = os.getenv('PHOTO_ABOUT_ID')


async def about_bot_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    browse_quran_text = Text.About_Bot
    browse_quran_keyboard = InlineKeyboardMarkup(Keyboards.get_about_bot_keyboard())
    await query.answer()
    await context.bot.send_photo(chat_id=chat_id, caption=browse_quran_text, photo=PHOTO_ABOUT_ID,
                                 reply_markup=browse_quran_keyboard)
    await query.delete_message()
    context.user_data["state"] = UserStates.Nothing
