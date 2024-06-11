import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from typing import List, Type

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from Database.models import Base, User, Khatma, Khatma_Parts, Khatma_Done, Khatma_Parts_Done, Quran_File
from Entites.ExpiredPart import ExpiredPart
from Entites.NotificationPart import NotificationPart
from Entites.PartData import PartData
from Entites.TelegramUser import TelegramUser
from Startup.Global_Files import Logs_Folder
from Packges.Global_Functions import build_async_db_uri, calc_next_notification_time
from Startup.KhatmaPartStatus import KhatmaPartStatus
from Startup.KhatmaStatus import KhatmaStatus

load_dotenv()
DATABASE_URI = os.getenv('DATABASE_URI')
DATABASE_BACKUP_URI = os.getenv('DATABASE_BACKUP_URI')
from sqlalchemy_utils import database_exists, create_database

TELEGRAM_FILES_IDS = {}


def add_backup_request():
    try:
        rq = requests.get(url=DATABASE_BACKUP_URI)
    except Exception as e:
        logging.error(e)


def init_database_logger():
    database_logger = logging.getLogger('sqlalchemy.engine')
    database_logger.setLevel(logging.DEBUG)
    database_handler = TimedRotatingFileHandler(filename=os.path.join(Logs_Folder, "database_log.log"),
                                                encoding="UTF-8",
                                                when='D',
                                                interval=3, backupCount=4, delay=False, utc=True)
    database_logger_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    database_handler.setFormatter(database_logger_formatter)
    database_logger.addHandler(database_handler)
    database_logger.propagate = False


async def init_database():
    async_engine = create_async_engine(build_async_db_uri(DATABASE_URI), echo=False)
    sync_engine = create_engine(DATABASE_URI, echo=False)
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def db_session():
    """ Creates a context with an open SQLAlchemy session."""
    async_engine = create_async_engine(build_async_db_uri(DATABASE_URI), echo=False)
    connection = await async_engine.connect()
    async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)()
    await async_session.begin()
    try:
        yield async_session
        await async_session.flush()
        await async_session.commit()
    except SQLAlchemyError as e:
        error = str(e.__cause__)
        logging.error(e)
        await async_session.rollback()
    await async_session.close()
    await connection.close()


async def insert_new_user(telegram_user: TelegramUser):
    async with db_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == int(telegram_user.id)))).scalars().first()
        if user is not None:
            user.telegram_username = telegram_user.username
            user.telegram_fullname = telegram_user.fullname
            return user.is_blocked
        users_count = (await session.execute(select(func.count(User.telegram_id)))).scalar()
        user = User(telegram_id=telegram_user.id, telegram_username=telegram_user.username,
                    telegram_fullname=telegram_user.fullname)
        session.add(user)
        return False


async def get_user_data(telegram_id) -> User:
    async with db_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == int(telegram_id)))).scalars().first()
        session.expunge(user)
    return user


async def get_all_users_data() -> List[Type[User]]:
    async with db_session() as session:
        users = (await session.execute(select(User))).scalars().all()
    return users


async def create_new_khatma(telegram_id, description, name_of_opener, time, number_of_days_to_finish_a_part
                            , is_private=False, max_number_of_parts=2):
    async with db_session() as session:
        New_Khatma = Khatma(user_id=telegram_id, name_of_opener=name_of_opener,
                            description=description, max_number_of_booked_parts_by_person=max_number_of_parts,
                            number_of_days_to_finish_a_part=number_of_days_to_finish_a_part, time=time,
                            is_private=is_private)
        session.add(New_Khatma)
        await session.commit()
        await session.refresh(New_Khatma)
        khatma_id = New_Khatma.id
        for i in range(1, 31):
            New_Khatma_Part = Khatma_Parts(khatma_id=khatma_id, part_no=i,
                                           part_state=KhatmaPartStatus.Opened)
            session.add(New_Khatma_Part)
        return khatma_id


async def get_khatma_public_list(sort_by_date="asc", page_id=0, page_size=7):
    async with db_session() as session:
        if sort_by_date == "asc":
            khatma_list = (
                await session.execute(select(Khatma).where(Khatma.is_private == False).order_by(Khatma.time.asc())
                                      .limit(page_size)
                                      .offset(page_id * page_size))
            ).scalars().all()
        else:
            khatma_list = (
                await session.execute(select(Khatma).where(Khatma.is_private == False).order_by(Khatma.time.desc())
                                      .limit(page_size)
                                      .offset(page_id * page_size))
            ).scalars().all()
    return khatma_list


