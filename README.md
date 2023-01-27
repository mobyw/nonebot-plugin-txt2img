<!-- markdownlint-disable MD033 MD041-->
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/mobyw/images@main/Screenshots/nonebot-plugin-txt2img.png" width="400px"/>
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

#### 使用 `nb-cli` 安装

```bash
nb plugin install nonebot-plugin-txt2img
```

#### 使用 `pip` 安装

```bash
pip install nonebot-plugin-txt2img
```

需要在 `bot.py` 文件添加以下代码加载插件：

```python
nonebot.load_plugin("nonebot_plugin_txt2img")
```

## 指令说明

指令匹配方式添加了 `to_me()` 规则，在群聊中使用时需要在命令首部或尾部添加 @机器人 (`@{bot_self_id}`) 或 机器人昵称 (`{bot_nickname}`)。

**使用指令**：txt2img

发送指令后根据提示输入标题、内容与字体大小，即可完成图片生成。

* 标题：以 `1.5` 倍字体大小排版在首行居中位置。
* 内容：以 `1` 倍字体大小左对齐排版。
* 字体大小：位于 `20~120` 之间的数字。

若内容只有一行，会根据内容文本宽度调节图片宽度。

## 跨插件使用

如需在其他插件中使用文本转图片功能，可以从本插件导入。

导入方式：

```python
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_txt2img import Txt2Img
```

使用方式：

```python
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

# 绘制图片并发送
pic = txt2img.draw(title, text)
msg = MessageSegment.image(pic)
```

## 项目致谢

本项目基于以下项目或服务实现，排名不分先后。

* [nonebot2](https://github.com/nonebot/nonebot2)
* [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
* [txt2img](https://github.com/taseikyo/txt2img)
