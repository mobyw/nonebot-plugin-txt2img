import asyncio
from pathlib import Path

import httpx
from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseSettings

DATA_ROOT = Path.cwd() / "data"
DATA_PATH = DATA_ROOT / "TXT2IMG"
FONT_PATH = DATA_PATH / "font"
IMAGE_PATH = DATA_PATH / "image"
FONT_FILE = FONT_PATH / "sarasa-mono-sc-regular.ttf"
MI_BACKGROUND_FILE = IMAGE_PATH / "mi_background.png"


class Config(BaseSettings):
    github_proxy:str = "https://ghproxy.net/"
    
config = Config.parse_obj(get_driver().config)


data_url = (
    config.github_proxy
    + "https://raw.githubusercontent.com/mobyw/nonebot-plugin-txt2img/main/data/TXT2IMG"
)
font_url = data_url + "/font/sarasa-mono-sc-regular.ttf"
mi_background_url = data_url + "/image/mi_background.png"


templates = {
    "mi": {
        "font": str(FONT_FILE),
        "text": {
            "color": (125, 101, 89),
        },
        "title": {
            "color": (125, 101, 89),
        },
        "margin": 80,
        "background": {
            "type": "image",
            "image": str(MI_BACKGROUND_FILE),
        },
        "border": {
            "color": (220, 211, 196),
            "width": 2,
            "margin": 30,
        },
    },
    "simple": {
        "font": str(FONT_FILE),
        "text": {
            "color": (0, 0, 0),
        },
        "title": {
            "color": (0, 0, 0),
        },
        "margin": 50,
        "background": {
            "type": "color",
            "color": (255, 255, 255),
        },
    },
}


# 检查文件夹
def check_path() -> bool:
    flag = True
    if not DATA_ROOT.exists():
        DATA_ROOT.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        flag = False
    if not FONT_PATH.exists():
        FONT_PATH.mkdir(parents=True, exist_ok=True)
        flag = False
    if not IMAGE_PATH.exists():
        IMAGE_PATH.mkdir(parents=True, exist_ok=True)
        flag = False
    if not FONT_FILE.exists() or not MI_BACKGROUND_FILE.exists():
        flag = False
    return flag


# 下载模板
async def download_template() -> int:
    # 下载文件
    async def download(url: str) -> bytes:
        async with httpx.AsyncClient() as client:
            for i in range(3):
                try:
                    resp = await client.get(url, timeout=20)
                    if resp.status_code == 302:
                        url = resp.headers["location"]
                        continue
                    resp.raise_for_status()
                    return resp.content
                except Exception as e:
                    logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                    await asyncio.sleep(3)
            logger.error(f"Error downloading {url}, all attempts failed.")
            raise Exception(f"{url} 下载失败！")

    if check_path():
        return 2

    flag = 1

    # 下载字体文件
    try:
        font_data = await download(font_url)
        with FONT_FILE.open("wb") as f:
            f.write(font_data)
    except Exception as e:
        flag = 0
        logger.warning(str(e))

    # 下载背景文件
    try:
        mi_bg_data = await download(mi_background_url)
        with MI_BACKGROUND_FILE.open("wb") as f:
            f.write(mi_bg_data)
    except Exception as e:
        flag = 0
        logger.warning(str(e))

    return flag