async def get_khatmas_by_user_id(user_id, sort_asc=True):
    async with db_session() as session:
        query = select(Khatma).where(Khatma.user_id == int(user_id))
        if sort_asc:
            query = query.order_by(Khatma.time.asc())
        else:
            query = query.order_by(Khatma.time.desc())
        khatmas = (await session.execute(query)).scalars().all()
        return khatmas


async def count_number_of_finished_parts_of_khatma(khatma_id):
    async with db_session() as session:
        all_parts_count = (await session.execute(
            select(func.count(Khatma_Parts.part_id)).where(Khatma_Parts.khatma_id == int(khatma_id)))).scalar()
        finished_parts_count = (await session.execute(
            select(func.count(Khatma_Parts.part_id)).where(Khatma_Parts.khatma_id == int(khatma_id),
                                                           Khatma_Parts.part_state == int(
                                                               KhatmaPartStatus.Done)))).scalar()
        if all_parts_count == 0:
            return 30
        return finished_parts_count


async def count_number_of_public_khatmas():
    async with db_session() as session:
        number_of_public_khatmas = (await session.execute(
            select(func.count(Khatma.id)))).scalar()
        return number_of_public_khatmas


async def get_khatma_with_parts_data(khatma_id):
    async with db_session() as session:
        khatma = (await session.execute(select(Khatma).where(Khatma.id == int(khatma_id)))).scalar()
        if khatma is not None:
            session.expunge(khatma)
            khatma_parts = (await session.execute(select(Khatma_Parts).where(Khatma_Parts.khatma_id == int(khatma_id))
                                                  .order_by(Khatma_Parts.part_no))).scalars().all()
            for khatma_part_id in range(len(khatma_parts)):
                session.expunge(khatma_parts[khatma_part_id])
            return KhatmaStatus.Opened, khatma, khatma_parts
        else:
            khatma = (await session.execute(select(Khatma_Done).where(Khatma_Done.id == int(khatma_id)))).scalar()
            if khatma is not None:
                session.expunge(khatma)
                khatma_parts = (
                    await session.execute(select(Khatma_Parts_Done).where(Khatma_Parts_Done.khatma_id == int(khatma_id))
                                          .order_by(Khatma_Parts_Done.part_no))).scalars().all()
                if khatma.is_canceled:
                    return KhatmaStatus.Canceled, khatma, khatma_parts
                else:
                    return KhatmaStatus.Done, khatma, khatma_parts
            return KhatmaStatus.Not_Found, None, None


async def get_khatma_part_data(khatma_id, part_no) -> Khatma_Parts:
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.khatma_id == int(khatma_id),
                                                        Khatma_Parts.part_no == int(part_no))
                                                  .order_by(Khatma_Parts.part_no))).scalar()
        session.expunge(khatma_part_data)
    return khatma_part_data


async def get_khatma_part_data_by_id(part_id) -> Khatma_Parts:
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.part_id == int(part_id)))).scalar()
        if khatma_part_data is None:
            return None
        session.expunge(khatma_part_data)
    return khatma_part_data


async def get_number_of_booked_parts_by_user(user_id):
    async with db_session() as session:
        count = (await session.execute(select(func.count(Khatma_Parts.part_id)).
                                       where(Khatma_Parts.user_id == int(user_id),
                                             Khatma_Parts.part_state == int(KhatmaPartStatus.Occupied)))).scalar()
        return count


async def count_number_of_currently_opened_khatmas_by_user(user_id):
    async with db_session() as session:
        number_of_currently_opened_khatmas_by_user = (await session.execute(
            select(func.count(Khatma.id)).where(Khatma.user_id == int(user_id)))).scalar()
        return number_of_currently_opened_khatmas_by_user


async def get_booked_parts_by_user(user_id):
    async with db_session() as session:
        booked_parts = (await session.execute(select(Khatma_Parts).
                                              where(Khatma_Parts.user_id == int(user_id),
                                                    Khatma_Parts.part_state == int(
                                                        KhatmaPartStatus.Occupied)))).scalars().all()
        for booked_part_id in range(len(booked_parts)):
            session.expunge(booked_parts[booked_part_id])
        return booked_parts


