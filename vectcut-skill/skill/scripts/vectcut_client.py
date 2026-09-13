#!/usr/bin/env python3
"""
VectCutAPI Python Client

A Python client library for VectCutAPI video editing service.
Provides a convenient interface for creating video drafts programmatically.

Usage:
    from vectcut_client import VectCutClient

    client = VectCutClient("http://localhost:9001")
    draft = client.create_draft(width=1080, height=1920)
    client.add_video(draft.draft_id, "https://example.com/video.mp4")
    client.add_text(draft.draft_id, "Hello World", start=0, end=5)
    result = client.save_draft(draft.draft_id)
    print(result.draft_url)
"""

import requests
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class Resolution(Enum):
    """常用视频分辨率预设"""
    VERTICAL = (1080, 1920)      # 竖屏 - TikTok/抖音
    HORIZONTAL = (1920, 1080)    # 横屏 - YouTube
    SQUARE = (1080, 1080)        # 方形 - Instagram
    WIDE = (1920, 1200)         # 宽屏


class Transition(Enum):
    """转场效果类型"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"


class TextAnimation(Enum):
    """文字动画类型"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SLIDE_IN_LEFT = "slide_in_left"
    SLIDE_IN_RIGHT = "slide_in_right"
    SLIDE_OUT_LEFT = "slide_out_left"
    SLIDE_OUT_RIGHT = "slide_out_right"
    ROTATE_IN = "rotate_in"
    ROTATE_OUT = "rotate_out"


@dataclass
class DraftInfo:
    """草稿信息"""
    draft_id: str
    draft_folder: Optional[str] = None
    draft_url: Optional[str] = None

    def __str__(self):
        return f"Draft(id={self.draft_id}, url={self.draft_url})"


@dataclass
class ApiResult:
    """API 响应结果"""
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None

    @property
    def draft_id(self) -> Optional[str]:
        return self.output.get("draft_id")

    @property
    def draft_url(self) -> Optional[str]:
        return self.output.get("draft_url")

    @property
    def draft_folder(self) -> Optional[str]:
        return self.output.get("draft_folder")


