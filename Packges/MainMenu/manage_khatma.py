import logging
from datetime import datetime

from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from Database import db
from Packges.Brodcast import send_completed_message_to_users, send_canceled_khatma_message_to_users
from Startup.Keyboards import Keyboards
from Startup.KhatmaPartStatus import KhatmaPartStatus
from Startup.KhatmaStatus import KhatmaStatus
from Startup.Text import Text
from Startup.UserStates import UserStates


async def manage_khatma_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                               intention=khatma_data.description,
                                               duration_in_days=0,
                                               start_date=khatma_data.start_date,
                                               end_date=khatma_data.end_date,
                                               is_canceled=False,
                                               is_finished=True)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_manage_khatma_keyboard(khatma_id=khatma_id, is_opened=False))
    elif khatma_status == KhatmaStatus.Canceled:
        message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                               intention=khatma_data.description,
                                               duration_in_days=0,
                                               start_date=khatma_data.start_date,
                                               end_date=khatma_data.end_date,
                                               is_canceled=True,
                                               is_finished=False)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_manage_khatma_keyboard(khatma_id=khatma_id, is_opened=False))
    else:
        message_text = Text.create_khatma_info_in_options(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                          intention=khatma_data.description,
                                                          duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                          start_date=khatma_data.time)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_manage_khatma_keyboard(khatma_id=khatma_id, is_opened=True))

    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def manage_khatma_properties_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                               intention=khatma_data.description,
                                               duration_in_days=0,
                                               start_date=khatma_data.start_date,
                                               end_date=khatma_data.end_date,
                                               is_canceled=False,
                                               is_finished=True)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_manage_khatma_properties_keyboard(khatma_id=khatma_id, is_opened=False))
    elif khatma_status == KhatmaStatus.Canceled:
        message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                               intention=khatma_data.description,
                                               duration_in_days=0,
                                               start_date=khatma_data.start_date,
                                               end_date=khatma_data.end_date,
                                               is_canceled=True,
                                               is_finished=False)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_manage_khatma_properties_keyboard(khatma_id=khatma_id, is_opened=False))
    else:
        message_text = Text.create_khatma_info_in_properties_options(khatma_id=khatma_id,
                                                                     name=khatma_data.name_of_opener,
                                                                     intention=khatma_data.description,
                                                                     duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                                     start_date=khatma_data.time)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_manage_khatma_properties_keyboard(khatma_id=khatma_id, is_opened=True))

    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def manage_khatma_update_name_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        await query.answer(text=Text.Khatma_Is_Ended)
        return
    elif khatma_status == KhatmaStatus.Canceled:
        await query.answer(text=Text.Khatma_Is_Canceled)
        return
    else:
        message_text = Text.Please_Enter_New_Opener_Name
        message_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
    try:
        message = await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=message_keyboard)
        context.user_data["state"] = UserStates.Update_Khatma_Waiting_For_Opener_Name
        context.user_data["khatma_id"] = khatma_id
        context.user_data["temp_message_id"] = message.message_id
    except Exception as e:
        logging.error(e)


async def manage_khatma_update_intention_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        await query.answer(text=Text.Khatma_Is_Ended)
        return
    elif khatma_status == KhatmaStatus.Canceled:
        await query.answer(text=Text.Khatma_Is_Canceled)
        return
    else:
        message_text = Text.Please_Enter_New_Intention
        message_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
    try:
        message = await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=message_keyboard)
        context.user_data["state"] = UserStates.Update_Khatma_Waiting_For_Intention
        context.user_data["khatma_id"] = khatma_id
        context.user_data["temp_message_id"] = message.message_id
    except Exception as e:
        logging.error(e)


