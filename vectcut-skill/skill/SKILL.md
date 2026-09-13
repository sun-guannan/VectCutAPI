---
name: vectcut-api
description: VectCutAPI is a powerful cloud-based video editing API tool that provides programmatic control over CapCut/JianYing (剪映) for professional video editing. Use this skill when users need to: (1) Create video draft projects programmatically, (2) Add video/audio/image materials with precise control, (3) Add text, subtitles, and captions, (4) Apply effects, transitions, and animations, (5) Add keyframe animations, (6) Process videos in batch, (7) Generate AI-powered videos, (8) Integrate with n8n workflows, (9) Build MCP video editing agents. The API supports HTTP REST and MCP protocols, works with both CapCut (international) and JianYing (China), and provides web preview without downloading.
---

# VectCutAPI 视频剪辑 API

## 概述

VectCutAPI 是一款强大的云端视频剪辑 API 工具，通过编程方式控制剪映/CapCut 进行专业视频编辑。它填补了 AI 生成素材与专业视频编辑之间的空白，提供精确的编辑控制能力。

### 核心优势

1. **双协议支持** - HTTP REST API 和 MCP 协议
2. **实时预览** - 网页预览无需下载
3. **可二次编辑** - 自动部署到剪映/CapCut 后，必须通过重新打开工程验证媒体链接
4. **云端处理** - 全云端操作生成视频

### 系统要求

- Python 3.10+
- 剪映 或 CapCut 国际版
- FFmpeg (可选，用于某些视频处理)

### 快速启动

```bash
# 安装依赖
pip install -r requirements.txt      # HTTP API 基础依赖
pip install -r requirements-mcp.txt  # MCP 协议支持 (可选)

# 配置文件
cp config.json.example config.json

# 启动服务
python capcut_server.py  # HTTP API 服务器 (端口: 9001)
python mcp_server.py     # MCP 协议服务器
```

## 工作流程

### 标准视频制作流程

```
1. 创建草稿 (create_draft)
   - 设置分辨率: 1080x1920 (竖屏) / 1920x1080 (横屏) / 1080x1080 (方形)
   - 获取 draft_id

2. 添加素材轨道
   - add_video: 添加视频轨道
   - add_audio: 添加音频轨道
   - add_image: 添加图片素材

3. 添加文字元素
   - add_text: 添加标题、说明文字
   - add_subtitle: 导入 SRT 字幕文件

4. 应用特效
   - add_effect: 添加视频特效
   - add_sticker: 添加贴纸素材
   - add_video_keyframe: 添加关键帧动画

5. 保存草稿
   - save_draft: 生成可导入剪映的草稿文件

6. 本地交付验收
   - 确认部署后的草稿和素材都位于 CapCut/JianYing 可访问路径
   - 重新打开工程，确认没有“链接媒体”弹窗、红色缺失素材或黑帧
```

### AI 视频生成工作流

```
AI 文案生成
    ↓
TTS 文字转语音 → audio_url
    ↓
图生视频 → video_url
    ↓
VectCutAPI 组合草稿
    ↓
导出或二次编辑
```

### 批量视频处理

使用 `auto_video_editor.py` 处理 Excel 表格驱动的批量视频制作。

## API 接口

### 核心操作

| 接口 | 方法 | 功能 |
|------|------|------|
| `/create_draft` | POST | 创建新草稿项目 |
| `/save_draft` | POST | 保存草稿并生成 URL |
| `/query_draft_status` | POST | 查询草稿状态 |
| `/query_script` | POST | 查询草稿脚本内容 |
| `/generate_draft_url` | POST | 生成草稿预览 URL |

### 素材添加

| 接口 | 方法 | 功能 |
|------|------|------|
| `/add_video` | POST | 添加视频轨道 |
| `/add_audio` | POST | 添加音频轨道 |
| `/add_image` | POST | 添加图片素材 |
| `/add_text` | POST | 添加文字元素 |
| `/add_subtitle` | POST | 添加 SRT 字幕 |
| `/add_sticker` | POST | 添加贴纸 |
| `/add_effect` | POST | 添加视频特效 |
| `/add_video_keyframe` | POST | 添加关键帧动画 |

### 查询接口 (GET)

| 接口 | 功能 |
|------|------|
| `/get_intro_animation_types` | 获取入场动画类型 |
| `/get_outro_animation_types` | 获取出场动画类型 |
| `/get_transition_types` | 获取转场效果类型 |
| `/get_mask_types` | 获取蒙版类型列表 |
| `/get_audio_effect_types` | 获取音频特效类型 |
| `/get_font_types` | 获取字体类型列表 |
| `/get_video_scene_effect_types` | 获取场景特效类型 |