class VectCutClient:
    """
    VectCutAPI Python 客户端

    提供简洁的接口来操作 VectCutAPI 视频编辑服务。
    """

    def __init__(self, base_url: str = "http://localhost:9001", timeout: int = 120):
        """
        初始化客户端

        Args:
            base_url: API 服务器地址
            timeout: 请求超时时间(秒)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _post(self, endpoint: str, **kwargs) -> ApiResult:
        """
        发送 POST 请求

        Args:
            endpoint: API 端点
            **kwargs: 请求参数

        Returns:
            ApiResult: API 响应结果
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=kwargs, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return ApiResult(
                success=data.get("success", False),
                output=data.get("output", {}),
                error=data.get("error")
            )
        except requests.RequestException as e:
            return ApiResult(success=False, output={}, error=str(e))

    def _get(self, endpoint: str) -> Any:
        """
        发送 GET 请求

        Args:
            endpoint: API 端点

        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    # ==================== 核心操作 ====================

    def create_draft(self,
                    width: int = 1080,
                    height: int = 1920,
                    draft_folder: Optional[str] = None) -> DraftInfo:
        """
        创建新草稿

        Args:
            width: 视频宽度
            height: 视频高度
            draft_folder: 草稿文件夹路径

        Returns:
            DraftInfo: 草稿信息
        """
        result = self._post("/create_draft",
                           width=width,
                           height=height,
                           draft_folder=draft_folder)
        if result.success:
            return DraftInfo(
                draft_id=result.draft_id,
                draft_folder=result.draft_folder
            )
        raise Exception(f"创建草稿失败: {result.error}")

    def save_draft(self,
                  draft_id: str,
                  draft_folder: Optional[str] = None,
                  project_name: Optional[str] = None,
                  auto_deploy: bool = True) -> DraftInfo:
        """
        保存草稿并生成下载链接

        Args:
            draft_id: 草稿 ID
            draft_folder: 草稿文件夹路径
            project_name: 自动部署到桌面端时使用的草稿名称
            auto_deploy: 是否自动复制到本机剪映/CapCut 草稿目录

        Returns:
            DraftInfo: 包含 draft_url 的草稿信息
        """
        result = self._post("/save_draft",
                           draft_id=draft_id,
                           draft_folder=draft_folder,
                           project_name=project_name,
                           auto_deploy=auto_deploy)
        if result.success:
            return DraftInfo(
                draft_id=draft_id,
                draft_folder=result.draft_folder,
                draft_url=result.draft_url
            )
        raise Exception(f"保存草稿失败: {result.error}")

    def query_draft_status(self, draft_id: str) -> Dict[str, Any]:
        """查询草稿状态"""
        return self._post("/query_draft_status", draft_id=draft_id)

    def query_script(self, draft_id: str) -> Dict[str, Any]:
        """查询草稿脚本内容"""
        return self._post("/query_script", draft_id=draft_id)

    # ==================== 素材添加 ====================

    def add_video(self,
                 draft_id: str,
                 video_url: str,
                 start: float = 0,
                 end: float = 0,
                 target_start: float = 0,
                 speed: float = 1.0,
                 volume: float = 1.0,
                 scale_x: float = 1.0,
                 scale_y: float = 1.0,
                 transform_x: float = 0,
                 transform_y: float = 0,
                 track_name: str = "video_main",
                 transition: Optional[str] = None,
                 transition_duration: float = 0.5,
                 mask_type: Optional[str] = None,
                 background_blur: Optional[int] = None,
                 **kwargs) -> bool:
        """
        添加视频轨道

        Args:
            draft_id: 草稿 ID
            video_url: 视频 URL
            start: 视频开始时间(秒)
            end: 视频结束时间(秒)
            target_start: 在时间轴上的开始时间
            speed: 播放速度
            volume: 音量 (0.0-1.0)
            scale_x/scale_y: 缩放比例
            transform_x/transform_y: 位置偏移
            track_name: 轨道名称
            transition: 转场类型
            transition_duration: 转场时长(秒)
            mask_type: 蒙版类型
            background_blur: 背景模糊级别(1-4)

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_video",
                           draft_id=draft_id,
                           video_url=video_url,
                           start=start,
                           end=end,
                           target_start=target_start,
                           speed=speed,
                           volume=volume,
                           scale_x=scale_x,
                           scale_y=scale_y,
                           transform_x=transform_x,
                           transform_y=transform_y,
                           track_name=track_name,
                           transition=transition,
                           transition_duration=transition_duration,
                           mask_type=mask_type,
                           background_blur=background_blur,
                           **kwargs)
        return result.success

    def add_audio(self,
                 draft_id: str,
                 audio_url: str,
                 start: float = 0,
                 end: Optional[float] = None,
                 target_start: float = 0,
                 speed: float = 1.0,
                 volume: float = 1.0,
                 track_name: str = "audio_main",
                 **kwargs) -> bool:
        """
        添加音频轨道

        Args:
            draft_id: 草稿 ID
            audio_url: 音频 URL
            start: 音频开始时间
            end: 音频结束时间
            target_start: 在时间轴上的开始时间
            speed: 播放速度
            volume: 音量 (0.0-1.0)
            track_name: 轨道名称

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_audio",
                           draft_id=draft_id,
                           audio_url=audio_url,
                           start=start,
                           end=end,
                           target_start=target_start,
                           speed=speed,
                           volume=volume,
                           track_name=track_name,
                           **kwargs)
        return result.success

    def add_image(self,
                 draft_id: str,
                 image_url: str,
                 start: float,
                 end: float,
                 target_start: float = 0,
                 scale_x: float = 1.0,
                 scale_y: float = 1.0,
                 transform_x: float = 0,
                 transform_y: float = 0,
                 animation_type: Optional[str] = None,
                 transition: Optional[str] = None,
                 **kwargs) -> bool:
        """
        添加图片素材

        Args:
            draft_id: 草稿 ID
            image_url: 图片 URL
            start: 开始时间
            end: 结束时间
            target_start: 在时间轴上的开始时间
            scale_x/scale_y: 缩放比例
            transform_x/transform_y: 位置偏移
            animation_type: 动画类型
            transition: 转场类型

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_image",
                           draft_id=draft_id,
                           image_url=image_url,
                           start=start,
                           end=end,
                           target_start=target_start,
                           scale_x=scale_x,
                           scale_y=scale_y,
                           transform_x=transform_x,
                           transform_y=transform_y,
                           animation_type=animation_type,
                           transition=transition,
                           **kwargs)
        return result.success

    def add_text(self,
                draft_id: str,
                text: str,
                start: float,
                end: float,
                font: str = "思源黑体",
                font_size: int = 32,
                font_color: str = "#FFFFFF",
                stroke_enabled: bool = False,
                stroke_color: str = "#FFFFFF",
                stroke_width: float = 2.0,
                shadow_enabled: bool = False,
                shadow_color: str = "#000000",
                background_color: Optional[str] = None,
                background_alpha: float = 1.0,
                background_round_radius: float = 0,
                text_intro: Optional[str] = None,
                text_outro: Optional[str] = None,
                text_styles: Optional[List[Dict]] = None,
                pos_x: float = 0,
                pos_y: float = 0,
                alignment_h: str = "center",
                alignment_v: str = "middle",
                **kwargs) -> bool:
        """
        添加文字元素

        Args:
            draft_id: 草稿 ID
            text: 文字内容
            start: 开始时间
            end: 结束时间
            font: 字体名称
            font_size: 字体大小
            font_color: 字体颜色 (HEX)
            stroke_enabled: 是否启用描边
            stroke_color: 描边颜色
            stroke_width: 描边宽度
            shadow_enabled: 是否启用阴影
            shadow_color: 阴影颜色
            background_color: 背景颜色
            background_alpha: 背景透明度
            background_round_radius: 背景圆角半径
            text_intro: 入场动画
            text_outro: 出场动画
            text_styles: 多样式文字
            pos_x/pos_y: 位置
            alignment_h: 水平对齐
            alignment_v: 垂直对齐

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_text",
                           draft_id=draft_id,
                           text=text,
                           start=start,
                           end=end,
                           font=font,
                           font_size=font_size,
                           font_color=font_color,
                           stroke_enabled=stroke_enabled,
                           stroke_color=stroke_color,
                           stroke_width=stroke_width,
                           shadow_enabled=shadow_enabled,
                           shadow_color=shadow_color,
                           background_color=background_color,
                           background_alpha=background_alpha,
                           background_round_radius=background_round_radius,
                           text_intro=text_intro,
                           text_outro=text_outro,
                           text_styles=text_styles,
                           pos_x=pos_x,
                           pos_y=pos_y,
                           alignment_h=alignment_h,
                           alignment_v=alignment_v,
                           **kwargs)
        return result.success

    def add_subtitle(self,
                    draft_id: str,
                    srt_url: str,
                    font: str = "思源黑体",
                    font_size: int = 32,
                    font_color: str = "#FFFFFF",
                    stroke_enabled: bool = True,
                    stroke_color: str = "#000000",
                    stroke_width: float = 3.0,
                    background_alpha: float = 0.5,
                    pos_y: float = -0.3,
                    time_offset: float = 0,
                    **kwargs) -> bool:
        """
        添加 SRT 字幕

        Args:
            draft_id: 草稿 ID
            srt_url: SRT 文件 URL
            font: 字体名称
            font_size: 字体大小
            font_color: 字体颜色
            stroke_enabled: 是否启用描边
            stroke_color: 描边颜色
            stroke_width: 描边宽度
            background_alpha: 背景透明度
            pos_y: 垂直位置
            time_offset: 时间偏移(秒)

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_subtitle",
                           draft_id=draft_id,
                           srt_url=srt_url,
                           font=font,
                           font_size=font_size,
                           font_color=font_color,
                           stroke_enabled=stroke_enabled,
                           stroke_color=stroke_color,
                           stroke_width=stroke_width,
                           background_alpha=background_alpha,
                           pos_y=pos_y,
                           time_offset=time_offset,
                           **kwargs)
        return result.success

    def add_sticker(self,
                   draft_id: str,
                   sticker_id: str,
                   start: float,
                   end: float,
                   target_start: float = 0,
                   scale_x: float = 1.0,
                   scale_y: float = 1.0,
                   transform_x: float = 0,
                   transform_y: float = 0,
                   flip_horizontal: bool = False,
                   flip_vertical: bool = False,
                   alpha: float = 1.0,
                   **kwargs) -> bool:
        """
        添加贴纸

        Args:
            draft_id: 草稿 ID
            sticker_id: 贴纸 ID
            start: 开始时间
            end: 结束时间
            target_start: 在时间轴上的开始时间
            scale_x/scale_y: 缩放比例
            transform_x/transform_y: 位置偏移
            flip_horizontal: 水平翻转
            flip_vertical: 垂直翻转
            alpha: 透明度

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_sticker",
                           draft_id=draft_id,
                           sticker_id=sticker_id,
                           start=start,
                           end=end,
                           target_start=target_start,
                           scale_x=scale_x,
                           scale_y=scale_y,
                           transform_x=transform_x,
                           transform_y=transform_y,
                           flip_horizontal=flip_horizontal,
                           flip_vertical=flip_vertical,
                           alpha=alpha,
                           **kwargs)
        return result.success

    def add_effect(self,
                  draft_id: str,
                  effect_type: str,
                  start: float,
                  end: float,
                  target_start: float = 0,
                  intensity: float = 1.0,
                  effect_params: Optional[List] = None,
                  **kwargs) -> bool:
        """
        添加视频特效

        Args:
            draft_id: 草稿 ID
            effect_type: 特效类型
            start: 开始时间
            end: 结束时间
            target_start: 在时间轴上的开始时间
            intensity: 特效强度
            effect_params: 特效参数

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_effect",
                           draft_id=draft_id,
                           effect_type=effect_type,
                           start=start,
                           end=end,
                           target_start=target_start,
                           intensity=intensity,
                           effect_params=effect_params,
                           **kwargs)
        return result.success

    def add_video_keyframe(self,
                          draft_id: str,
                          track_name: str,
                          property_types: List[str],
                          times: List[float],
                          values: List[str],
                          **kwargs) -> bool:
        """
        添加关键帧动画

        Args:
            draft_id: 草稿 ID
            track_name: 轨道名称
            property_types: 属性类型列表
            times: 关键帧时间点
            values: 对应属性值

        Returns:
            bool: 是否成功
        """
        result = self._post("/add_video_keyframe",
                           draft_id=draft_id,
                           track_name=track_name,
                           property_types=property_types,
                           times=times,
                           values=values,
                           **kwargs)
        return result.success

    # ==================== 查询接口 ====================

    def get_intro_animation_types(self) -> List[str]:
        """获取入场动画类型列表"""
        return self._get("/get_intro_animation_types")

    def get_outro_animation_types(self) -> List[str]:
        """获取出场动画类型列表"""
        return self._get("/get_outro_animation_types")

    def get_transition_types(self) -> List[str]:
        """获取转场效果类型列表"""
        return self._get("/get_transition_types")

    def get_mask_types(self) -> List[str]:
        """获取蒙版类型列表"""
        return self._get("/get_mask_types")

    def get_audio_effect_types(self) -> List[str]:
        """获取音频特效类型列表"""
        return self._get("/get_audio_effect_types")

    def get_font_types(self) -> List[str]:
        """获取字体类型列表"""
        return self._get("/get_font_types")

    def get_text_intro_types(self) -> List[str]:
        """获取文字入场动画列表"""
        return self._get("/get_text_intro_types")

    def get_text_outro_types(self) -> List[str]:
        """获取文字出场动画列表"""
        return self._get("/get_text_outro_types")

    def get_video_scene_effect_types(self) -> List[str]:
        """获取场景特效类型列表"""
        return self._get("/get_video_scene_effect_types")

    # ==================== 工具方法 ====================

    def get_duration(self, media_url: str) -> Optional[float]:
        """
        获取媒体文件时长

        Args:
            media_url: 媒体 URL

        Returns:
            时长(秒)，失败返回 None
        """
        result = self._post("/get_duration", media_url=media_url)
        if result.success:
            return result.output.get("duration")
        return None

    def close(self):
        """关闭客户端会话"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ==================== 便捷函数 ====================

def create_quick_video(base_url: str = "http://localhost:9001",
                      video_url: str = "",
                      text_content: str = "",
                      bgm_url: str = "",
                      resolution: Resolution = Resolution.VERTICAL) -> Optional[str]:
    """
    快速创建简单视频

    Args:
        base_url: API 服务器地址
        video_url: 背景视频 URL
        text_content: 文字内容
        bgm_url: 背景音乐 URL
        resolution: 视频分辨率

    Returns:
        草稿 URL，失败返回 None
    """
    with VectCutClient(base_url) as client:
        draft = client.create_draft(width=resolution.value[0], height=resolution.value[1])

        if video_url:
            client.add_video(draft.draft_id, video_url)

        if bgm_url:
            client.add_audio(draft.draft_id, bgm_url, volume=0.3)

        if text_content:
            client.add_text(
                draft.draft_id,
                text_content,
                start=1,
                end=5,
                font_size=56,
                shadow_enabled=True,
                background_alpha=0.7
            )

        result = client.save_draft(draft.draft_id)
        return result.draft_url


if __name__ == "__main__":
    # 示例用法
    with VectCutClient() as client:
        # 创建草稿
        draft = client.create_draft(width=1080, height=1920)
        print(f"创建草稿: {draft.draft_id}")

        # 添加视频
        client.add_video(
            draft.draft_id,
            "https://example.com/video.mp4",
            volume=0.6
        )

        # 添加文字
        client.add_text(
            draft.draft_id,
            "Hello VectCutAPI!",
            start=0,
            end=5,
            font_size=64,
            font_color="#FFD700",
            shadow_enabled=True
        )

        # 保存草稿
        result = client.save_draft(draft.draft_id)
        print(f"草稿已保存: {result.draft_url}")
