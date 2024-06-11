import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from Database import db
from Packges.Global_Functions import delete_old_khatma_opening_request
from Startup.CallBackData import CallBackData
from Startup.Keyboards import Keyboards
from Startup.KhatmaStatus import KhatmaStatus
from Startup.Text import Text
from Startup.UserStates import UserStates


async def contribute_to_public_khatma_options_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    page_id = int(data[2])
    page_size = int(data[3])
    new_sort = ("asc" if data[4] == "1" else "desc")
    khatma_list = await db.get_khatma_public_list(sort_by_date=new_sort, page_size=page_size, page_id=page_id)
    count_all_public_khatmas = await db.count_number_of_public_khatmas()
    contribute_public_khatma_explain_message_keyboard = InlineKeyboardMarkup(
        await Keyboards.get_khatma_public_list_keyboard(khatma_list=khatma_list,
                                                        is_asc=(True if new_sort == "asc" else False), page_id=page_id,
                                                        page_size=page_size,
                                                        number_of_all_khatmas=count_all_public_khatmas))
    await query.answer()
    try:
        await query.edit_message_text(text=Text.create_public_khatma_explain_text(),
                                      reply_markup=contribute_public_khatma_explain_message_keyboard,
                                      parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(e)


async def contribute_to_public_khatma_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    khatma_list = await db.get_khatma_public_list()
    count_all_public_khatmas = await db.count_number_of_public_khatmas()
    if len(khatma_list) == 0:
        contribute_public_khatma_explain_message_text = Text.Contribute_Public_Khatma_Empty_Explain_Text
        contribute_public_khatma_explain_message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_back_to_main_menu())
        contribute_khatma_message_object = await query.edit_message_text(
            text=contribute_public_khatma_explain_message_text,
            reply_markup=contribute_public_khatma_explain_message_keyboard)
    else:
        contribute_public_khatma_explain_message_text = Text.create_public_khatma_explain_text()
        contribute_public_khatma_explain_message_keyboard = InlineKeyboardMarkup(
            await Keyboards.get_khatma_public_list_keyboard(khatma_list=khatma_list,
                                                            number_of_all_khatmas=count_all_public_khatmas))
        await delete_old_khatma_opening_request(chat_id, context)
        contribute_khatma_message_object = await query.edit_message_text(
            text=contribute_public_khatma_explain_message_text,
            reply_markup=contribute_public_khatma_explain_message_keyboard, parse_mode="MarkdownV2")
    context.user_data["state"] = UserStates.Contribute_Public_Khatma_Menu
    context.user_data["temp_message_id"] = contribute_khatma_message_object.id
    await query.answer()


async def contribute_to_private_khatma_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    contribute_private_khatma_explain_message_text = Text.Contribute_Private_Khatma_Explain_Text
    contribute_private_khatma_explain_message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_back_to_main_menu())
    await delete_old_khatma_opening_request(chat_id, context)
    contribute_khatma_message_object = await query.edit_message_text(
        text=contribute_private_khatma_explain_message_text,
        reply_markup=contribute_private_khatma_explain_message_keyboard)
    context.user_data["state"] = UserStates.Contribute_Private_Khatma_Waiting_ID
    context.user_data["temp_message_id"] = contribute_khatma_message_object.id
    await query.answer()


async def view_khatma_from_contribute_parts(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    is_refresh = False
    if data[2].endswith("R"):
        is_refresh = True
    if is_refresh:
        khatma_id = int(data[2][:-1])
    else:
        khatma_id = int(data[2])
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Opened:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                           start_date=khatma_data.time)
        khatma_info_message_keyboard = Keyboards.get_khatma_parts_from_my_parts_options_keyboard(khatma_id=khatma_id,
                                                                                                 khatma_parts=khatma_parts_data)
    elif khatma_status == KhatmaStatus.Done:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=False,
                                                           is_finished=True)
        khatma_info_message_keyboard = [
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Current_Contribution_Parts)]]
    else:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=True,
                                                           is_finished=False)
        khatma_info_message_keyboard = [
            [InlineKeyboardButton("عودة", callback_data=CallBackData.Current_Contribution_Parts)]]
    khatma_info_message_keyboard = InlineKeyboardMarkup(khatma_info_message_keyboard)
    if is_refresh:
        await query.answer(text=Text.Khatma_Parts_Refresh_Done, show_alert=False)
    try:
        await query.edit_message_text(text=khatma_info_message_text,
                                      reply_markup=khatma_info_message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def view_public_khatma_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    khatma_id = int(data[2])
    page_id = int(data[3])
    page_size = int(data[4])
    sort = ("asc" if data[5] == "1" else "desc")
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Opened:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                           start_date=khatma_data.time)
        khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                khatma_parts=khatma_parts_data,
                                                                                                have_return_button=True,
                                                                                                return_button_page_id=page_id,
                                                                                                return_button_page_size=page_size,
                                                                                                return_button_is_asc=
                                                                                                (
                                                                                                    True if sort == "asc" else False)))
    elif khatma_status == KhatmaStatus.Done:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=False,
                                                           is_finished=True)
        khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                khatma_parts=[],
                                                                                                have_return_button=True,
                                                                                                have_refresh_button=False,
                                                                                                return_button_page_id=page_id,
                                                                                                return_button_page_size=page_size,
                                                                                                return_button_is_asc=
                                                                                                (
                                                                                                    True if sort == "asc" else False)))
    else:
        khatma_info_message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                           intention=khatma_data.description,
                                                           duration_in_days=0,
                                                           start_date=khatma_data.start_date,
                                                           end_date=khatma_data.end_date,
                                                           is_canceled=True,
                                                           is_finished=False)
        khatma_info_message_keyboard = InlineKeyboardMarkup(Keyboards.get_khatma_parts_keyboard(khatma_id=khatma_id,
                                                                                                khatma_parts=[],
                                                                                                have_return_button=True,
                                                                                                have_refresh_button=False,
                                                                                                return_button_page_id=page_id,
                                                                                                return_button_page_size=page_size,
                                                                                                return_button_is_asc=
                                                                                                (
                                                                                                    True if sort == "asc" else False)))
    await query.edit_message_text(text=khatma_info_message_text,
                                  reply_markup=khatma_info_message_keyboard, parse_mode=ParseMode.MARKDOWN_V2)


async def contribute_khatma_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    contribute_khatma_explain_message_text = Text.Contribute_Khatma_Explain_Text
    contribute_khatma_explain_message_keyboard = InlineKeyboardMarkup(Keyboards.get_contribute_khatma_type_keyboard())
    await delete_old_khatma_opening_request(chat_id, context)

    await query.edit_message_text(text=contribute_khatma_explain_message_text,
                                  reply_markup=contribute_khatma_explain_message_keyboard)
    context.user_data["state"] = UserStates.Contribute_Khatma_Waiting_Type
    await query.answer()
