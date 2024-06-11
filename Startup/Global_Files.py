import os
from pathlib import Path

Script_Folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Startup_Folder = os.path.join(os.path.abspath(Script_Folder), Path('Startup'))
Secret_Folder = os.path.join(os.path.abspath(Script_Folder), Path('Secret Files'))
Backup_File_Prefix = os.path.join(Script_Folder, "Backup")
Logs_Folder = os.path.join(os.path.abspath(Script_Folder), Path('logs'))
Resources_Folder = os.path.join(os.path.abspath(Script_Folder), Path('Resources'))
Quran_Images_Arabic_Folder = os.path.join(os.path.abspath(Resources_Folder), Path('Quran Images Arabic'))
Quran_PDF_Arabic_Folder = os.path.join(os.path.abspath(Resources_Folder), Path('Quran PDF Arabic'))
Quran_Hafs_Pages_Images_Folder = os.path.join(os.path.abspath(Quran_Images_Arabic_Folder), Path('Hafs'))
Quran_Hafs_Tajwid_Pages_Images_Folder = os.path.join(os.path.abspath(Quran_Images_Arabic_Folder), Path('Hafs Tajwid'))
Quran_Hafs_Chapters_Folder = os.path.join(os.path.abspath(Quran_PDF_Arabic_Folder), Path("Hafs"), Path("By Chapters"))
Quran_Hafs_Tajwid_Chapters_Folder = os.path.join(os.path.abspath(Quran_PDF_Arabic_Folder), Path("Hafs Tajwid"), Path("By Chapters"))
Daily_Page_Quran_File = os.path.join(Startup_Folder, "Quran_Daily_Page.json")
Developer_Gmail_Credential_File = os.path.join(Secret_Folder, "developer_credentials.json")
Developer_Gmail_Token_File = os.path.join(Secret_Folder, "developer_token.json")
os.makedirs(Logs_Folder, exist_ok=True)
