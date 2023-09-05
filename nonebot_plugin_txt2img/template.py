from typing import Dict

from .config import default_font_file, default_image_file
from .model import Font, Color, Border, Template, ColorBackground, ImageBackground

template_default = Template(
    name="default",
    font=Font(color=Color("dimgray"), font=default_font_file, size=32),
    margin=80,
    background=ImageBackground(image=default_image_file),
    border=Border(width=2, margin=30, color=Color("lightgray")),
)

template_simple = Template(
    name="simple",
    font=Font(color=Color("black"), font=default_font_file, size=32),
    margin=50,
    background=ColorBackground(color=Color("white")),
)

templates: Dict[str, Template] = {
    template_default.name: template_default,
    template_simple.name: template_simple,
}