async def cancel_reservation_of_all_expired_booked_parts() -> List[ExpiredPart]:
    time_now = datetime.utcnow()
    dead_parts = []
    async with db_session() as session:
        booked_parts = (await session.execute(select(Khatma_Parts).
                                              where(Khatma_Parts.part_state == int(
            KhatmaPartStatus.Occupied), Khatma_Parts.part_deadline <= time_now))).scalars().all()
        for booked_part in booked_parts:
            dead_parts.append(
                ExpiredPart(telegram_user_id=booked_part.user_id,
                            khatma_id=booked_part.khatma_id,
                            part_no=booked_part.part_no,
                            khatma_opener_name=booked_part.Khatma.name_of_opener,
                            khatma_intention=booked_part.Khatma.description,
                            khatma_part_duration=booked_part.Khatma.number_of_days_to_finish_a_part)
            )
            booked_part.part_state = KhatmaPartStatus.Opened
            booked_part.part_end = None
            booked_part.part_deadline = None
            booked_part.part_start = None
            booked_part.part_next_notification_time = None
            booked_part.user_id = None
    return dead_parts


async def get_send_notification_of_booked_parts() -> List[NotificationPart]:
    time_now = datetime.utcnow()
    notification_parts = []
    async with db_session() as session:
        booked_parts = (await session.execute(select(Khatma_Parts).
                                              where(Khatma_Parts.part_state == int(
            KhatmaPartStatus.Occupied), Khatma_Parts.part_next_notification_time <= time_now))).scalars().all()
        for booked_part in booked_parts:
            notification_parts.append(
                NotificationPart(telegram_user_id=booked_part.user_id,
                                 khatma_id=booked_part.khatma_id,
                                 part_no=booked_part.part_no,
                                 khatma_opener_name=booked_part.Khatma.name_of_opener,
                                 khatma_intention=booked_part.Khatma.description,
                                 khatma_part_duration=booked_part.Khatma.number_of_days_to_finish_a_part,
                                 part_deadline=booked_part.part_deadline)
            )
            booked_part.part_next_notification_time = calc_next_notification_time(
                deadline_time=booked_part.part_deadline)
    return notification_parts


async def book_khatma_part(khatma_id, part_no, user_id, duration_in_days):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.khatma_id == int(khatma_id),
                                                        Khatma_Parts.part_no == int(part_no))
                                                  .order_by(Khatma_Parts.part_no))).scalar()
        if khatma_part_data.user_id is None:
            khatma_part_data.user_id = user_id
            khatma_part_data.part_state = KhatmaPartStatus.Occupied
            khatma_part_data.part_start = datetime.utcnow()
            khatma_part_data.part_deadline = datetime.utcnow() + timedelta(days=duration_in_days)
            khatma_part_data.part_next_notification_time = calc_next_notification_time(
                deadline_time=khatma_part_data.part_deadline)
            return None
        else:
            session.expunge(khatma_part_data)
            return khatma_part_data


async def mark_khatma_part_as_done(khatma_id, part_no):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.khatma_id == int(khatma_id),
                                                        Khatma_Parts.part_no == int(part_no))
                                                  .order_by(Khatma_Parts.part_no))).scalar()
        if khatma_part_data.user_id is not None and khatma_part_data.part_state == KhatmaPartStatus.Occupied:
            khatma_part_data.part_state = KhatmaPartStatus.Done
            khatma_part_data.part_end = datetime.utcnow()
            return None
        else:
            session.expunge(khatma_part_data)
            return khatma_part_data


async def mark_khatma_part_as_done_by_part_id(part_id, user_id):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.part_id == int(part_id),
                                                        Khatma_Parts.user_id == int(user_id)))).scalar()
        if khatma_part_data is None:
            return False
        if khatma_part_data.part_state == KhatmaPartStatus.Occupied:
            khatma_part_data.part_state = KhatmaPartStatus.Done
            khatma_part_data.part_end = datetime.utcnow()
            return True
        else:
            return False


async def get_khatma_data_by_part_id(part_id) -> Khatma:
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.part_id == int(part_id)))).scalar()
        if khatma_part_data is None:
            return None
        session.expunge(khatma_part_data)
        return khatma_part_data.Khatma