## 使用示例

### 创建竖屏视频草稿

```python
import requests

# 1. 创建草稿
response = requests.post("http://localhost:9001/create_draft", json={
    "width": 1080,
    "height": 1920
})
draft_id = response.json()["output"]["draft_id"]

# 2. 添加背景视频
requests.post("http://localhost:9001/add_video", json={
    "draft_id": draft_id,
    "video_url": "https://example.com/background.mp4",
    "start": 0,
    "end": 10,
    "volume": 0.6
})

# 3. 添加标题文字
requests.post("http://localhost:9001/add_text", json={
    "draft_id": draft_id,
    "text": "欢迎使用 VectCutAPI",
    "start": 1,
    "end": 5,
    "font_size": 56,
    "font_color": "#FFD700",
    "shadow_enabled": True,
    "background_color": "#000000"
})

# 4. 保存草稿
response = requests.post("http://localhost:9001/save_draft", json={
    "draft_id": draft_id
})
draft_url = response.json()["output"]["draft_url"]
print(f"草稿已保存: {draft_url}")
```

### 添加转场效果

```python
requests.post("http://localhost:9001/add_video", json={
    "draft_id": draft_id,
    "video_url": "https://example.com/video2.mp4",
    "transition": "fade_in",           # 转场类型
    "transition_duration": 0.5,        # 转场时长(秒)
    "target_start": 10                 # 在时间轴 10 秒处开始
})
```

### 添加关键帧动画

```python
requests.post("http://localhost:9001/add_video_keyframe", json={
    "draft_id": draft_id,
    "track_name": "video_main",
    "property_types": ["scale_x", "scale_y", "alpha"],
    "times": [0, 2, 4],          # 关键帧时间点
    "values": ["1.0", "1.2", "0.8"]  # 对应属性值
})
```

### 添加 SRT 字幕

```python
requests.post("http://localhost:9001/add_subtitle", json={
    "draft_id": draft_id,
    "srt_url": "https://example.com/subtitles.srt",
    "font_size": 32,
    "font_color": "#FFFFFF",
    "background_alpha": 0.7
})
```

## MCP 协议集成

VectCutAPI 支持 MCP (Model Context Protocol) 协议，可直接由 AI Agent 调用。

### MCP 工具列表

| 工具名称 | 功能描述 |
|---------|----------|
| `create_draft` | 创建新的视频草稿项目 |
| `add_video` | 添加视频到草稿 |
| `add_audio` | 添加音频到草稿 |
| `add_image` | 添加图片素材 |
| `add_text` | 添加文字元素 |
| `add_subtitle` | 添加字幕文件 |
| `add_effect` | 添加视觉特效 |
| `add_sticker` | 添加贴纸元素 |
| `add_video_keyframe` | 添加关键帧动画 |
| `get_video_duration` | 获取视频时长 |
| `save_draft` | 保存草稿项目 |

### MCP 客户端配置

创建 `mcp_config.json`:

```json
{
  "mcpServers": {
    "vectcut-api": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "H:/ComfyUI/web/VectCutAPI",
      "env": {
        "PYTHONPATH": "H:/ComfyUI/web/VectCutAPI",
        "DEBUG": "0"
      }
    }
  }
}
```

## 参数说明

### 视频参数 (add_video)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `draft_id` | string | 必需 | 草稿 ID |
| `video_url` | string | 必需 | 视频 URL |
| `start` | float | 0 | 视频开始时间(秒) |
| `end` | float | 0 | 视频结束时间(秒) |
| `target_start` | float | 0 | 在时间轴上的开始时间 |
| `speed` | float | 1.0 | 播放速度 |
| `volume` | float | 1.0 | 音量 (0-1) |
| `scale_x/scale_y` | float | 1.0 | 缩放比例 |
| `transform_x/transform_y` | float | 0 | 位置偏移 |
| `transition` | string | - | 转场类型 |
| `transition_duration` | float | 0.5 | 转场时长(秒) |
| `mask_type` | string | - | 蒙版类型 |
| `background_blur` | int | - | 背景模糊级别(1-4) |

