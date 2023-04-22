<!-- markdownlint-disable MD033 MD036 MD041-->
<p align="center">
  <img src="https://github.com/mobyw/images/raw/main/Screenshots/nonebot-plugin-txt2img.png" width="400px"/>
</p>

<div align="center">

# nonebot-plugin-txt2img

_✨ 轻量文字转图片插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/mobyw/nonebot-plugin-txt2img/master/LICENSE">
    <img src="https://img.shields.io/github/license/mobyw/nonebot-plugin-txt2img.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-txt2img">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-txt2img.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
</p>

## 简介

本插件由使用 `PIL(Pillow)` 库将纯文字消息转为图片，启动时会检测所需资源是否存在，若不存在会自动下载到对应位置。生成的图片以 `base64` 格式发送，不保存到磁盘。

## 安装步骤

### 安装 NoneBot2

完整文档可以在 [这里](https://v2.nonebot.dev/) 查看。

请在创建项目时选用 `onebot v11` 适配器，并且按照文档完成最小实例的创建。

### 安装 nonebot-plugin-txt2img

#### 使用 `nb-cli` 安装（推荐）

```bash
nb plugin install nonebot-plugin-txt2img
```

#### 使用 `pip` 安装

```bash
pip install nonebot-plugin-txt2img
```

需要在 bot 根目录 `pyproject.toml` 文件中 [tool.nonebot] 部分添加：

```python
plugins = ["nonebot_plugin_txt2img"]
```

## 指令说明

指令匹配方式添加了 `to_me()` 规则，在群聊中使用时需要在命令首部或尾部添加 @机器人 (`@{bot_self_id}`) 或 机器人昵称 (`{bot_nickname}`)。

**使用指令**：txt2img

发送指令后根据提示输入标题、内容与字体大小，即可完成图片生成。

* 标题：以 `1.5` 倍字体大小排版在首行居中位置。
* 内容：以 `1` 倍字体大小左对齐排版。
* 字体大小：位于 `20~120` 之间的数字。

若内容不满一行，或每行都是较短的内容，会根据内容文本宽度调节图片宽度。

## 跨插件使用

如需在其他插件中使用文本转图片功能，可以从本插件导入。

导入方式：

```python
from nonebot import require
require("nonebot_plugin_txt2img")
from nonebot_plugin_txt2img import Txt2Img
```

基本使用方式（以 `OneBot V11` 为例）：

```python
from nonebot.adapters.onebot.v11 import MessageSegment

# 标题设置为 '' 或 ' ' 可以去除标题行
title = '标题'
text = '正文内容'
font_size = 32

txt2img = Txt2Img()

# 设置字体大小
txt2img.set_font_size(font_size)

# # 同时设置内容与标题字体大小
# title_font_size = 48
# txt2img.set_font_size(font_size, title_font_size)

# # 设置固定宽度
# # 设置后不会在内容较窄时自动调整宽度
# width = 1080
# txt2img.set_width(1080)

# # 绘制 PIL.Image.Image 图片
# pic = txt2img.draw_img(title, text)

# 绘制 base64 图片并发送
pic = txt2img.draw(title, text)
msg = MessageSegment.image(pic)
```

使用模板：

插件内置 `["mi", "simple"]` 两个模板，分别是小米便笺以及黑底白字简单风格。默认模板是 `"mi"`，可使用以下代码修改使用的模板：

```python
...
# 使用简约模板
pic = txt2img.draw(title, text, "simple")
msg = MessageSegment.image(pic)
```

也可以传入一个 `dict` 以实现自定义模板，示例如下：

```python
template = {
    # 必填项
    "font": "arial.ttf",                # 字体文件路径字符串，必填
    "text": {
        "color": (0, 0, 0),             # 正文颜色 RGB，必填
    },
    "title": {
        "color": (0, 0, 0),             # 标题颜色 RGB，必填
    },
    "margin": 80,                       # 边距，必填
    "background": {
        "type": "image",                # 背景类型，"image" 或 "color"，必填
        "image": "/path/to/img.png",    # 背景图片路径，类型为 "image" 时必填
        "color": (255, 255, 255),       # 背景颜色 RGB，类型为 "color" 时必填
    },
    # 可选项
    "border": {
        "color": (255, 255, 0),         # 边框颜色 RGB，必填
        "width": 2,                     # 边框宽度，必填
        "margin": 30,                   # 边框边距，小于顶层 "margin" 项，必填
    },
}
...
# 使用自定义模板
pic = txt2img.draw(title, text, template)
msg = MessageSegment.image(pic)
```

## 项目致谢

本项目基于以下项目或服务实现，排名不分先后。

* [nonebot2](https://github.com/nonebot/nonebot2)
* [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
* [txt2img](https://github.com/taseikyo/txt2img)