async def mark_khatma_part_as_cancel_by_part_id(part_id, user_id):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.part_id == int(part_id),
                                                        Khatma_Parts.user_id == int(user_id)))).scalar()
        if khatma_part_data is None:
            return False
        khatma_part_data.part_state = KhatmaPartStatus.Opened
        khatma_part_data.part_end = None
        khatma_part_data.part_deadline = None
        khatma_part_data.part_start = None
        khatma_part_data.part_next_notification_time = None
        khatma_part_data.user_id = None
        return True


async def mark_khatma_part_as_cancel(khatma_id, part_no, user_id):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.khatma_id == int(khatma_id)
                                                        , Khatma_Parts.part_no == int(part_no),
                                                        Khatma_Parts.user_id == int(user_id)))).scalar()
        if khatma_part_data is None:
            return False
        user_id = khatma_part_data.user_id
        khatma_part_data.part_state = KhatmaPartStatus.Opened
        khatma_part_data.part_end = None
        khatma_part_data.part_deadline = None
        khatma_part_data.part_start = None
        khatma_part_data.part_next_notification_time = None
        khatma_part_data.user_id = None
        return True


async def mark_khatma_part_as_cancel_by_admin(khatma_id, part_no):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.khatma_id == int(khatma_id)
                                                        , Khatma_Parts.part_no == int(part_no)))).scalar()
        user_id = khatma_part_data.user_id
        if khatma_part_data is None:
            return None
        if khatma_part_data.user_id is None:
            user_id = None
        khatma_part_data.part_state = KhatmaPartStatus.Opened
        khatma_part_data.part_end = None
        khatma_part_data.part_deadline = None
        khatma_part_data.part_start = None
        khatma_part_data.part_next_notification_time = None
        khatma_part_data.user_id = None
        return user_id


async def mark_khatma_part_as_done_by_admin(khatma_id, part_no):
    async with db_session() as session:
        khatma_part_data = (await session.execute(select(Khatma_Parts).
                                                  where(Khatma_Parts.khatma_id == int(khatma_id)
                                                        , Khatma_Parts.part_no == int(part_no)))).scalar()
        user_id = khatma_part_data.user_id
        if khatma_part_data is None:
            return None
        if khatma_part_data.user_id is None:
            return None
        khatma_part_data.part_state = KhatmaPartStatus.Done
        khatma_part_data.part_end = datetime.utcnow()
        return user_id


async def check_if_khatma_done(khatma_id):
    async with db_session() as session:
        khatma_parts = (await session.execute(select(Khatma_Parts).
        where(Khatma_Parts.khatma_id == int(khatma_id),
              Khatma_Parts.part_state == int(
                  KhatmaPartStatus.Done)).order_by(
            Khatma_Parts.part_no))).scalars().all()
        if len(khatma_parts) == 30:
            finished_parts_dict = {}
            khatma = (await session.execute(select(Khatma).where(Khatma.id == int(khatma_id)))).scalar()
            new_khatma_done = Khatma_Done(id=khatma.id,
                                          user_id=khatma.user_id,
                                          name_of_opener=khatma.name_of_opener,
                                          description=khatma.description,
                                          start_date=khatma.time,
                                          end_date=datetime.utcnow(),
                                          is_canceled=False)
            session.add(new_khatma_done)
            for khatma_part in khatma_parts:
                if khatma_part.user_id in finished_parts_dict.keys():
                    finished_parts_dict[khatma_part.user_id].append(
                        PartData(
                            khatma_id=khatma_id,
                            part_no=khatma_part.part_no,
                            khatma_opener_name=khatma.name_of_opener,
                            khatma_intention=khatma.description,
                            part_state=khatma_part.part_state
                        )
                    )
                else:
                    finished_parts_dict[khatma_part.user_id] = [
                        PartData(
                            khatma_id=khatma_id,
                            part_no=khatma_part.part_no,
                            khatma_opener_name=khatma.name_of_opener,
                            khatma_intention=khatma.description,
                            part_state=khatma_part.part_state
                        )
                    ]
                new_done_part = Khatma_Parts_Done(
                    part_id=khatma_part.part_id,
                    khatma_id=khatma_part.khatma_id,
                    part_no=khatma_part.part_no,
                    user_id=khatma_part.user_id,
                    part_start=khatma_part.part_start,
                    part_end=khatma_part.part_end
                )
                session.add(new_done_part)
                await session.delete(khatma_part)
            await session.delete(khatma)
            return finished_parts_dict
        else:
            return None


