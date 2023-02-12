from nonebot import get_driver, on_command, on_metaevent
from nonebot.adapters.onebot.v11 import Bot, LifecycleMetaEvent, MessageSegment
from nonebot.log import logger
from nonebot.params import ArgPlainText
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .config import download_template
from .txt2img import Txt2Img

__plugin_meta__ = PluginMetadata(
    name="文字转图片",
    description="使用 Pillow 进行文字转图片",
    usage="""发送 txt2img 命令即可交互进行文字转图片""",
    extra={"version": "0.3.0"},
)


def check_first_connect(_: LifecycleMetaEvent) -> bool:
    return True


start_metaevent = on_metaevent(rule=check_first_connect, temp=True)


@start_metaevent.handle()
async def start(bot: Bot) -> None:
    logger.info("开始检查资源文件")
    flag = await download_template()
    if flag == 2:
        logger.info("模板文件完好")
    elif flag == 1:
        logger.info("模板文件下载完成")
    else:
        message = "模板文件下载失败，请尝试手动下载并放置到工程目录下的 data/TXT2IMG 文件夹中"
        logger.warning(message)
        try:
            await bot.send_private_msg(
                user_id=int(list(get_driver().config.superusers)[0]), message=message
            )
        except Exception as e:
            logger.warning(f"发送提示消息失败: {e}")


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
