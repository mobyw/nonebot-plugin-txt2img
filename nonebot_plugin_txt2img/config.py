from pathlib import Path
from typing import Optional

from nonebot import get_driver
from pydantic import Extra, BaseModel
from nonebot_plugin_localstore import get_data_dir

plugin_data_dir: Path = get_data_dir("txt2img")
plugin_font_dir = plugin_data_dir / "font"
plugin_image_dir = plugin_data_dir / "image"
default_font_file = plugin_font_dir / "sarasa-mono-sc-regular.ttf"
default_image_file = plugin_image_dir / "mi_background.png"


class Config(BaseModel, extra=Extra.ignore):
    github_proxy: Optional[str] = "https://ghproxy.com"


plugin_config = Config(**get_driver().config.dict())

github_proxy = plugin_config.github_proxy if plugin_config.github_proxy else ""
github_proxy = github_proxy + "/" if not github_proxy.endswith("/") else github_proxy

data_url = (
    github_proxy
    + "https://raw.githubusercontent.com/mobyw/nonebot-plugin-txt2img/main/data/TXT2IMG"
)
default_font_url = data_url + "/font/sarasa-mono-sc-regular.ttf"
default_image_url = data_url + "/image/mi_background.png"