async def update_khatma_opener_name(khatma_id, new_opener_name) -> bool:
    async with db_session() as session:
        khatma_data = (await session.execute(select(Khatma).
                                             where(Khatma.id == int(khatma_id)))).scalar()
        if khatma_data is None:
            return False
        khatma_data.name_of_opener = new_opener_name
        return True


async def update_khatma_intention(khatma_id, new_intention) -> bool:
    async with db_session() as session:
        khatma_data = (await session.execute(select(Khatma).
                                             where(Khatma.id == int(khatma_id)))).scalar()
        if khatma_data is None:
            return False
        khatma_data.description = new_intention
        return True


async def update_khatma_type(khatma_id, is_private) -> bool:
    async with db_session() as session:
        khatma_data = (await session.execute(select(Khatma).
                                             where(Khatma.id == int(khatma_id)))).scalar()
        if khatma_data is None:
            return False
        khatma_data.is_private = is_private
        return True


async def update_quran_file_link(file_id, telegram_file_id):
    async with db_session() as session:
        quran_file_data = (await session.execute(select(Quran_File).
                                                 where(Quran_File.file_id == int(file_id)))).scalar()
        if quran_file_data is not None:
            quran_file_data.telegram_file_id = telegram_file_id
            return True
        quran_file_new = Quran_File(file_id=int(file_id), telegram_file_id=telegram_file_id)
        session.add(quran_file_new)
        return True


def calc_file_id_with_page_no(page_no, book_id):
    return page_no + 1000 * book_id


def calc_file_id_with_chapter_no(chapter_no, book_id):
    return (chapter_no + 700) + (1000 * book_id)


def calc_file_id_with_book_id(book_id):
    return 800 + (1000 * book_id)


async def get_quran_page_link(page_no, book_id):
    file_id_in_db = calc_file_id_with_page_no(page_no, book_id)
    cached_file_id = TELEGRAM_FILES_IDS.get(file_id_in_db, None)
    if cached_file_id is not None:
        return cached_file_id
    async with db_session() as session:
        quran_file_data = (await session.execute(select(Quran_File).
                                                 where(Quran_File.file_id == int(file_id_in_db)))).scalar()
        if quran_file_data is None:
            return None
        TELEGRAM_FILES_IDS[file_id_in_db] = quran_file_data.telegram_file_id
        return quran_file_data.telegram_file_id


async def get_quran_chapter_link(chapter_no, book_id):
    file_id_in_db = calc_file_id_with_chapter_no(chapter_no, book_id)
    cached_file_id = TELEGRAM_FILES_IDS.get(file_id_in_db, None)
    if cached_file_id is not None:
        return cached_file_id
    async with db_session() as session:
        quran_file_data = (await session.execute(select(Quran_File).
                                                 where(Quran_File.file_id == int(file_id_in_db)))).scalar()
        if quran_file_data is None:
            return None
        TELEGRAM_FILES_IDS[file_id_in_db] = quran_file_data.telegram_file_id
        return quran_file_data.telegram_file_id


async def get_quran_book_link(book_id):
    file_id_in_db = calc_file_id_with_book_id(book_id)
    cached_file_id = TELEGRAM_FILES_IDS.get(file_id_in_db, None)
    if cached_file_id is not None:
        return cached_file_id
    async with db_session() as session:
        quran_file_data = (await session.execute(select(Quran_File).
                                                 where(Quran_File.file_id == int(file_id_in_db)))).scalar()
        if quran_file_data is None:
            return None
        TELEGRAM_FILES_IDS[file_id_in_db] = quran_file_data.telegram_file_id
        return quran_file_data.telegram_file_id


async def update_khatma_reservation_part_duration(khatma_id, new_reservation_part_duration) -> bool:
    async with db_session() as session:
        khatma_data = (await session.execute(select(Khatma).
                                             where(Khatma.id == int(khatma_id)))).scalar()
        if khatma_data is None:
            return False
        khatma_data.number_of_days_to_finish_a_part = new_reservation_part_duration
        khatma_parts = (await session.execute(select(Khatma_Parts).where(Khatma_Parts.khatma_id == int(khatma_id))
                                              .order_by(Khatma_Parts.part_no))).scalars().all()
        for khatma_part in khatma_parts:
            if khatma_part.part_state == KhatmaPartStatus.Occupied:
                khatma_part.part_deadline = khatma_part.part_start + timedelta(days=new_reservation_part_duration)
                khatma_part.part_next_notification_time = calc_next_notification_time(
                    deadline_time=khatma_part.part_deadline)
        return True


