from pathlib import Path
from zipfile import ZipFile

import requests
from nonebot.log import logger

DATA_ROOT = Path.cwd() / "data"
DATA_PATH = DATA_ROOT / "TXT2IMG"
FONT_PATH = DATA_PATH / "font"
IMAGE_PATH = DATA_PATH / "image"

FONT_ZIP = FONT_PATH / "sarasa-mono-sc-regular.zip"
FONT_FILE = FONT_PATH / "sarasa-mono-sc-regular.ttf"
BACKGROUND_FILE = IMAGE_PATH / "background.png"
BANNER_FILE = IMAGE_PATH / "banner.png"

data_url = "https://cdn.jsdelivr.net/gh/mobyw/nonebot-plugin-txt2img@main/data/TXT2IMG"
font_url = data_url + "/font/sarasa-mono-sc-regular.zip"
background_url = data_url + "/image/background.png"
banner_url = data_url + "/image/banner.png"


if not DATA_ROOT.exists():
    DATA_ROOT.mkdir()

if not DATA_PATH.exists():
    DATA_PATH.mkdir()

if not FONT_PATH.exists():
    FONT_PATH.mkdir()

if not IMAGE_PATH.exists():
    IMAGE_PATH.mkdir()

if not FONT_FILE.exists():
    font_req = requests.get(font_url)
    with open(FONT_ZIP, "wb") as file:
        file.write(font_req.content)
        logger.info("字体文件下载成功")
        with ZipFile(FONT_ZIP, 'r') as zipfile:
            for name in zipfile.namelist():
                zipfile.extract(name, FONT_PATH)
        logger.info("字体文件解压成功")
else:
    logger.info("字体文件已存在")

if not BACKGROUND_FILE.exists():
    background_req = requests.get(background_url)
    with open(BACKGROUND_FILE, "wb") as file:
        file.write(background_req.content)
        logger.info("背景文件下载成功")
else:
    logger.info("背景文件已存在")

if not BANNER_FILE.exists():
    banner_req = requests.get(banner_url)
    with open(BANNER_FILE, "wb") as file:
        file.write(banner_req.content)
        logger.info("模板文件下载成功")
else:
    logger.info("模板文件已存在")
