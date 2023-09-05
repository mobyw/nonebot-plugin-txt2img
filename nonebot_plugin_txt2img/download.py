import asyncio
from enum import Enum

from nonebot import get_driver
from nonebot.log import logger
from nonebot.drivers import Request, ForwardDriver

from .config import (
    plugin_font_dir,
    default_font_url,
    plugin_image_dir,
    default_font_file,
    default_image_url,
    default_image_file,
)


class Status(Enum):
    FAILED = 0
    OK = 1
    EXIST = 2


def check_resource() -> bool:
    """
    检查资源文件夹
    """

    flag = True
    if not plugin_font_dir.exists():
        plugin_font_dir.mkdir(parents=True, exist_ok=True)
        flag = False
    if not plugin_image_dir.exists():
        plugin_image_dir.mkdir(parents=True, exist_ok=True)
        flag = False
    if not default_font_file.exists() or not default_image_file.exists():
        flag = False
    return flag


async def download_template() -> Status:
    """
    下载默认模板资源
    """

    # 检查资源是否已存在
    if check_resource():
        return Status.EXIST

    # 获取 nonebot2 的 driver
    driver = get_driver()

    # 检查 driver
    if not isinstance(driver, ForwardDriver):
        message = f"当前驱动器 {driver} 不支持 ForwardDriver，请配置合适的驱动器"
        raise RuntimeError(message)

    # 预定义下载文件过程
    async def download(url: str) -> bytes:
        logger.info(f"正在下载 {url}")
        for i in range(3):
            try:
                request = Request("GET", url, timeout=20)
                response = await driver.request(request)
                if response.status_code == 302:
                    url = response.headers.get("location") or url
                    continue
                assert isinstance(response.content, bytes)
                return response.content
            except Exception as e:
                logger.warning(f"下载 {url} 出错, 重试次数 {i+1}/3: {e}")
                await asyncio.sleep(2)
        logger.error(f"下载资源失败，链接：{url}")
        raise Exception(f"{url} 下载失败！")

    flag = Status.OK

    # 下载字体文件
    try:
        font_data = await download(default_font_url)
        with default_font_file.open("wb") as f:
            f.write(font_data)
    except Exception as e:
        flag = Status.FAILED
        logger.warning(str(e))

    # 下载背景文件
    try:
        image_data = await download(default_image_url)
        with default_image_file.open("wb") as f:
            f.write(image_data)
    except Exception as e:
        flag = Status.FAILED
        logger.warning(str(e))

    return flag
