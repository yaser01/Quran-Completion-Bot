import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.requests import Request

sys.path.append('../')
from Database.db import DATABASE_URI
from Database.models import User, Khatma, Khatma_Done, Khatma_Parts, Khatma_Parts_Done, Quran_File
from Packges.Global_Functions import build_async_db_uri
import sys

sys.path.append('../')  # add ability to import modules from parent folder
async_engine = create_async_engine(build_async_db_uri(DATABASE_URI), echo=False)
app = FastAPI()
load_dotenv()
Admin_Password = os.getenv('ADMIN_PAGE_PASSWORD')
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == "Admin" and password == Admin_Password:
            request.session.update({"token": "..."})
            return True
        else:
            request.session.clear()
            return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


authentication_backend = AdminAuth(secret_key="...")

admin = Admin(app, async_engine, authentication_backend=authentication_backend)


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_list = [User.id, User.telegram_id, User.telegram_fullname, User.telegram_username, User.is_blocked]
    column_details_list = [User.id, User.telegram_id, User.telegram_fullname, User.telegram_username, User.is_blocked,
                           User.Khatma_List]
    column_searchable_list = [User.telegram_id, User.telegram_fullname, User.telegram_username]
    column_export_list = [User.id, User.telegram_id, User.telegram_fullname, User.telegram_username, User.is_blocked]
    column_sortable_list = [User.id]
    page_size = 25
    page_size_options = [25, 50, 100, 200]


class KhatmaAdmin(ModelView, model=Khatma):
    name = "Khatma"
    name_plural = "Khatmas"
    column_list = [Khatma.id, Khatma.User,Khatma.user_id, Khatma.name_of_opener, Khatma.time, Khatma.description,
                   Khatma.number_of_days_to_finish_a_part]
    column_details_list = [Khatma.id, Khatma.User,Khatma.user_id, Khatma.name_of_opener, Khatma.time, Khatma.description,
                           Khatma.number_of_days_to_finish_a_part]
    column_searchable_list = [Khatma.id, Khatma.user_id]
    column_export_list = [Khatma.id, Khatma.User, Khatma.name_of_opener, Khatma.time, Khatma.description,
                          Khatma.number_of_days_to_finish_a_part]
    column_sortable_list = [Khatma.id, Khatma.time, Khatma.number_of_days_to_finish_a_part]
    form_excluded_columns = [Khatma.is_private, Khatma.max_number_of_booked_parts_by_person]
    column_labels = {Khatma.time: "Start time"}
    column_formatters = {Khatma.time: lambda m, a: str(m.time)[:str(m.time).find(".")]}
    page_size = 25
    page_size_options = [25, 50, 100, 200]


class KhatmaDoneAdmin(ModelView, model=Khatma_Done):
    name = "Khatma Done"
    name_plural = "Khatmas Done"
    column_list = [Khatma_Done.id, Khatma_Done.User, Khatma_Done.name_of_opener, Khatma_Done.start_date,
                   Khatma_Done.end_date,
                   Khatma_Done.is_canceled, Khatma_Done.description]
    column_searchable_list = [Khatma_Done.user_id, Khatma_Done.id]
    column_formatters = {Khatma_Done.start_date: lambda m, a: str(m.start_date)[:str(m.start_date).find(".")],
                         Khatma_Done.end_date: lambda m, a: str(m.end_date)[:str(m.end_date).find(".")]}
    column_sortable_list = [Khatma.id, Khatma.time, Khatma.number_of_days_to_finish_a_part]
    page_size = 25
    page_size_options = [25, 50, 100, 200]


def part_state_formatter(m, a):
    if m.part_state == 0:
        return "Opened"
    elif m.part_state == 1:
        return "Taken"
    else:
        return "Done"


