import shutil
from pathlib import Path

from anyio import open_file
from httpx import AsyncClient
from nonebot.log import logger
from nonebot.utils import run_sync

DATA_ROOT = Path.cwd() / "data"
DATA_PATH = DATA_ROOT / "TXT2IMG"
FONT_PATH = DATA_PATH / "font"
IMAGE_PATH = DATA_PATH / "image"

FONT_ZIP = FONT_PATH / "sarasa-mono-sc-regular.zip"
FONT_FILE = FONT_PATH / "sarasa-mono-sc-regular.ttf"
BACKGROUND_FILE = IMAGE_PATH / "background.png"
BANNER_FILE = IMAGE_PATH / "banner.png"

github_proxy = "https://ghproxy.com/"
data_url = github_proxy + "https://raw.githubusercontent.com/mobyw/nonebot-plugin-txt2img/main/data/TXT2IMG"
font_url = data_url + "/font/sarasa-mono-sc-regular.zip"
background_url = data_url + "/image/background.png"
banner_url = data_url + "/image/banner.png"


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
    return flag


@run_sync
def unarchive_file(path: Path):
    try:
        shutil.unpack_archive(path, extract_dir=FONT_PATH)
    except:  # noqa: E722
        shutil.rmtree(FONT_PATH)
        raise
    assert FONT_FILE.exists(), "font file not found"


async def download_template():
    async def download(url: str, path: Path) -> bool:
        try:
            async with await open_file(str(path), "wb") as file:
                async with AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_bytes():
                            await file.write(chunk)
            return True
        except Exception as e:
            logger.warning(f"Download failed: {url} {e}")
            return False
    
    failed = False

    # download font
    if not await download(font_url, FONT_ZIP):
        failed = True
    else:
        try:
            await unarchive_file(FONT_ZIP)
        except Exception as e:
            logger.warning(f"Unzip failed: {FONT_ZIP} {e}")
            failed = True

    # download background
    if not await download(background_url, BACKGROUND_FILE):
        failed = True

    # download banner
    if not await download(banner_url, BANNER_FILE):
        failed = True

    if failed:
        logger.error("The resource is not fully downloaded.")
        logger.error("Please manually copy the resource file.")
        logger.error(f"Resource path: {DATA_PATH}")
