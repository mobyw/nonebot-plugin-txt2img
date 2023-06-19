from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFont

from .config import FONT_FILE, templates


class Txt2Img:
    """Convert text to image"""

    font_family: str
    title_font_size: int
    text_font_size: int
    title_line_space: int
    text_line_space: int
    text_max_width: int
    fix_width: bool
    text_color: tuple
    title_color: tuple
    bg_color: tuple

    def __init__(self):
        self.font_family = str(FONT_FILE)
        self.title_font_size = 45
        self.text_font_size = 30
        self.title_line_space = 30
        self.text_line_space = 15
        self.text_max_width = 1080
        self.fix_width = False
        self.text_color = (0, 0, 0, 255)
        self.title_color = (0, 0, 0, 255)
        self.bg_color = (255, 255, 255, 0)

    def set_font_family(self, font_family: str):
        """设置字体"""
        self.font_family = font_family

    def set_font_size(self, font_size: int, title_font_size: Optional[int] = None):
        """设置字体大小"""
        self.text_font_size = font_size
        self.text_line_space = font_size // 2
        if title_font_size is not None:
            self.title_font_size = title_font_size
        else:
            self.title_font_size = int(font_size * 1.5)
        self.title_line_space = font_size

    def set_font_color(self, text_color: tuple, title_color: Optional[tuple] = None):
        """设置字体颜色"""
        self.text_color = text_color
        if title_color is not None:
            self.title_color = title_color
        else:
            self.title_color = text_color

    def set_width(self, width: int):
        """设置图片宽度"""
        self.text_max_width = width
        self.fix_width = True

    def word_wrap(self, text: str, font: ImageFont.FreeTypeFont) -> str:
        """自动换行"""
        temp_len = 0
        result = ""
        for ch in text:
            char_w = font.getsize(ch)[0]
            if ch == "\n":
                result += ch
                temp_len = 0
            elif char_w > 0:
                result += ch
                temp_len += char_w
                if temp_len > self.text_max_width - self.text_font_size:
                    temp_len = 0
                    result += "\n"
        result = result.rstrip()
        return result

    def draw_img(
        self, title: str, text: str, template: Union[str, dict] = "mi"
    ) -> Image.Image:
        """绘制给定模板下的图片"""

        if isinstance(template, str):
            try:
                template = templates[template]  # type: ignore
            except KeyError:
                template = templates["mi"]  # type: ignore

        try:
            font_family = template["font"]  # type: ignore
            text_color = template["text"]["color"]  # type: ignore
            title_color = template["title"]["color"]  # type: ignore
            margin = int(template["margin"])  # type: ignore
            background = template["background"]  # type: ignore
        except KeyError:
            raise ValueError("Invalid template")

        if not Path(font_family).exists():
            raise ValueError("Invalid font")

        self.set_font_family(font_family)
        self.set_font_color(text_color, title_color)  # type: ignore
        text_img = self.draw_text(title, text)

        try:
            if background["type"] == "image":  # type: ignore
                out_img = Image.new(
                    "RGBA",
                    (text_img.width + 2 * margin, text_img.height + 2 * margin),
                    (0, 0, 0, 0),
                )
                bg_img = Image.open(background["image"])  # type: ignore
                out_img = tile_image(bg_img, out_img)
            elif background["type"] == "color":  # type: ignore
                out_img = Image.new("RGBA", (text_img.width + 2 * margin, text_img.height + 2 * margin), background["color"])  # type: ignore
            else:
                raise ValueError("Invalid background type")
        except Exception:
            raise ValueError("Invalid template")

        out_img.paste(text_img, (margin, margin), text_img)

        try:
            border = template["border"]  # type: ignore
            border_color = border["color"]  # type: ignore
            border_width = int(border["width"])  # type: ignore
            border_margin = int(border["margin"])  # type: ignore
            draw = ImageDraw.Draw(out_img)
            draw.rectangle(
                (
                    border_margin,
                    border_margin,
                    out_img.width - border_margin,
                    out_img.height - border_margin,
                ),
                outline=border_color,
                width=border_width,
            )
        except KeyError:
            pass
        except Exception:
            raise ValueError("Invalid template")

        return out_img

    def draw(self, title: str, text: str, template: Union[str, dict] = "mi") -> str:
        """绘制给定模板下指定标题与正文的图片并转换为base64"""
        out_img = self.draw_img(title, text, template)
        return img2b64(out_img)

    def draw_text(self, title: str, text: str) -> Image.Image:
        """绘制标题与正文的图片"""
        title_font = ImageFont.truetype(self.font_family, self.title_font_size)
        text_font = ImageFont.truetype(self.font_family, self.text_font_size)

        if title == " ":
            title = ""

        if len(title.split("\n")) > 1:
            title = title.split("\n")[0]

        text = self.word_wrap(text, text_font)

        lines = text.split("\n")
        text_rows = len(lines)

        title_width = title_font.getsize(title)[0]

        if not self.fix_width:
            line_max_width = max([text_font.getsize(line)[0] for line in lines])
            text_total_width = max(line_max_width, title_width)
        else:
            text_total_width = self.text_max_width

        if title:
            text_total_height = (
                self.title_font_size
                + self.title_line_space
                + self.text_font_size * text_rows
                + (text_rows - 1) * (self.text_line_space)
            )
        else:
            text_total_height = self.text_font_size * text_rows + (text_rows - 1) * (
                self.text_line_space
            )

        out_img = Image.new(
            mode="RGBA", size=(text_total_width, text_total_height), color=self.bg_color
        )
        draw = ImageDraw.Draw(out_img)

        if title:
            draw.text(
                ((text_total_width - title_width) // 2, 0),
                title,
                font=title_font,
                fill=self.text_color,
                spacing=self.title_line_space,
            )
            draw.text(
                (
                    0,
                    self.title_font_size + self.title_line_space,
                ),
                text,
                font=text_font,
                fill=self.text_color,
                spacing=self.text_line_space,
            )
        else:
            draw.text(
                (0, 0),
                text,
                font=text_font,
                fill=self.text_color,
                spacing=self.text_line_space,
            )

        return out_img


def tile_image(small_image: Image.Image, big_image: Image.Image) -> Image.Image:
    """将小图片平铺到大图片上"""
    w, h = small_image.size

    for i in range(0, big_image.size[0], w):
        for j in range(0, big_image.size[1], h):
            big_image.paste(small_image, (i, j))

    return big_image


def img2b64(img) -> str:
    """图片转 base64"""
    buf = BytesIO()
    img.save(buf, format="PNG")
    base64_str = "base64://" + b64encode(buf.getvalue()).decode()
    return base64_str