async def manage_khatma_update_part_duration_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        await query.answer(text=Text.Khatma_Is_Ended)
        return
    elif khatma_status == KhatmaStatus.Canceled:
        await query.answer(text=Text.Khatma_Is_Canceled)
        return
    else:
        message_text = Text.Please_Enter_New_Duration_In_Days
        message_keyboard = InlineKeyboardMarkup(Keyboards.get_cancel_keyboard())
    try:
        message = await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=message_keyboard)
        context.user_data["state"] = UserStates.Update_Khatma_Waiting_For_Part_Duration
        context.user_data["khatma_id"] = khatma_id
        context.user_data["temp_message_id"] = message.message_id
    except Exception as e:
        logging.error(e)


async def manage_khatma_update_type_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        await query.answer(text=Text.Khatma_Is_Ended)
        return
    elif khatma_status == KhatmaStatus.Canceled:
        await query.answer(text=Text.Khatma_Is_Canceled)
        return
    else:
        message_text = Text.Please_Enter_New_Khatma_Type
        message_keyboard = InlineKeyboardMarkup(Keyboards.get_update_khatma_type_keyboard(khatma_id=khatma_id))
    try:
        await context.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=message_keyboard)
        context.user_data["state"] = UserStates.Update_Khatma_Waiting_For_Khatma_Type
    except Exception as e:
        logging.error(e)


async def manage_khatma_update_type_to_private_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    result = await db.update_khatma_type(khatma_id=khatma_id, is_private=True)
    await query.delete_message()
    if result:
        await context.bot.send_message(chat_id=chat_id, text=Text.Update_Khatma_Info_Done)
    else:
        await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)
    context.user_data["state"] = UserStates.Nothing


async def manage_khatma_update_type_to_public_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    result = await db.update_khatma_type(khatma_id=khatma_id, is_private=False)
    await query.delete_message()
    if result:
        await context.bot.send_message(chat_id=chat_id, text=Text.Update_Khatma_Info_Done)
    else:
        await context.bot.send_message(chat_id=chat_id, text=Text.Unknown_Error_Text)
    context.user_data["state"] = UserStates.Nothing


async def manage_khatma_parts_options_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(text=Text.Khatma_Not_Found)
        return
    elif khatma_status == KhatmaStatus.Done:
        message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                               intention=khatma_data.description,
                                               duration_in_days=0,
                                               start_date=khatma_data.start_date,
                                               end_date=khatma_data.end_date,
                                               is_canceled=False,
                                               is_finished=True)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                        is_opened=False))
    elif khatma_status == KhatmaStatus.Canceled:
        message_text = Text.create_khatma_info(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                               intention=khatma_data.description,
                                               duration_in_days=0,
                                               start_date=khatma_data.start_date,
                                               end_date=khatma_data.end_date,
                                               is_canceled=True,
                                               is_finished=False)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                        is_opened=False))
    else:
        message_text = Text.create_khatma_info_parts_options(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                             intention=khatma_data.description,
                                                             duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                             start_date=khatma_data.time)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                        is_opened=True))

    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def manage_khatma_part_option_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    part_no = data.split("_")[2]
    khatma_id = int(khatma_id)
    part_no = int(part_no)
    khatma_part_data = await db.get_khatma_part_data(khatma_id=khatma_id, part_no=part_no)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    await query.answer()
    if khatma_part_data.part_state == KhatmaPartStatus.Opened:
        message_text = Text.create_khatma_part_options_text_opened(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                                   intention=khatma_data.description, part_no=part_no)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_khatma_part_options_opened_keyboard(khatma_id=khatma_id, part_no=part_no))
    elif khatma_part_data.part_state == KhatmaPartStatus.Done:
        booked_user_fullname = (await db.get_user_data(telegram_id=khatma_part_data.user_id)).telegram_fullname
        ended_since_total_time = (datetime.utcnow() - khatma_part_data.part_end).total_seconds()
        message_text = Text.create_khatma_part_options_text_done(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                                 intention=khatma_data.description, part_no=part_no,
                                                                 booked_user_id=khatma_part_data.user_id,
                                                                 booked_user_fullname=booked_user_fullname,
                                                                 ended_since_total_time=ended_since_total_time,
                                                                 )
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_khatma_part_options_done_keyboard(khatma_id=khatma_id, part_no=part_no))
    else:
        booked_since_total_time = (datetime.utcnow() - khatma_part_data.part_start).total_seconds()
        deadline_total_time = (khatma_part_data.part_deadline - datetime.utcnow()).total_seconds()
        booked_user_fullname = (await db.get_user_data(telegram_id=khatma_part_data.user_id)).telegram_fullname
        message_text = Text.create_khatma_part_options_text_occupied(khatma_id=khatma_id,
                                                                     name=khatma_data.name_of_opener,
                                                                     intention=khatma_data.description, part_no=part_no,
                                                                     booked_user_id=khatma_part_data.user_id,
                                                                     booked_user_fullname=booked_user_fullname,
                                                                     booked_since_total_time=booked_since_total_time,
                                                                     deadline_total_time=deadline_total_time)
        message_keyboard = InlineKeyboardMarkup(
            Keyboards.get_khatma_part_options_occupied_keyboard(khatma_id=khatma_id, part_no=part_no))
    await query.edit_message_text(text=message_text, reply_markup=message_keyboard, parse_mode=ParseMode.HTML)


