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

data_url = "https://raw.fastgit.org/mobyw/nonebot-plugin-txt2img/main/data/TXT2IMG"
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
    if not IMAGE_PATH.exists():
        IMAGE_PATH.mkdir(parents=True, exist_ok=True)
    return flag


@run_sync
def unarchive_file(path: Path):
    try:
        shutil.unpack_archive(path, extract_dir=FONT_PATH)
    except:  # noqa: E722
        shutil.rmtree(FONT_PATH)
        raise
    assert FONT_PATH.exists(), "font file not found"


async def download_template():
    async def download(url: str, path: Path) -> bool:
        try:
            async with await open_file(str(path), "wb") as file:
                async with AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_bytes():
                            await file.write(chunk)
            return True
        except:
            logger.warning("Download failed")
            return False

    # download font
    await download(font_url, FONT_ZIP)
    logger.info("Download font successful")
    await unarchive_file(FONT_ZIP)

    # download background
    await download(background_url, BACKGROUND_FILE)
    logger.info("Download background successful")

    # download banner
    await download(banner_url, BANNER_FILE)
    logger.info("Download banner successful")