async def mark_khatma_as_done_by_admin(khatma_id):
    async with db_session() as session:
        khatma_parts = (await session.execute(select(Khatma_Parts).
        where(Khatma_Parts.khatma_id == int(khatma_id)).order_by(
            Khatma_Parts.part_no))).scalars().all()
        parts_dict = {}
        khatma = (await session.execute(select(Khatma).where(Khatma.id == int(khatma_id)))).scalar()
        new_khatma_done = Khatma_Done(id=khatma.id,
                                      user_id=khatma.user_id,
                                      name_of_opener=khatma.name_of_opener,
                                      description=khatma.description,
                                      start_date=khatma.time,
                                      end_date=datetime.utcnow(),
                                      is_canceled=False)
        session.add(new_khatma_done)
        for khatma_part in khatma_parts:
            if khatma_part.part_state == KhatmaPartStatus.Occupied or khatma_part.part_state == KhatmaPartStatus.Done:
                if khatma_part.user_id in parts_dict.keys():
                    parts_dict[khatma_part.user_id].append(
                        PartData(
                            khatma_id=khatma_id,
                            part_no=khatma_part.part_no,
                            khatma_opener_name=khatma.name_of_opener,
                            khatma_intention=khatma.description,
                            part_state=khatma_part.part_state
                        )
                    )
                else:
                    parts_dict[khatma_part.user_id] = [
                        PartData(
                            khatma_id=khatma_id,
                            part_no=khatma_part.part_no,
                            khatma_opener_name=khatma.name_of_opener,
                            khatma_intention=khatma.description,
                            part_state=khatma_part.part_state
                        )
                    ]
            new_done_part = Khatma_Parts_Done(
                part_id=khatma_part.part_id,
                khatma_id=khatma_part.khatma_id,
                part_no=khatma_part.part_no,
                user_id=khatma_part.user_id if khatma_part.user_id is not None else khatma.user_id,
                part_start=khatma_part.part_start,
                part_end=khatma_part.part_end
            )
            session.add(new_done_part)
            await session.delete(khatma_part)
        await session.delete(khatma)
        return parts_dict


async def mark_khatma_as_canceled_by_admin(khatma_id):
    async with db_session() as session:
        khatma_parts = (await session.execute(select(Khatma_Parts).
        where(Khatma_Parts.khatma_id == int(khatma_id)).order_by(
            Khatma_Parts.part_no))).scalars().all()
        parts_dict = {}
        khatma = (await session.execute(select(Khatma).where(Khatma.id == int(khatma_id)))).scalar()
        new_khatma_done = Khatma_Done(id=khatma.id,
                                      user_id=khatma.user_id,
                                      name_of_opener=khatma.name_of_opener,
                                      description=khatma.description,
                                      start_date=khatma.time,
                                      end_date=datetime.utcnow(),
                                      is_canceled=True)
        session.add(new_khatma_done)
        for khatma_part in khatma_parts:
            if khatma_part.part_state == KhatmaPartStatus.Occupied or khatma_part.part_state == KhatmaPartStatus.Done:
                if khatma_part.user_id in parts_dict.keys():
                    parts_dict[khatma_part.user_id].append(
                        PartData(
                            khatma_id=khatma_id,
                            part_no=khatma_part.part_no,
                            khatma_opener_name=khatma.name_of_opener,
                            khatma_intention=khatma.description,
                            part_state=khatma_part.part_state
                        )
                    )
                else:
                    parts_dict[khatma_part.user_id] = [
                        PartData(
                            khatma_id=khatma_id,
                            part_no=khatma_part.part_no,
                            khatma_opener_name=khatma.name_of_opener,
                            khatma_intention=khatma.description,
                            part_state=khatma_part.part_state
                        )
                    ]
            new_done_part = Khatma_Parts_Done(
                part_id=khatma_part.part_id,
                khatma_id=khatma_part.khatma_id,
                part_no=khatma_part.part_no,
                user_id=khatma_part.user_id if khatma_part.user_id is not None else khatma.user_id,
                part_start=khatma_part.part_start,
                part_end=khatma_part.part_end
            )
            session.add(new_done_part)
            await session.delete(khatma_part)
        await session.delete(khatma)
        return parts_dict


init_database_logger()
if __name__ == "__main__":
    asyncio.run(init_database())
