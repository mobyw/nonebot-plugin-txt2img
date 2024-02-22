from io import BytesIO
from copy import deepcopy
from typing import Union, Optional

from pydantic.color import ColorType
from PIL import Image, ImageDraw, ImageFont

from .template import templates
from .model import Template, ColorBackground, ImageBackground


class Txt2Img:
    """
    纯文本转图片
    """

    fix_width: bool = False
    max_width: int = 1080

    template: Template = deepcopy(templates["default"])

    def __init__(self, template: Union[Template, str, None] = None):
        if isinstance(template, Template):
            self.template = deepcopy(template)
        elif isinstance(template, str) and template in templates.keys():
            self.template = deepcopy(templates[template])

    def set_font_size(self, size: int, title: Optional[int] = None):
        """设置字体大小"""
        self.template.set_content_size(size)
        self.template.set_title_size(title if title else int(size * 1.5))

    def set_font_color(self, color: ColorType, title: Optional[ColorType] = None):
        """设置字体颜色"""
        self.template.set_content_color(color)
        self.template.set_title_color(title if title else color)

    def set_width(self, width: int):
        """设置固定图片宽度"""
        self.max_width = width
        self.fix_width = True

    def text_word_wrap(self, content: str) -> str:
        """文本内容自动换行"""
        font_config = self.template.get_content_font()
        font = ImageFont.truetype(font_config.font.as_posix(), font_config.size)
        length_counter: float = 0
        text_result: str = ""
        # 处理文本
        for ch in content:
            if ch == "\n":
                # 换行
                text_result += ch
                length_counter = 0
                continue
            char_width = font.getlength(ch)
            if char_width <= 0:
                # 不可见字符
                continue
            text_result += ch
            length_counter += char_width
            if length_counter + font_config.size > self.max_width:
                length_counter = 0
                text_result += "\n"
        # 移除末尾空白
        text_result = text_result.rstrip()
        return text_result

    def draw_text(self, title: str, content: str) -> Image.Image:
        """绘制标题与正文的图片"""
        title_font_config = self.template.get_title_font()
        title_font = ImageFont.truetype(
            title_font_config.font.as_posix(), title_font_config.size
        )
        content_font_config = self.template.get_content_font()
        content_font = ImageFont.truetype(
            content_font_config.font.as_posix(), content_font_config.size
        )
        # 移除标题两端空白
        title = title.strip()
        # 多行标题只取首行
        if len(title.split("\n")) > 1:
            title = title.split("\n")[0]
        # 预处理正文文本
        content = self.text_word_wrap(content)
        content_lines = content.split("\n")
        content_row_number = len(content_lines)
        # 获取标题宽度
        title_width = title_font.getlength(title)
        # 调整宽度
        if not self.fix_width:
            line_max_width = max(
                [content_font.getlength(line) for line in content_lines]
            )
            text_total_width = int(max(line_max_width, title_width))
        else:
            text_total_width = self.max_width
        # 计算图像高度
        if title:
            text_total_height = (
                title_font.size
                + content_font.size  # title line space
                + content_font.size * content_row_number
                + content_row_number * (content_font.size // 2)  # content line space
            )
        else:
            text_total_height = (
                content_font.size * content_row_number
                + content_row_number * (content_font.size // 2)
            )
        # 创建画布
        output_image = Image.new(
            mode="RGBA",
            size=(text_total_width, text_total_height),
            color=(255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(output_image)
        # 绘制标题
        content_offset = 0
        if title:
            draw.text(
                ((text_total_width - title_width) // 2, 0),
                title,
                font=title_font,
                fill=title_font_config.color.as_rgb(),
                spacing=content_font.size,
            )
            content_offset = title_font.size + content_font.size
        # 绘制正文
        draw.text(
            (0, content_offset),
            content,
            font=content_font,
            fill=content_font_config.color.as_rgb(),
            spacing=content_font.size // 2,
        )
        return output_image

    def draw_img(
        self, title: str, text: str, template: Union[Template, str, None] = None
    ) -> Image.Image:
        """绘制给定文本的图片"""
        # 修改模板
        if isinstance(template, Template):
            self.template = deepcopy(template)
        elif isinstance(template, str) and template in templates.keys():
            self.template = deepcopy(templates[template])
        # 绘制文字区域
        text_image = self.draw_text(title, text)
        # 绘制图片背景
        if isinstance(background := self.template.background, ImageBackground):
            full_image = Image.new(
                "RGBA",
                (
                    text_image.width + 2 * self.template.margin,
                    text_image.height + 2 * self.template.margin,
                ),
                (0, 0, 0, 0),
            )
            background_image = Image.open(background.image)
            full_image = tile_image(background_image, full_image)
        elif isinstance(background := self.template.background, ColorBackground):
            full_image = Image.new(
                "RGBA",
                (
                    text_image.width + 2 * self.template.margin,
                    text_image.height + 2 * self.template.margin,
                ),
                background.color.as_rgb(),
            )
        else:
            raise ValueError("未知的图像背景配置")
        full_image.paste(
            text_image, (self.template.margin, self.template.margin), text_image
        )
        # 绘制图片边框
        if (border := self.template.border) is not None:
            draw = ImageDraw.Draw(full_image)
            draw.rectangle(
                (
                    border.margin,
                    border.margin,
                    full_image.width - border.margin,
                    full_image.height - border.margin,
                ),
                outline=border.color.as_rgb(),
                width=border.width,
            )
        return full_image

    def draw(
        self, title: str, text: str, template: Union[Template, str, None] = None
    ) -> BytesIO:
        """绘制给定模板下指定标题与正文的图片并转换为 BytesIO"""
        image = self.draw_img(title, text, template)
        output = BytesIO()
        image.save(output, "png")
        return output


def tile_image(image: Image.Image, full_image: Image.Image) -> Image.Image:
    """图片平铺"""
    w, h = image.size
    for i in range(0, full_image.size[0], w):
        for j in range(0, full_image.size[1], h):
            full_image.paste(image, (i, j))
    return full_image