async def mark_part_as_occupied_by_admin_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[2]
    khatma_id = int(khatma_id)
    part_no = data.split("_")[3]
    part_no = int(part_no)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    khatma_part_data = await db.book_khatma_part(khatma_id=khatma_id, part_no=part_no, user_id=chat_id,
                                                 duration_in_days=khatma_data.number_of_days_to_finish_a_part)
    if khatma_part_data is not None:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    await query.answer(Text.Khatma_Part_Occupied_Done)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    message_text = Text.create_khatma_info_parts_options(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                         intention=khatma_data.description,
                                                         duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                         start_date=khatma_data.time)
    message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                    is_opened=True))

    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def mark_part_as_cancel_occupied_by_admin_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[2]
    khatma_id = int(khatma_id)
    part_no = data.split("_")[3]
    part_no = int(part_no)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    user_id = await db.mark_khatma_part_as_cancel_by_admin(khatma_id=khatma_id, part_no=part_no)
    if user_id is None:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    await query.answer(Text.Mark_Khatma_Part_As_Cancel_Text)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    message_text = Text.create_khatma_info_parts_options(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                         intention=khatma_data.description,
                                                         duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                         start_date=khatma_data.time)
    message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                    is_opened=True))
    message_text_for_user = Text.create_cancel_khatma_part_by_admin_text(khatma_id=khatma_id,
                                                                         khatma_opener_name=khatma_data.name_of_opener,
                                                                         part_no=part_no)
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)

    try:
        await context.bot.send_message(chat_id=user_id, text=message_text_for_user)
    except Exception as e:
        logging.error(e)


async def mark_part_as_done_by_admin_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[2]
    khatma_id = int(khatma_id)
    part_no = data.split("_")[3]
    part_no = int(part_no)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    user_id = await db.mark_khatma_part_as_done_by_admin(khatma_id=khatma_id, part_no=part_no)
    if user_id is None:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    await query.answer(Text.Khatma_Part_Done_By_Admin)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    message_text = Text.create_khatma_info_parts_options(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                         intention=khatma_data.description,
                                                         duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                         start_date=khatma_data.time)
    message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                    is_opened=True))
    message_text_for_user = Text.create_done_khatma_part_by_admin_text(khatma_id=khatma_id,
                                                                       khatma_opener_name=khatma_data.name_of_opener,
                                                                       part_no=part_no)
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)

    try:
        await context.bot.send_message(chat_id=user_id, text=message_text_for_user)
    except Exception as e:
        logging.error(e)
    finished_parts_dict = await db.check_if_khatma_done(khatma_id=khatma_id)
    if finished_parts_dict is not None:
        await send_completed_message_to_users(finished_parts_dict=finished_parts_dict,
                                              khatma_opener_user_id=khatma_data.user_id
                                              , context=context)


