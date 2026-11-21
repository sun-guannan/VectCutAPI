# CapCut API MCP Server Documentation

## Overview

The CapCut API MCP Server is a video editing service based on the Model Context Protocol (MCP), providing complete CapCut video editing functionality interfaces. Through the MCP protocol, you can easily integrate professional-grade video editing capabilities into various applications.

## Features

### 🎬 Core Capabilities
- **Draft Management**: Create, save, and manage video projects
- **Multimedia Support**: Video, audio, image, and text processing
- **Advanced Effects**: Effects, animations, transitions, and filters
- **Precise Control**: Timeline, keyframes, and layer management

### 🛠️ Available Tools (11 Tools)

| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `create_draft` | Create new video draft project | width, height, fps |
| `add_text` | Add text elements | text, font_size, color, shadow, background |
| `add_video` | Add video track | video_url, start, end, transform, volume |
| `add_audio` | Add audio track | audio_url, volume, speed, effects |
| `add_image` | Add image assets | image_url, transform, animation, transition |
| `add_subtitle` | Add subtitle files | srt_path, font_style, position |
| `add_effect` | Add visual effects | effect_type, parameters, duration |
| `add_sticker` | Add sticker elements | resource_id, position, scale, rotation |
| `add_video_keyframe` | Add keyframe animations | property_types, times, values |
| `get_video_duration` | Get video duration | video_url |
| `save_draft` | Save draft project | draft_id |

## Installation & Setup

### Requirements
- Python 3.10+
- CapCut Application (macOS/Windows)
- MCP Client Support

### Dependencies Installation
```bash
# Create virtual environment
python3.10 -m venv venv-mcp
source venv-mcp/bin/activate  # macOS/Linux
# or venv-mcp\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-mcp.txt
```

### MCP Configuration
Create or update `mcp_config.json` file:

```json
{
  "mcpServers": {
    "capcut-api": {
      "command": "python3.10",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/CapCutAPI-dev",
      "env": {
        "PYTHONPATH": "/path/to/CapCutAPI-dev"
      }
    }
  }
}
```

## Usage Guide

### Basic Workflow

#### 1. Create Draft
```python
# Create 1080x1920 portrait project
result = mcp_client.call_tool("create_draft", {
    "width": 1080,
    "height": 1920
})
draft_id = result["draft_id"]
```

#### 2. Add Content
```python
# Add title text
mcp_client.call_tool("add_text", {
    "text": "My Video Title",
    "start": 0,
    "end": 5,
    "draft_id": draft_id,
    "font_size": 48,
    "font_color": "#FFFFFF"
})

# Add background video
mcp_client.call_tool("add_video", {
    "video_url": "https://example.com/video.mp4",
    "draft_id": draft_id,
    "start": 0,
    "end": 10,
    "volume": 0.8
})
```

#### 3. Save Project
```python
# Save draft
result = mcp_client.call_tool("save_draft", {
    "draft_id": draft_id
})
```

### Advanced Features

#### Text Styling
```python
# Text with shadow and background
mcp_client.call_tool("add_text", {
    "text": "Advanced Text Effects",
    "draft_id": draft_id,
    "font_size": 56,
    "font_color": "#FFD700",
    "shadow_enabled": True,
    "shadow_color": "#000000",
    "shadow_alpha": 0.8,
    "background_color": "#1E1E1E",
    "background_alpha": 0.7,
    "background_round_radius": 15
})
```

#### Keyframe Animation
```python
# Scale and opacity animation
mcp_client.call_tool("add_video_keyframe", {
    "draft_id": draft_id,
    "track_name": "video_main",
    "property_types": ["scale_x", "scale_y", "alpha"],
    "times": [0, 2, 4],
    "values": ["1.0", "1.5", "0.5"]
})
```

#### Multi-Style Text
```python
# Different colored text segments
mcp_client.call_tool("add_text", {
    "text": "Colorful Text Effect",
    "draft_id": draft_id,
    "text_styles": [
        {"start": 0, "end": 2, "font_color": "#FF0000"},
        {"start": 2, "end": 4, "font_color": "#00FF00"}
    ]
})
```

## Testing & Validation

### Using Test Client
```bash
# Run test client
python test_mcp_client.py
```

### Functionality Checklist
- [ ] Server starts successfully
- [ ] Tool list retrieval works
- [ ] Draft creation functionality
- [ ] Text addition functionality
- [ ] Video/audio/image addition
- [ ] Effects and animation functionality
- [ ] Draft saving functionality

## Troubleshooting

### Common Issues

#### 1. "CapCut modules not available"
**Solution**:
- Confirm CapCut application is installed
- Check Python path configuration
- Verify dependency package installation

#### 2. Server startup failure
**Solution**:
- Check virtual environment activation
- Verify configuration file paths
- Review error logs

#### 3. Tool call errors
**Solution**:
- Check parameter format
- Verify media file URLs
- Confirm time range settings

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=1
python mcp_server.py
```

## Best Practices

### Performance Optimization
1. **Media Files**: Use compressed formats, avoid oversized files
2. **Time Management**: Plan element timelines reasonably, avoid overlaps
3. **Memory Usage**: Save drafts promptly, clean temporary files

### Error Handling
1. **Parameter Validation**: Check required parameters before calling
2. **Exception Catching**: Handle network and file errors
3. **Retry Mechanism**: Retry on temporary failures

## API Reference

### Common Parameters
- `draft_id`: Unique draft identifier
- `start/end`: Time range (seconds)
- `width/height`: Project dimensions
- `transform_x/y`: Position coordinates
- `scale_x/y`: Scale ratios

### Response Format
```json
{
  "success": true,
  "result": {
    "draft_id": "dfd_cat_xxx",
    "draft_url": "https://..."
  },
  "features_used": {
    "shadow": false,
    "background": false,
    "multi_style": false
  }
}
```

## Changelog

### v1.0.0
- Initial release
- Support for 11 core tools
- Complete MCP protocol implementation

## Technical Support

For questions or suggestions, please contact us through:
- GitHub Issues
- Technical Documentation
- Community Forums

---

*This documentation is continuously updated. Please follow the latest version.*