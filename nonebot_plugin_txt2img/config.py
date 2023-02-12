from pathlib import Path

from anyio import open_file
from httpx import AsyncClient
from nonebot.log import logger

DATA_ROOT = Path.cwd() / "data"
DATA_PATH = DATA_ROOT / "TXT2IMG"
FONT_PATH = DATA_PATH / "font"
IMAGE_PATH = DATA_PATH / "image"
FONT_FILE = FONT_PATH / "sarasa-mono-sc-regular.ttf"
MI_BACKGROUND_FILE = IMAGE_PATH / "mi_background.png"


github_proxy = "https://ghproxy.com/"
data_url = (
    github_proxy
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
    async def download(url: str, path: Path) -> bool:
        try:
            async with await open_file(str(path), "wb") as file:
                async with AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_bytes():
                            await file.write(chunk)
            return True
        except Exception as e:
            logger.warning(f"下载文件失败: {url} {e}")
            return False

    if check_path():
        return 2

    flag = 1

    # 下载字体文件
    if not await download(font_url, FONT_FILE):
        flag = 0

    # 下载背景文件
    if not await download(mi_background_url, MI_BACKGROUND_FILE):
        flag = 0

    return flag