class KhatmaPartsAdmin(ModelView, model=Khatma_Parts):
    name = "Khatma Part"
    name_plural = "Khatma Parts"
    column_list = [Khatma_Parts.Khatma, Khatma_Parts.part_no, Khatma_Parts.User, Khatma_Parts.part_state,
                   Khatma_Parts.part_start, Khatma_Parts.part_end, Khatma_Parts.part_deadline,
                   Khatma_Parts.part_next_notification_time]
    column_searchable_list = [Khatma_Parts.khatma_id, Khatma_Parts.part_no, Khatma_Parts.user_id]
    column_formatters = {
        Khatma_Parts.part_start: lambda m, a: str(m.part_start)[:str(m.part_start).find(".")] if str(m.part_start)[:str(
            m.part_start).find(".")] != "Non" else "",
        Khatma_Parts.part_end: lambda m, a: str(m.part_end)[:str(m.part_end).find(".")] if str(m.part_end)[
                                                                                           :str(m.part_end).find(
                                                                                               ".")] != "Non" else "",
        Khatma_Parts.part_deadline: lambda m, a: str(m.part_deadline)[:str(m.part_deadline).find(".")] if str(
            m.part_deadline)[:str(m.part_deadline).find(".")] != "Non" else "",
        Khatma_Parts.part_next_notification_time: lambda m, a: str(m.part_next_notification_time)[:str(
            m.part_next_notification_time).find(".")] if str(m.part_next_notification_time)[
                                                         :str(m.part_next_notification_time).find(
                                                             ".")] != "Non" else "",
        Khatma_Parts.part_state: part_state_formatter
    }
    column_sortable_list = [Khatma_Parts.Khatma, Khatma_Parts.User, Khatma_Parts.part_state,
                            Khatma_Parts.part_start, Khatma_Parts.part_end, Khatma_Parts.part_deadline,
                            Khatma_Parts.part_next_notification_time]
    page_size = 25
    page_size_options = [25, 50, 100, 200]


class KhatmaPartsDoneAdmin(ModelView, model=Khatma_Parts_Done):
    name = "Khatma Part Done"
    name_plural = "Khatma Parts Done"
    column_list = [Khatma_Parts_Done.Khatma_Done, Khatma_Parts_Done.part_no, Khatma_Parts_Done.User,
                   Khatma_Parts.part_state,
                   Khatma_Parts.part_start, Khatma_Parts.part_end]
    column_searchable_list = [Khatma_Parts_Done.khatma_id, Khatma_Parts_Done.part_no, Khatma_Parts_Done.user_id]
    column_formatters = {
        Khatma_Parts_Done.part_start: lambda m, a: str(m.part_start)[:str(m.part_start).find(".")] if str(m.part_start)[
                                                                                                      :str(
                                                                                                          m.part_start).find(
                                                                                                          ".")] != "Non" else "",
        Khatma_Parts_Done.part_end: lambda m, a: str(m.part_end)[:str(m.part_end).find(".")] if str(m.part_end)[
                                                                                                :str(m.part_end).find(
                                                                                                    ".")] != "Non" else "",
    }
    column_sortable_list = [Khatma_Parts_Done.Khatma_Done, Khatma_Parts_Done.User,
                            Khatma_Parts_Done.part_start, Khatma_Parts_Done.part_end]
    page_size = 25
    page_size_options = [25, 50, 100, 200]


class QuranFileAdmin(ModelView, model=Quran_File):
    name = "Quran File"
    name_plural = "Quran Files"
    column_list = [Quran_File.file_id, Quran_File.telegram_file_id]
    column_searchable_list = [Quran_File.file_id, Quran_File.telegram_file_id]
    column_sortable_list = [Quran_File.file_id]
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    can_create = True
    form_include_pk = True


admin.add_view(UserAdmin)
admin.add_view(KhatmaAdmin)
admin.add_view(KhatmaDoneAdmin)
admin.add_view(KhatmaPartsAdmin)
admin.add_view(KhatmaPartsDoneAdmin)
admin.add_view(QuranFileAdmin)