async def mark_part_as_cancel_read_by_admin_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[2]
    khatma_id = int(khatma_id)
    part_no = data.split("_")[3]
    part_no = int(part_no)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    user_id = await db.mark_khatma_part_as_cancel_by_admin(khatma_id=khatma_id, part_no=part_no)
    if user_id is None:
        await query.answer(Text.Khatma_Part_Not_Found)
        return
    await query.answer(Text.Mark_Khatma_Part_As_Cancel_Read_Text)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    message_text = Text.create_khatma_info_parts_options(khatma_id=khatma_id, name=khatma_data.name_of_opener,
                                                         intention=khatma_data.description,
                                                         duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                         start_date=khatma_data.time)
    message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_khatma_parts_options_keyboard(khatma_id=khatma_id, khatma_parts=khatma_parts_data,
                                                    is_opened=True))
    message_text_for_user = Text.create_cancel_read_khatma_part_by_admin_text(khatma_id=khatma_id,
                                                                              khatma_opener_name=khatma_data.name_of_opener,
                                                                              part_no=part_no)
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)

    try:
        await context.bot.send_message(chat_id=user_id, text=message_text_for_user)
    except Exception as e:
        logging.error(e)


async def mark_khatma_as_cancel_by_admin_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Is_Ended)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Is_Canceled)
        return
    message_text = Text.create_khatma_info_in_cancel_khatma_confirmation(khatma_id=khatma_id,
                                                                         name=khatma_data.name_of_opener,
                                                                         intention=khatma_data.description,
                                                                         duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                                         start_date=khatma_data.time)
    message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_mark_khatma_as_canceled_by_admin_confirmation(khatma_id=khatma_id))
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def mark_khatma_as_cancel_by_admin_confirmed_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Is_Ended)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Is_Canceled)
        return
    parts_dict = await db.mark_khatma_as_canceled_by_admin(khatma_id=khatma_id)

    message_text = Text.Welcome
    message_keyboard = InlineKeyboardMarkup(Keyboards.get_main_inline_keyboard())
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)

    await send_canceled_khatma_message_to_users(parts_dict=parts_dict, khatma_opener_user_id=khatma_data.user_id
                                                , context=context)


async def mark_khatma_as_done_by_admin_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Is_Ended)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Is_Canceled)
        return
    message_text = Text.create_khatma_info_in_read_khatma_confirmation(khatma_id=khatma_id,
                                                                       name=khatma_data.name_of_opener,
                                                                       intention=khatma_data.description,
                                                                       duration_in_days=khatma_data.number_of_days_to_finish_a_part,
                                                                       start_date=khatma_data.time)
    message_keyboard = InlineKeyboardMarkup(
        Keyboards.get_mark_khatma_as_done_by_admin_confirmation(khatma_id=khatma_id))
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


async def mark_khatma_as_done_by_admin_confirmed_pressed(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.from_user.id
    data = query.data
    khatma_id = data.split("_")[1]
    khatma_id = int(khatma_id)
    khatma_status, khatma_data, khatma_parts_data = await db.get_khatma_with_parts_data(khatma_id=khatma_id)
    if khatma_status == KhatmaStatus.Done:
        await query.answer(Text.Khatma_Is_Ended)
        return
    if khatma_status == KhatmaStatus.Not_Found:
        await query.answer(Text.Khatma_Not_Found)
        return
    if khatma_status == KhatmaStatus.Canceled:
        await query.answer(Text.Khatma_Is_Canceled)
        return
    parts_dict = await db.mark_khatma_as_done_by_admin(khatma_id=khatma_id)
    message_text = Text.Welcome
    message_keyboard = InlineKeyboardMarkup(Keyboards.get_main_inline_keyboard())
    try:
        await query.edit_message_text(text=message_text,
                                      reply_markup=message_keyboard,
                                      parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)

    await send_completed_message_to_users(finished_parts_dict=parts_dict, khatma_opener_user_id=khatma_data.user_id
                                          , context=context)
