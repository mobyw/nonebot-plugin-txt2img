from nonebot import get_driver, on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.params import ArgPlainText
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .config import check_path, download_template
from .txt2img import Txt2Img

__plugin_meta__ = PluginMetadata(
    name="文字转图片",
    description="使用 Pillow 进行文字转图片",
    usage="""发送 txt2img 命令即可交互进行文字转图片""",
    extra={"version": "0.2.0"},
)

driver = get_driver()


@driver.on_startup
async def startup():
    logger.info("Initialing plugin txt2img")
    if not check_path():
        await download_template()
        logger.info("Success to download txt2img template")


txt2img = on_command("txt2img", rule=to_me())


@txt2img.got("TITLE", prompt="请输入标题（空格表示留空）")
@txt2img.got("TEXT", prompt="请输入内容")
@txt2img.got("SIZE", prompt="请输入字体大小")
async def txt2img_handle(
    title: str = ArgPlainText("TITLE"),
    text: str = ArgPlainText("TEXT"),
    size: str = ArgPlainText("SIZE"),
):
    if size.isdigit():
        if 20 <= int(size) <= 120:
            font_size = int(size)
            img = Txt2Img()
            img.set_font_size(font_size)
            pic = img.draw(title, text)
            await txt2img.finish(MessageSegment.image(pic))  # type: ignore
        else:
            await txt2img.reject("字体大小需要在20到120之间，请重新输入")  # type: ignore
    else:
        await txt2img.reject("字体大小格式有误，请输入20到120之间的数字")  # type: ignore
