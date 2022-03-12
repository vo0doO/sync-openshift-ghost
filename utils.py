from cmath import log
import os
from re import A
import shutil
import time
from msilib.schema import Error
from shutil import copy2
import logging
from cmdl import run
from get_token import get_token

logger = logging.getLogger("Sync my ghost openshift")

PROJECT_NAME = "sso"
APP_NAME = "ghostis"
BLOG_URL = "https://blog.vo.dedyn.io"
LOGS_FILE_NAME = "logs.log"

TOKEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token")
POD_GHOST_CONTENT_PATH = "/var/lib/ghost/content"
POD_GHOST_PATH = "/var/lib/ghost"
LOCAL_GHOST_PATH = "/home/vo0/ghost/current"
LOCAL_GHOST_PATH_FOR_BACKUP = "c:\\home\\vo0\\ghost\\current"
LOCAL_GHOST_CONTENT_PATH = "/home/vo0/ghost/current/content"
LOCAL_GHOST_BACKUP_PATH = "c:\\home\\vo0\\ghost\\backups"
LOCAL_GHOST_GOGLE_DRIVE_PATH = "c:\\home\\vo0\\ghost\\gdrive"
GHOST_CONTENT_ITEMS_DIRS = ["images", "themes", "logs", "settings", "data", "public"]
FILENAME_FOR_CREATE = str

POD_NAME = run(f"oc get pods -l app={APP_NAME} -o name").replace("pod/", "")


def get_time() -> str:
    try:
        return time.asctime().replace(" ", "_").replace(":", "-")
    except Exception as e:
        logger.error("Error on clean logs", e.with_traceback)


def backup_local_files() -> None:
    try:
        shutil.copytree(
            f"{LOCAL_GHOST_PATH_FOR_BACKUP}",
            f"{LOCAL_GHOST_BACKUP_PATH}\\ghost[{get_time()}]",
            symlinks=False,
            ignore=None,
            copy_function=copy2,
            ignore_dangling_symlinks=False,
            dirs_exist_ok=False,
        )
        return
    except Exception as e:
        logger.error("Error on clean logs", e.with_traceback)


def clear_backups(folder: str) -> None:
    if folder is None:
        raise Error("Backups folder is not specified.")
    try:
        backups_dirs = os.listdir(folder)
        if len(backups_dirs) <= 3:
            logger.info("Backups do not need cleaning")
            return

        for dir in backups_dirs[0 : len(backups_dirs) - 2]:
            shutil.rmtree(f"{folder}\\{dir}", ignore_errors=True)
    except Exception as e:
        logger.error("Error on clean logs", e.with_traceback)


def clear_logs(file_name) -> None:
    if file_name is None:
        raise Error("Not specified Log file name")
    try:
        with open(file_name, "r") as logs:
            lines = logs.readlines()
            lines_len = len(lines)
        if lines_len < 300:
            logger.info("Logs do not need cleaning")
            return

        with open("logs.log", "w") as logs:
            for line in lines[len(lines) - 200 : -1]:
                logs.write(line)
    except Exception as e:
        logger.error("Error on clean logs", e.with_traceback)


def make_archive_for_google_drive(folder, archive_name):
    if folder is None or archive_name is None:
        raise Error("Folder or archive name is empty")
    try:
        files = os.listdir(folder)
        if len(files) < 4:
            logger.info("Local archives for google drive don't need more cleaning")
            return

        for file in files[0 : len(files) - 3]:
            if ".zip" in file:
                os.remove(f"{folder}\\{file}")
        shutil.make_archive(
            f"{folder}\\{archive_name}", "zip", LOCAL_GHOST_PATH_FOR_BACKUP
        )
        return archive_name
    except Exception as e:
        logger.error("Error on make archive", e.with_traceback)


COMMANDS = {
    "backup_current_local_files": 'shutil.copytree(f"{LOCAL_GHOST_PATH_FOR_BACKUP}", f"{LOCAL_GHOST_BACKUP_PATH}\\ghost[{my_time}]", symlinks=False, ignore=None, copy_function=copy2, ignore_dangling_symlinks=False, dirs_exist_ok=False)',
    "login_to_cluster": f"oc login https://api.pro-eu-west-1.openshift.com --token={get_token(token_path=TOKEN_PATH, password='p')}",
    "set_project": f"oc project {PROJECT_NAME}",
    "get_pod_name": f"oc get pods -l app={APP_NAME} -o name",
    "copy_all_ghost_content_dirs_from_local_to_pod": f"oc cp {LOCAL_GHOST_CONTENT_PATH} {PROJECT_NAME}/{POD_NAME}:{POD_GHOST_PATH}",
    "copy_once_ghost_content_dir_from_local_to_pod": f"oc cp {LOCAL_GHOST_CONTENT_PATH}/{GHOST_CONTENT_ITEMS_DIRS[0]} {PROJECT_NAME}/{POD_NAME}:{POD_GHOST_CONTENT_PATH}",
    "copy_all_ghost_dirs_from_pod_to_local": f"oc cp {PROJECT_NAME}/{POD_NAME}:{POD_GHOST_PATH} {LOCAL_GHOST_PATH}",
    "copy_all_ghost_content_dirs_from_pod_to_local": f"oc cp {PROJECT_NAME}/{POD_NAME}:{POD_GHOST_CONTENT_PATH} {LOCAL_GHOST_PATH}",
    "copy_once_ghost_content_dir_from_local_to_pod": f"oc cp {PROJECT_NAME}/{POD_NAME}:{POD_GHOST_CONTENT_PATH}/{GHOST_CONTENT_ITEMS_DIRS[0]} {LOCAL_GHOST_CONTENT_PATH}/{GHOST_CONTENT_ITEMS_DIRS[0]} ",
    "create_empty_dir_in_pod": f"oc exec {POD_NAME} mkdir content/{GHOST_CONTENT_ITEMS_DIRS[0]}",
    "create_empty_file_in_pod": f"oc exec {POD_NAME} touch content/{FILENAME_FOR_CREATE}",
    "get_folders_in_pod": f"oc exec {POD_NAME} -- ls content/",
    "run_ghost": f"oc exec {POD_NAME} -- node current/index.js --url={BLOG_URL}",
}
