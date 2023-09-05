from pathlib import Path
from copy import deepcopy
from typing import Union, Optional

from pydantic import BaseModel
from pydantic.color import Color, ColorType


class Font(BaseModel):
    """
    字体配置
    """

    color: Color
    """
    颜色
    """
    font: Path
    """
    字体文件路径
    """
    size: int
    """
    默认字体大小
    """


class ImageBackground(BaseModel):
    """
    图片填充背景
    """

    type = "image"
    """
    背景类型：图片
    """
    image: Path
    """
    图片文件路径
    """


class ColorBackground(BaseModel):
    """
    纯色背景
    """

    type = "color"
    """
    背景类型：纯色
    """
    color: Color
    """
    背景颜色
    """


class Border(BaseModel):
    """
    图片描边
    """

    width: int
    """
    宽度
    """
    margin: int
    """
    边距
    """
    color: Color
    """
    默认颜色
    """


class Template(BaseModel):
    """
    文字转图片模板
    """

    name: str
    """
    模板名称
    """
    background: Union[ImageBackground, ColorBackground]
    """
    背景
    """
    margin: int
    """
    边距
    """
    font: Font
    """
    全局字体配置
    """
    title: Optional[Font] = None
    """
    标题字体配置
    """
    content: Optional[Font] = None
    """
    内容字体配置
    """
    border: Optional[Border] = None
    """
    描边
    """

    def get_title_font(self) -> Font:
        if self.title is None:
            font = deepcopy(self.font)
            font.size = int(font.size * 1.5)
            return font
        return self.title

    def set_title_size(self, size: int):
        if self.title is None:
            self.title = deepcopy(self.get_title_font())
        self.title.size = size

    def set_title_color(self, color: ColorType):
        if self.title is None:
            self.title = deepcopy(self.get_title_font())
        self.title.color = Color(color)

    def get_content_font(self) -> Font:
        if self.content is None:
            return self.font
        return self.content

    def set_content_size(self, size: int):
        if self.content is None:
            self.content = deepcopy(self.get_content_font())
        self.content.size = size

    def set_content_color(self, color: ColorType):
        if self.content is None:
            self.content = deepcopy(self.get_content_font())
        self.content.color = Color(color)
