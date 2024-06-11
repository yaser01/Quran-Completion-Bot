import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import telegram
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys

sys.path.append('../')  # add ability to import modules from parent folder
from Packges.DriveManager import DriveManager
from Startup.Global_Files import Logs_Folder, Backup_File_Prefix

load_dotenv()
DATABASE_URI = os.getenv('DATABASE_URI')
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID')
ADMIN_BOT_TOKEN = os.getenv('BOT_TOKEN')
Admin_Bot = telegram.Bot(token=ADMIN_BOT_TOKEN)
GOOGLE_DRIVE_BACKUP_FOLDER_ID = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID')
drive_manager = DriveManager()
backups_files_ids = []
BACKUPS_LIMIT = 50
engine = create_engine(DATABASE_URI, client_encoding='utf8')
Session_Maker = sessionmaker(bind=engine)
session = Session_Maker()

logging.basicConfig(
    format='(%(asctime)s): %(name)s [%(levelname)s]: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG,
    handlers=[
        TimedRotatingFileHandler(filename=os.path.join(Logs_Folder, "backup_database.log"),
                                 encoding="UTF-8",
                                 when='D',
                                 interval=7, backupCount=4, delay=False, utc=False),
        logging.StreamHandler()
    ], force=True
)
app = FastAPI()


async def backup_database():
    file_name = ""
    try:
        file_path = str(Backup_File_Prefix) + "_" + str(
            datetime.now().strftime("%Y_%m_%d_%H_%M_%S")) + ".gz"
        file_name = Path(file_path).name
        os.system(f"pg_dump --dbname={DATABASE_URI} | gzip -9 > \"{file_path}\"")
        new_file_id = drive_manager.upload_file(file_name=file_name, file_path=file_path,
                                                folder_drive_id=GOOGLE_DRIVE_BACKUP_FOLDER_ID)
        file_size = os.path.getsize(Path(file_path))
        os.remove(Path(file_path))
        backups_files_ids.append(new_file_id)
        if len(backups_files_ids) > BACKUPS_LIMIT:
            oldest_file_id = backups_files_ids[0]
            backups_files_ids.pop(0)
            drive_manager.delete_file(oldest_file_id)

        logging.info(f"Uploade file: '{file_name}' with size: [{round(file_size / (1024 * 1024), 2)} MB] Succeeded :D ")
    except Exception as e:
        logging.error(e)
        message_text = "لقد حدث خطأ أثناء القيام بنسخة احتياطية..."
        message_text += "\n"
        message_text += str(e)
        await Admin_Bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message_text)
        logging.info(f"Uploade file {file_name} Failed :( ")


@app.get("/backup_database")
async def root(background_tasks: BackgroundTasks):
    background_tasks.add_task(backup_database)
    return "True"
