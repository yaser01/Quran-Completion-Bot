import logging
from datetime import datetime
from functools import cmp_to_key

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Database import db
from Packges.Brodcast import send_completed_message_to_users
from Packges.Global_Functions import delete_old_khatma_opening_request, compare_between_part_asc, \
    format_timespan_in_arabic
from Startup.Keyboards import Keyboards
from Startup.Text import Text
from Startup.UserOptionsKeys import UserOptionsKeys
from Startup.UserStates import UserStates


async def current_contribution_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    current_contribution_message_text = Text.Current_Contribute_Explain_Text
    current_contribution_message_keyboard = InlineKeyboardMarkup(Keyboards.get_current_contributions_keyboard())
    await delete_old_khatma_opening_request(chat_id, context)
    await query.edit_message_text(text=current_contribution_message_text,
                                  reply_markup=current_contribution_message_keyboard)
    context.user_data["state"] = UserStates.Current_Contribution_Waiting_Type
    await query.answer()


async def current_contribution_parts_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    user_id = chat_id
    booked_parts = await db.get_booked_parts_by_user(user_id=user_id)
    booked_parts = sorted(booked_parts, key=cmp_to_key(compare_between_part_asc), reverse=False)
    current_contribution_parts_message_text = Text.create_current_contribution_parts_explain_text()
    current_contribution_parts_message_keyboard = InlineKeyboardMarkup(await
                                                                       Keyboards.get_current_contributions_booked_parts_keyboard(
                                                                           booked_parts=booked_parts))
    try:
        await query.edit_message_text(text=current_contribution_parts_message_text,
                                      reply_markup=current_contribution_parts_message_keyboard,
                                      parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(e)
        await query.answer()


async def current_contribution_khatmas_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    user_id = chat_id
    data = query.data
    my_khatmas_sort = context.user_data.get(UserOptionsKeys.My_Khatmas_Sort, None)
    if my_khatmas_sort is None:
        my_khatmas_sort = True
        context.user_data[UserOptionsKeys.My_Khatmas_Sort] = True
    if len(data.split("_")) > 2:
        new_sort = (True if data.split("_")[-1] == "1" else False)
        context.user_data[UserOptionsKeys.My_Khatmas_Sort] = new_sort
        my_khatmas_sort = new_sort
    khatmas = await db.get_khatmas_by_user_id(user_id=user_id, sort_asc=my_khatmas_sort)
    current_contribution_parts_message_text = Text.create_my_khatmas_explain_text()
    current_contribution_parts_message_keyboard = InlineKeyboardMarkup(await
                                                                       Keyboards.get_my_khatmas_list_keyboard(
                                                                           khatma_list=khatmas,
                                                                           sort_asc=my_khatmas_sort))
    try:
        await query.edit_message_text(text=current_contribution_parts_message_text,
                                      reply_markup=current_contribution_parts_message_keyboard,
                                      parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(e)
        await query.answer()


async def options_khatma_part_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    part_id = data.split("_")[2]
    part_id = int(part_id)
    part_data = await db.get_khatma_part_data_by_id(part_id=part_id)
    if part_data is None:
        await query.answer(Text.Khatma_Part_Not_Found, show_alert=True)
    await query.answer()
    khatma_data = part_data.Khatma
    booked_since_total_time = (datetime.utcnow() - part_data.part_start).total_seconds()
    deadline_total_time = (part_data.part_deadline - datetime.utcnow()).total_seconds()
    options_khatma_part_explain_message_text = Text.create_khatma_part_details_text(khatma_id=khatma_data.id,
                                                                                    name=khatma_data.name_of_opener,
                                                                                    intention=khatma_data.description,
                                                                                    part_no=part_data.part_no,
                                                                                    booked_since_total_time=booked_since_total_time,
                                                                                    deadline_total_time=deadline_total_time)
    options_khatma_part_explain_message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_khatma_part_details_keyboard(part_id=part_id, user_id=chat_id))
    try:
        await query.edit_message_text(text=options_khatma_part_explain_message_text,
                                      reply_markup=options_khatma_part_explain_message_keyboard)
    except Exception as e:
        logging.error(e)


async def mark_part_as_cancel_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    part_id = data.split("_")[2]
    part_id = int(part_id)
    result = await db.mark_khatma_part_as_cancel_by_part_id(part_id=part_id, user_id=chat_id)
    if not result:
        await query.answer(Text.Unknown_Error_Text, show_alert=True)
        return
    await query.answer(Text.Mark_Khatma_Part_As_Cancel_Text, show_alert=True)
    user_id = chat_id
    booked_parts = await db.get_booked_parts_by_user(user_id=user_id)
    booked_parts = sorted(booked_parts, key=cmp_to_key(compare_between_part_asc), reverse=False)
    current_contribution_parts_message_text = Text.create_current_contribution_parts_explain_text()
    current_contribution_parts_message_keyboard = InlineKeyboardMarkup(await
                                                                       Keyboards.get_current_contributions_booked_parts_keyboard(
                                                                           booked_parts=booked_parts))
    try:
        await query.edit_message_text(text=current_contribution_parts_message_text,
                                      reply_markup=current_contribution_parts_message_keyboard,
                                      parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(e)


async def mark_part_as_done_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    part_id = data.split("_")[2]
    part_id = int(part_id)
    khatma_part_data = await db.get_khatma_part_data_by_id(part_id=part_id)
    time_since_start_in_second = (datetime.utcnow() - khatma_part_data.part_start).total_seconds()
    if time_since_start_in_second < 1200:
        await query.answer(text=Text.Mark_Part_As_Done_Time_Limit, show_alert=True)
        return
    result = await db.mark_khatma_part_as_done_by_part_id(part_id=part_id, user_id=chat_id)
    khatma_data = await db.get_khatma_data_by_part_id(part_id=part_id)
    if not result:
        await query.answer(Text.Unknown_Error_Text, show_alert=True)
        return
    await query.answer(Text.Mark_Khatma_Part_As_Done_Text, show_alert=True)
    finished_parts_dict = await db.check_if_khatma_done(khatma_id=khatma_data.id)
    user_id = chat_id
    booked_parts = await db.get_booked_parts_by_user(user_id=user_id)
    booked_parts = sorted(booked_parts, key=cmp_to_key(compare_between_part_asc), reverse=False)
    current_contribution_parts_message_text = Text.create_current_contribution_parts_explain_text()
    current_contribution_parts_message_keyboard = InlineKeyboardMarkup(await
                                                                       Keyboards.get_current_contributions_booked_parts_keyboard(
                                                                           booked_parts=booked_parts))
    try:
        await query.edit_message_text(text=current_contribution_parts_message_text,
                                      reply_markup=current_contribution_parts_message_keyboard,
                                      parse_mode="MarkdownV2")
    except Exception as e:
        logging.error(e)
    if finished_parts_dict is not None:
        await send_completed_message_to_users(finished_parts_dict=finished_parts_dict,
                                              khatma_opener_user_id=khatma_data.user_id, context=context)


async def time_remaining_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data.split("_")
    total_seconds = data[1]
    time_text = "بقي لك: "
    time_text += format_timespan_in_arabic(total_time=total_seconds, max_units=2)
    time_text += " ⏳"
    time_text += "."
    await query.answer(time_text)
