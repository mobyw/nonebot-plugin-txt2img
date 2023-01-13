import math
from base64 import b64encode
from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from wcwidth import wcswidth, wcwidth

from .config import BACKGROUND_FILE, BANNER_FILE, FONT_FILE, IMAGE_PATH

out_padding = 30
padding = 45
banner_size = 20

border_color = (220, 211, 196)
text_color = (125, 101, 89)


class Txt2Img:
    """Convert text to a b64 image"""

    font_family: str
    title_font_size: int
    text_font_size: int
    title_line_space: int
    text_line_space: int
    img_width: int
    fix_width: bool

    def __init__(self):
        self.font_family = str(FONT_FILE)
        self.title_font_size = 45
        self.text_font_size = 30
        self.title_line_space = 30
        self.text_line_space = 15
        self.img_width = 1080
        self.fix_width = False

    def set_font_size(self, font_size: int, title_font_size: Optional[int] = None):
        """设置字体大小"""
        self.text_font_size = font_size
        self.text_line_space = font_size // 2
        if title_font_size is not None:
            self.title_font_size = title_font_size
        else:
            self.title_font_size = int(font_size * 1.5)
        self.title_line_space = font_size

    def set_width(self, width: int):
        """设置图片宽度"""
        self.img_width = width
        self.fix_width = True

    def get_resized_width(self, char_ws: int) -> int:
        """获取推荐图片宽度"""
        return (out_padding + padding) * 2 + self.text_font_size * char_ws // 2

    def word_wrap(self, text: str) -> str:
        """为文本添加自动换行"""
        char_ws = (
            (self.img_width - (out_padding + padding) * 2) * 2 // self.text_font_size
        )
        temp_len = 0
        result = ""
        for ch in text:
            char_w = wcwidth(ch)
            if wcwidth(ch) > 0:
                result += ch
                temp_len += char_w
                if ch == "\n":
                    temp_len = 0
                if temp_len >= char_ws:
                    temp_len = 0
                    result += "\n"
        result = result.rstrip()
        return result

    def draw(self, title: str, text: str) -> str:
        """绘制当前模板下指定标题与正文的图片"""
        title_font = ImageFont.truetype(self.font_family, self.title_font_size)
        text_font = ImageFont.truetype(self.font_family, self.text_font_size)

        if title == " ":
            title = ""

        text = self.word_wrap(text)

        if text.find("\n") > -1:
            text_rows = len(text.split("\n"))
            total_w = self.img_width
        else:
            text_rows = 1
            if not self.fix_width:
                total_w = self.get_resized_width(wcswidth(text))
            else:
                total_w = self.img_width

        if title:
            inner_h = (
                padding * 2
                + self.title_font_size
                + self.title_line_space
                + self.text_font_size * text_rows
                + (text_rows - 1) * (self.text_line_space)
            )
        else:
            inner_h = (
                padding * 2
                + self.text_font_size * text_rows
                + (text_rows - 1) * (self.text_line_space)
            )

        total_h = out_padding * 2 + inner_h

        out_img = Image.new(mode="RGB", size=(total_w, total_h), color=(255, 255, 255))
        draw = ImageDraw.Draw(out_img)

        bg_img = Image.open(BACKGROUND_FILE).resize((total_w, 100), resample=3)
        banner_img = Image.open(BANNER_FILE).resize(
            (banner_size, banner_size), resample=3
        )

        # add background
        for x in range(int(math.ceil(total_h / 100))):
            out_img.paste(bg_img, (0, x * 100))

        # add border
        def draw_rectangle(draw, rect, width):
            for i in range(width):
                draw.rectangle(
                    (rect[0] + i, rect[1] + i, rect[2] - i, rect[3] - i),
                    outline=border_color,
                )

        draw_rectangle(
            draw,
            (out_padding, out_padding, total_w - out_padding, total_h - out_padding),
            2,
        )

        # add banner
        out_img.paste(banner_img, (out_padding, out_padding))
        out_img.paste(
            banner_img.transpose(Image.FLIP_TOP_BOTTOM),
            (out_padding, total_h - out_padding - banner_size + 1),
        )
        out_img.paste(
            banner_img.transpose(Image.FLIP_LEFT_RIGHT),
            (total_w - out_padding - banner_size + 1, out_padding),
        )
        out_img.paste(
            banner_img.transpose(Image.FLIP_LEFT_RIGHT).transpose(
                Image.FLIP_TOP_BOTTOM
            ),
            (
                total_w - out_padding - banner_size + 1,
                total_h - out_padding - banner_size + 1,
            ),
        )

        if title:
            user_w, _ = ImageDraw.Draw(Image.new(mode="RGB", size=(1, 1))).textsize(
                title, font=title_font, spacing=self.title_line_space
            )
            draw.text(
                ((total_w - user_w) // 2, out_padding + padding),
                title,
                font=title_font,
                fill=text_color,
                spacing=self.title_line_space,
            )
            draw.text(
                (
                    out_padding + padding,
                    out_padding
                    + padding
                    + self.title_font_size
                    + self.title_line_space,
                ),
                text,
                font=text_font,
                fill=text_color,
                spacing=self.text_line_space,
            )
        else:
            draw.text(
                (out_padding + padding, out_padding + padding),
                text,
                font=text_font,
                fill=text_color,
                spacing=self.text_line_space,
            )

        return self.img2b64(out_img)

    def img2b64(self, out_img) -> str:
        """图片转 base64"""
        buf = BytesIO()
        out_img.save(buf, format="PNG")
        base64_str = "base64://" + b64encode(buf.getvalue()).decode()
        return base64_str
