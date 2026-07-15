from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from config.Global_Files import About_Image_File
from config.Keyboards import Keyboards
from config.Text import Text
from config.UserStates import UserStates


async def about_bot_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    browse_quran_text = Text.About_Bot
    browse_quran_keyboard = InlineKeyboardMarkup(Keyboards.get_about_bot_keyboard())
    await query.answer()
    await context.bot.send_photo(chat_id=chat_id, caption=browse_quran_text, photo=About_Image_File,
                                 reply_markup=browse_quran_keyboard)
    await query.delete_message()
    context.user_data["state"] = UserStates.Nothing
