from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import ArgPlainText
from nonebot.rule import to_me

from .txt2img import Txt2Img

txt2img = on_command("txt2img", rule=to_me())


@txt2img.got("TITLE", prompt="请输入标题（空格表示留空）")
@txt2img.got("TEXT", prompt="请输入内容")
@txt2img.got("SIZE", prompt="请输入字体大小")
async def txt2img_handle(
    title: str = ArgPlainText("TITLE"),
    text: str = ArgPlainText("TEXT"),
    size: str = ArgPlainText("SIZE")
):
    if size.isdigit():
        font_size = int(size)
        if title == ' ':
            title = ''
        img = Txt2Img(font_size)
        pic = img.save(title, text)
        await txt2img.finish(MessageSegment.image(pic))  # type: ignore
    else:
        await txt2img.finish("字体大小格式有误，请输入数字！")  # type: ignore