### 文字参数 (add_text)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | string | 必需 | 文字内容 |
| `start` | float | 必需 | 开始时间 |
| `end` | float | 必需 | 结束时间 |
| `font` | string | "思源黑体" | 字体名称 |
| `font_size` | int | 32 | 字体大小 |
| `font_color` | string | "#FFFFFF" | 字体颜色 (HEX) |
| `stroke_enabled` | bool | False | 是否启用描边 |
| `stroke_color` | string | "#FFFFFF" | 描边颜色 |
| `stroke_width` | float | 2.0 | 描边宽度 |
| `shadow_enabled` | bool | False | 是否启用阴影 |
| `shadow_color` | string | "#000000" | 阴影颜色 |
| `background_color` | string | - | 背景颜色 |
| `background_alpha` | float | 1.0 | 背景透明度 |
| `text_styles` | array | - | 多样式文字 (见下方) |

### 多样式文字 (text_styles)

```python
"text_styles": [
    {"start": 0, "end": 2, "font_color": "#FF6B6B"},
    {"start": 2, "end": 4, "font_color": "#4ECDC4"},
    {"start": 4, "end": 6, "font_color": "#45B7D1"}
]
```

## 配置文件

### config.json 结构

```json
{
  "is_capcut_env": true,
  "draft_domain": "https://www.capcutapi.top",
  "port": 9001,
  "preview_router": "/draft/downloader",
  "is_upload_draft": false,
  "oss_config": {
    "bucket_name": "your-bucket",
    "access_key_id": "your-key-id",
    "access_key_secret": "your-secret",
    "endpoint": "https://your-endpoint.aliyuncs.com"
  }
}
```

## 高级功能

### 批量视频处理

使用 `auto_video_editor.py` 进行 Excel 驱动的批量处理：

```python
python auto_video_editor.py input.xlsx
```

Excel 表格格式:
| 视频标题 | 二段文案 | 开头素材 | 结尾素材 | 封面素材 |
|---------|---------|---------|---------|---------|
| 产品介绍 | ... | video1.mp4 | video2.mp4 | image.png |

### n8n 工作流集成

项目包含多个预配置的 n8n 工作流：

- `text-to-video-with-animation.json` - 文字转视频工作流
- `auto-video-mixing.json` - 自动视频混剪
- `form-upload-processing.json` - 表单上传处理

## 资源

### scripts/

可执行脚本，用于 VectCutAPI 操作。

- **vectcut_client.py** - Python 客户端封装库

### references/

参考文档和指南。

- **api_reference.md** - 完整 API 接口参考
- **workflows.md** - 工作流示例和最佳实践
- **animation_types.md** - 动画类型参考
- **transition_types.md** - 转场效果类型参考

### assets/examples/

示例代码和模板。

- **basic_video.py** - 基础视频制作示例
- **text_animation.py** - 文字动画示例
- **subtitle_import.py** - 字幕导入示例
- **batch_processing.py** - 批量处理示例

## 常见问题

### 草稿文件位置

调用 `save_draft` 后会生成 `dfd_` 开头的草稿文件夹。启用本地自动部署时，工具会将草稿复制到 CapCut/JianYing 草稿目录，并同步把 JSON 中的素材路径改写为部署目录内的路径。

不要只根据 API 返回成功就宣称“可编辑”。本地交付必须重新打开目标工程验证：媒体库中的素材全部可预览，时间线没有红色缺失片段，且没有弹出“链接媒体”。如果工程被手动移动到另一个目录，绝对素材路径可能失效，需要重新链接或重新部署。

### 本地草稿交付检查

当 `save_draft` 用于桌面版 CapCut/JianYing 时，按以下顺序验收：

1. 确认返回的部署目录存在，并检查所有视频、音频和图片文件都存在。
2. 检查草稿内容文件中的媒体 `path` 指向部署目录，而不是 VectCutAPI 的临时或源代码目录。
3. 重新打开桌面应用中的草稿。
4. 只有在没有“链接媒体”提示、没有“暂无访问权限”红色片段、预览画面正常时，才报告工程交付完成。

如果第 3 或第 4 步无法执行，应明确报告“草稿已生成但尚未完成桌面端验收”，不要把生成成功等同于可编辑成功。

### 支持的视频格式

- MP4 (推荐)
- MOV
- AVI
- MKV

### 支持的图片格式

- PNG (推荐，支持透明)
- JPG/JPEG
- WebP

### 支持的音频格式

- MP3 (推荐)
- AAC
- WAV
- M4A

## 项目信息

- **GitHub**: https://github.com/sun-guannan/VectCutAPI
- **在线体验**: https://www.vectcut.com
- **开源协议**: Apache License 2.0
- **Star 数量**: 800+
