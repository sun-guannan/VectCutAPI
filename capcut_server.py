import requests
from flask import Flask, request, jsonify, Response
from datetime import datetime
import pyJianYingDraft as draft
from pyJianYingDraft.metadata.animation_meta import Intro_type, Outro_type, Group_animation_type
from pyJianYingDraft.metadata.capcut_animation_meta import CapCut_Intro_type, CapCut_Outro_type, CapCut_Group_animation_type
from pyJianYingDraft.metadata.transition_meta import Transition_type
from pyJianYingDraft.metadata.capcut_transition_meta import CapCut_Transition_type
from pyJianYingDraft.metadata.mask_meta import Mask_type
from pyJianYingDraft.metadata.capcut_mask_meta import CapCut_Mask_type
from pyJianYingDraft.metadata.audio_effect_meta import Tone_effect_type, Audio_scene_effect_type, Speech_to_song_type
from pyJianYingDraft.metadata.capcut_audio_effect_meta import CapCut_Voice_filters_effect_type, CapCut_Voice_characters_effect_type, CapCut_Speech_to_song_effect_type
from pyJianYingDraft.metadata.font_meta import Font_type
from pyJianYingDraft.metadata.animation_meta import Text_intro, Text_outro, Text_loop_anim
from pyJianYingDraft.metadata.capcut_text_animation_meta import CapCut_Text_intro, CapCut_Text_outro, CapCut_Text_loop_anim
from pyJianYingDraft.metadata.video_effect_meta import Video_scene_effect_type, Video_character_effect_type
from pyJianYingDraft.metadata.capcut_effect_meta import CapCut_Video_scene_effect_type, CapCut_Video_character_effect_type
import random
import uuid
import json
import codecs
from add_audio_track import add_audio_track
from add_video_track import add_video_track
from add_text_impl import add_text_impl
from add_subtitle_impl import add_subtitle_impl
from add_image_impl import add_image_impl
from add_video_keyframe_impl import add_video_keyframe_impl
from save_draft_impl import save_draft_impl, query_task_status, query_script_impl
from add_effect_impl import add_effect_impl
from add_sticker_impl import add_sticker_impl
from create_draft import create_draft
from util import generate_draft_url as utilgenerate_draft_url, hex_to_rgb
from pyJianYingDraft.text_segment import TextStyleRange, Text_style, Text_border

from settings.local import IS_CAPCUT_ENV, DRAFT_DOMAIN, PREVIEW_ROUTER, PORT

app = Flask(__name__)
 
@app.route('/add_video', methods=['POST'])
def add_video():
    data = request.get_json()
    # Get required parameters
    draft_folder = data.get('draft_folder')
    video_url = data.get('video_url')
    start = data.get('start', 0)
    end = data.get('end', 0)
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    scale_x = data.get('scale_x', 1)
    scale_y = data.get('scale_y', 1)
    transform_x = data.get('transform_x', 0)
    speed = data.get('speed', 1.0)  # New speed parameter
    target_start = data.get('target_start', 0)  # New target start time parameter
    track_name = data.get('track_name', "video_main")  # New track name parameter
    relative_index = data.get('relative_index', 0)  # New relative index parameter
    duration = data.get('duration')  # New duration parameter
    transition = data.get('transition')  # New transition type parameter
    transition_duration = data.get('transition_duration', 0.5)  # New transition duration parameter, default 0.5 seconds
    filter_type = data.get('filter_type')  # [本地补丁] 剪映滤镜名
    filter_intensity = data.get('filter_intensity', 100.0)  # [本地补丁] 滤镜强度0-100
    volume = data.get('volume', 1.0)  # New volume parameter, default 1.0 
    
    # Get mask related parameters
    mask_type = data.get('mask_type')  # Mask type
    mask_center_x = data.get('mask_center_x', 0.5)  # Mask center X coordinate
    mask_center_y = data.get('mask_center_y', 0.5)  # Mask center Y coordinate
    mask_size = data.get('mask_size', 1.0)  # Mask size, relative to screen height
    mask_rotation = data.get('mask_rotation', 0.0)  # Mask rotation angle
    mask_feather = data.get('mask_feather', 0.0)  # Mask feather degree
    mask_invert = data.get('mask_invert', False)  # Whether to invert mask
    mask_rect_width = data.get('mask_rect_width')  # Rectangle mask width
    mask_round_corner = data.get('mask_round_corner')  # Rectangle mask rounded corner

    background_blur = data.get('background_blur')  # Background blur level, optional values: 1 (light), 2 (medium), 3 (strong), 4 (maximum), default None (no background blur)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not video_url:
        error_message = "Hi, the required parameters 'video_url' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        draft_result = add_video_track(
            draft_folder=draft_folder,
            video_url=video_url,
            width=width,
            height=height,
            start=start,
            end=end,
            target_start=target_start,
            draft_id=draft_id,
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x,
            speed=speed,
            track_name=track_name,
            relative_index=relative_index,
            duration=duration,
            transition=transition,  # Pass transition type parameter
            transition_duration=transition_duration,  # Pass transition duration parameter
            filter_type=filter_type,  # [本地补丁] 滤镜透传
            filter_intensity=filter_intensity,  # [本地补丁]
            volume=volume,  # Pass volume parameter
            # Pass mask related parameters
            mask_type=mask_type,
            mask_center_x=mask_center_x,
            mask_center_y=mask_center_y,
            mask_size=mask_size,
            mask_rotation=mask_rotation,
            mask_feather=mask_feather,
            mask_invert=mask_invert,
            mask_rect_width=mask_rect_width,
            mask_round_corner=mask_round_corner,
            background_blur=background_blur
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing video: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_audio', methods=['POST'])
def add_audio():
    data = request.get_json()
    
    # Get required parameters
    draft_folder = data.get('draft_folder')
    audio_url = data.get('audio_url')
    start = data.get('start', 0)
    end = data.get('end', None)
    draft_id = data.get('draft_id')
    volume = data.get('volume', 1.0)  # Default volume 1.0
    target_start = data.get('target_start', 0)  # New target start time parameter
    speed = data.get('speed', 1.0)  # New speed parameter
    track_name = data.get('track_name', 'audio_main')  # New track name parameter
    duration = data.get('duration', None)  # New duration parameter
    # Get audio effect parameters separately
    effect_type = data.get('effect_type', None)  # Audio effect type name
    effect_params = data.get('effect_params', None)  # Audio effect parameter list
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    
    # # If there are audio effect parameters, combine them into sound_effects format
    sound_effects = None
    if effect_type is not None:
        sound_effects = [(effect_type, effect_params)]

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not audio_url:
        error_message = "Hi, the required parameters 'audio_url' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        # Call the modified add_audio_track method
        draft_result = add_audio_track(
            draft_folder=draft_folder,
            audio_url=audio_url,
            start=start,
            end=end,
            target_start=target_start,
            draft_id=draft_id,
            volume=volume,
            track_name=track_name,
            speed=speed,
            sound_effects=sound_effects,  # Add audio effect parameters
            width=width,
            height=height,
            duration=duration  # Add duration parameter
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing audio: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/create_draft', methods=['POST'])
def create_draft_service():
    data = request.get_json()
    
    # Get parameters
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    try:
        # Create new draft
        script, draft_id = create_draft(width=width, height=height)
        
        result["success"] = True
        result["output"] = {
            "draft_id": draft_id,
            "draft_url": utilgenerate_draft_url(draft_id)
        }
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while creating draft: {str(e)}."
        result["error"] = error_message
        return jsonify(result)
        
@app.route('/add_subtitle', methods=['POST'])
def add_subtitle():
    data = request.get_json()
    
    # Get required parameters
    srt = data.get('srt')  # Subtitle content or URL
    draft_id = data.get('draft_id')
    time_offset = data.get('time_offset', 0.0)  # Default 0 seconds
    
    # Font style parameters
    font = data.get('font', "思源粗宋")
    font_size = data.get('font_size', 5.0)  # Default size 5.0
    bold = data.get('bold', False)  # Default not bold
    italic = data.get('italic', False)  # Default not italic
    underline = data.get('underline', False)  # Default no underline
    font_color = data.get('font_color', '#FFFFFF')  # Default white
    vertical = data.get('vertical', False)  # New: whether to display vertically, default False
    alpha = data.get('alpha', 1)  # New: transparency, default 1
    # Border parameters
    border_alpha = data.get('border_alpha', 1.0)
    border_color = data.get('border_color', '#000000')
    border_width = data.get('border_width', 0.0)
    
    # Background parameters
    background_color = data.get('background_color', '#000000')
    background_style = data.get('background_style', 0)
    background_alpha = data.get('background_alpha', 0.0)
        
    # Image adjustment parameters
    transform_x = data.get('transform_x', 0.0)  # Default 0
    transform_y = data.get('transform_y', -0.8)  # Default -0.8
    scale_x = data.get('scale_x', 1.0)  # Default 1.0
    scale_y = data.get('scale_y', 1.0)  # Default 1.0
    rotation = data.get('rotation', 0.0)  # Default 0.0
    track_name = data.get('track_name', 'subtitle')  # Default track name is 'subtitle'
    width = data.get('width', 1080)
    height = data.get('height', 1920)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not srt:
        error_message = "Hi, the required parameters 'srt' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        # Call add_subtitle_impl method
        draft_result = add_subtitle_impl(
            srt_path=srt,
            draft_id=draft_id,
            track_name=track_name,
            time_offset=time_offset,
            # Font style parameters
            font = font,
            font_size=font_size,
            bold=bold,
            italic=italic,
            underline=underline,
            font_color=font_color,
            vertical=vertical,  # New: pass vertical parameter
            alpha=alpha,  # New: pass alpha parameter
            border_alpha=border_alpha,
            border_color=border_color,
            border_width=border_width,
            background_color=background_color,
            background_style=background_style,
            background_alpha=background_alpha,
            # Image adjustment parameters
            transform_x=transform_x,
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            rotation=rotation,
            width=width,
            height=height
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing subtitle: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_text', methods=['POST'])
def add_text():
    data = request.get_json()
    
    # Get required parameters
    text = data.get('text')
    start = data.get('start', 0)
    end = data.get('end', 5)
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    transform_x = data.get('transform_x', 0)
    font = data.get('font', "文轩体")
    font_color = data.get('color', data.get('font_color', "#FF0000"))  # Support both 'color' and 'font_color'
    font_size = data.get('size', data.get('font_size', 8.0))  # Support both 'size' and 'font_size'
    track_name = data.get('track_name', "text_main")
    vertical = data.get('vertical', False)
    font_alpha = data.get('alpha', data.get('font_alpha', 1.0))  # Support both 'alpha' and 'font_alpha'  
    outro_animation = data.get('outro_animation', None)
    outro_duration = data.get('outro_duration', 0.5)
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    
    # New fixed width and height parameters 
    fixed_width = data.get('fixed_width', -1)
    fixed_height = data.get('fixed_height', -1)
    
    # Border parameters
    border_alpha = data.get('border_alpha', 1.0)
    border_color = data.get('border_color', "#000000")
    border_width = data.get('border_width', 0.0)
    
    # Background parameters
    background_color = data.get('background_color', "#000000")
    background_style = data.get('background_style', 0)
    background_alpha = data.get('background_alpha', 0.0)
    background_round_radius = data.get('background_round_radius', 0.0)
    background_height = data.get('background_height', 0.14)  # Background height, range 0.0-1.0
    background_width = data.get('background_width', 0.14)  # Background width, range 0.0-1.0
    background_horizontal_offset = data.get('background_horizontal_offset', 0.5)  # Background horizontal offset, range 0.0-1.0
    background_vertical_offset = data.get('background_vertical_offset', 0.5)  # Background vertical offset, range 0.0-1.0

    # Shadow parameters
    shadow_enabled = data.get('shadow_enabled', False)  # Whether to enable shadow
    shadow_alpha = data.get('shadow_alpha', 0.9)  # Shadow transparency, range 0.0-1.0
    shadow_angle = data.get('shadow_angle', -45.0)  # Shadow angle, range -180.0-180.0
    shadow_color = data.get('shadow_color', "#000000")  # Shadow color
    shadow_distance = data.get('shadow_distance', 5.0)  # Shadow distance
    shadow_smoothing = data.get('shadow_smoothing', 0.15)  # Shadow smoothing, range 0.0-1.0
    
    # Bubble and decorative text effects
    bubble_effect_id = data.get('bubble_effect_id')
    bubble_resource_id = data.get('bubble_resource_id')
    effect_effect_id = data.get('effect_effect_id')
    
    # Entrance animation
    intro_animation = data.get('intro_animation')
    intro_duration = data.get('intro_duration', 0.5)
    
    # Exit animation
    outro_animation = data.get('outro_animation')
    outro_duration = data.get('outro_duration', 0.5)

    # Multi-style text parameters
    text_styles_data = data.get('text_styles', [])
    text_styles = None
    if text_styles_data:
        text_styles = []
        for style_data in text_styles_data:
            # Get style range
            start_pos = style_data.get('start', 0)
            end_pos = style_data.get('end', 0)
            
            # Create text style
            style = Text_style(
                size=style_data.get('style',{}).get('size', font_size),
                bold=style_data.get('style',{}).get('bold', False),
                italic=style_data.get('style',{}).get('italic', False),
                underline=style_data.get('style',{}).get('underline', False),
                color=hex_to_rgb(style_data.get('style',{}).get('color', font_color)),
                alpha=style_data.get('style',{}).get('alpha', font_alpha),
                align=style_data.get('style',{}).get('align', 1),
                vertical=style_data.get('style',{}).get('vertical', vertical),
                letter_spacing=style_data.get('style',{}).get('letter_spacing', 0),
                line_spacing=style_data.get('style',{}).get('line_spacing', 0)
            )
            
            # Create border (if any)
            border = None
            if style_data.get('border',{}).get('width', 0) > 0:
                border = Text_border(
                    alpha=style_data.get('border',{}).get('alpha', border_alpha),
                    color=hex_to_rgb(style_data.get('border',{}).get('color', border_color)),
                    width=style_data.get('border',{}).get('width', border_width)
                )
            
            # Create style range object
            style_range = TextStyleRange(
                start=start_pos,
                end=end_pos,
                style=style,
                border=border,
                font_str=style_data.get('font', font)
            )
            
            text_styles.append(style_range)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not text or start is None or end is None:
        error_message = "Hi, the required parameters 'text', 'start' or 'end' are missing. "
        result["error"] = error_message
        return jsonify(result)

    try:
        
        # Call add_text_impl method
        draft_result = add_text_impl(
            text=text,
            start=start,
            end=end,
            draft_id=draft_id,
            transform_y=transform_y,
            transform_x=transform_x,
            font=font,
            font_color=font_color,
            font_size=font_size,
            track_name=track_name,
            vertical=vertical,
            font_alpha=font_alpha,
            border_alpha=border_alpha,
            border_color=border_color,
            border_width=border_width,
            background_color=background_color,
            background_style=background_style,
            background_alpha=background_alpha,
            background_round_radius=background_round_radius,
            background_height=background_height,
            background_width=background_width,
            background_horizontal_offset=background_horizontal_offset,
            background_vertical_offset=background_vertical_offset,
            shadow_enabled=shadow_enabled,
            shadow_alpha=shadow_alpha,
            shadow_angle=shadow_angle,
            shadow_color=shadow_color,
            shadow_distance=shadow_distance,
            shadow_smoothing=shadow_smoothing,
            bubble_effect_id=bubble_effect_id,
            bubble_resource_id=bubble_resource_id,
            effect_effect_id=effect_effect_id,
            intro_animation=intro_animation,
            intro_duration=intro_duration,
            outro_animation=outro_animation,
            outro_duration=outro_duration,
            width=width,
            height=height,
            fixed_width=fixed_width,
            fixed_height=fixed_height,
            text_styles=text_styles
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing text: {str(e)}. You can click the link below for help: "
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_image', methods=['POST'])
def add_image():
    data = request.get_json()
    
    # Get required parameters
    draft_folder = data.get('draft_folder')
    image_url = data.get('image_url')
    width = data.get('width', 1080)
    height = data.get('height', 1920)
    start = data.get('start', 0)
    end = data.get('end', 3.0)  # Default display 3 seconds
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    scale_x = data.get('scale_x', 1)
    scale_y = data.get('scale_y', 1)
    transform_x = data.get('transform_x', 0)
    track_name = data.get('track_name', "image_main")  # Default track name
    relative_index = data.get('relative_index', 0)  # New track rendering order index parameter 
    animation = data.get('animation')  # Entrance animation parameter (backward compatibility)
    animation_duration = data.get('animation_duration', 0.5)  # Entrance animation duration
    intro_animation = data.get('intro_animation')  # New entrance animation parameter, higher priority than animation
    intro_animation_duration = data.get('intro_animation_duration', 0.5)
    outro_animation = data.get('outro_animation')  # New exit animation parameter
    outro_animation_duration = data.get('outro_animation_duration', 0.5)  # New exit animation duration
    combo_animation = data.get('combo_animation')  # New combo animation parameter
    combo_animation_duration = data.get('combo_animation_duration', 0.5)  # New combo animation duration
    transition = data.get('transition')  # Transition type parameter
    transition_duration = data.get('transition_duration', 0.5)  # Transition duration parameter, default 0.5 seconds
    
    # New mask related parameters 
    mask_type = data.get('mask_type')  # Mask type
    mask_center_x = data.get('mask_center_x', 0.0)  # Mask center X coordinate
    mask_center_y = data.get('mask_center_y', 0.0)  # Mask center Y coordinate
    mask_size = data.get('mask_size', 0.5)  # Mask main size, relative to canvas height
    mask_rotation = data.get('mask_rotation', 0.0)  # Mask rotation angle
    mask_feather = data.get('mask_feather', 0.0)  # Mask feather parameter
    mask_invert = data.get('mask_invert', False)  # Whether to invert mask
    mask_rect_width = data.get('mask_rect_width')  # Rectangle mask width
    mask_round_corner = data.get('mask_round_corner')  # Rectangle mask rounded corner

    background_blur = data.get('background_blur')  # Background blur level, optional values: 1 (light), 2 (medium), 3 (strong), 4 (maximum), default None (no background blur)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not image_url:
        error_message = "Hi, the required parameters 'image_url' are missing."
        result["error"] = error_message
        return jsonify(result)

    try:
        draft_result = add_image_impl(
            draft_folder=draft_folder,
            image_url=image_url,
            width=width,
            height=height,
            start=start,
            end=end,
            draft_id=draft_id,
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x,
            track_name=track_name,
            relative_index=relative_index,  # Pass track rendering order index parameter
            animation=animation,  # Pass entrance animation parameter (backward compatibility)
            animation_duration=animation_duration,  # Pass entrance animation duration
            intro_animation=intro_animation,  # Pass new entrance animation parameter
            intro_animation_duration=intro_animation_duration,
            outro_animation=outro_animation,  # Pass exit animation parameter
            outro_animation_duration=outro_animation_duration,  # Pass exit animation duration
            combo_animation=combo_animation,  # Pass combo animation parameter
            combo_animation_duration=combo_animation_duration,  # Pass combo animation duration
            transition=transition,  # Pass transition type parameter
            transition_duration=transition_duration,  # Pass transition duration parameter
            filter_type=filter_type,  # [本地补丁] 滤镜透传
            filter_intensity=filter_intensity,  # [本地补丁] (seconds)
            # Pass mask related parameters
            mask_type=mask_type,
            mask_center_x=mask_center_x,
            mask_center_y=mask_center_y,
            mask_size=mask_size,
            mask_rotation=mask_rotation,
            mask_feather=mask_feather,
            mask_invert=mask_invert,
            mask_rect_width=mask_rect_width,
            mask_round_corner=mask_round_corner,
            background_blur=background_blur
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while processing image: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_video_keyframe', methods=['POST'])
def add_video_keyframe():
    data = request.get_json()
    
    # Get required parameters
    draft_id = data.get('draft_id')
    track_name = data.get('track_name', 'video_main')  # Default main track
    
    # Single keyframe parameters (backward compatibility)
    property_type = data.get('property_type', 'alpha')  # Default opacity
    time = data.get('time', 0.0)  # Default 0 seconds
    value = data.get('value', '1.0')  # Default value 1.0
    
    # Batch keyframe parameters (new)
    property_types = data.get('property_types')  # Property type list
    times = data.get('times')  # Time list
    values = data.get('values')  # Value list

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    try:
        # Call add_video_keyframe_impl method
        draft_result = add_video_keyframe_impl(
            draft_id=draft_id,
            track_name=track_name,
            property_type=property_type,
            time=time,
            value=value,
            property_types=property_types,
            times=times,
            values=values
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while adding keyframe: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_effect', methods=['POST'])
def add_effect():
    data = request.get_json()
    
    # Get required parameters
    effect_type = data.get('effect_type')  # Effect type name, will match from Video_scene_effect_type or Video_character_effect_type
    start = data.get('start', 0)  # Start time (seconds), default 0
    effect_category = data.get('effect_category', "scene") # Effect category, "scene" or "character", default "scene"
    end = data.get('end', 3.0)  # End time (seconds), default 3 seconds
    draft_id = data.get('draft_id')  # Draft ID, if None or corresponding zip file not found, create new draft
    track_name = data.get('track_name', "effect_01")  # Track name, can be omitted when there is only one effect track
    params = data.get('params')  # Effect parameter list, items not provided or None in parameter list use default values
    width = data.get('width', 1080)
    height = data.get('height', 1920)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not effect_type:
        error_message = "Hi, the required parameters 'effect_type' are missing. Please add them and try again."
        result["error"] = error_message
        return jsonify(result)

    try:
        # Call add_effect_impl method
        draft_result = add_effect_impl(
            effect_type=effect_type,
            effect_category=effect_category,
            start=start,
            end=end,
            draft_id=draft_id,
            track_name=track_name,
            params=params,
            width=width,
            height=height
        )
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while adding effect: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

@app.route('/query_script', methods=['POST'])
def query_script():
    data = request.get_json()

    # Get required parameters
    draft_id = data.get('draft_id')
    force_update = data.get('force_update', True)
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not draft_id:
        error_message = "Hi, the required parameter 'draft_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)

    try:
        # Call query_script_impl method
        script = query_script_impl(draft_id=draft_id, force_update=force_update)
        
        if script is None:
            error_message = f"Draft {draft_id} does not exist in cache."
            result["error"] = error_message
            return jsonify(result)
        
        # Convert script object to JSON serializable dictionary
        script_str = script.dumps()
        
        result["success"] = True
        result["output"] = script_str
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while querying script: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

@app.route('/save_draft', methods=['POST'])
def save_draft():
    data = request.get_json()
    
    # Get required parameters
    draft_id = data.get('draft_id')
    draft_folder = data.get('draft_folder')  # Draft folder parameter
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    # Validate required parameters
    if not draft_id:
        error_message = "Hi, the required parameter 'draft_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)
    
    try:
        # Call save_draft_impl method, start background task
        draft_result = save_draft_impl(draft_id, draft_folder)
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while saving draft: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

# Add new query status interface
@app.route('/query_draft_status', methods=['POST'])
def query_draft_status():
    data = request.get_json()
    
    # Get required parameters
    task_id = data.get('task_id')
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    # Validate required parameters
    if not task_id:
        error_message = "Hi, the required parameter 'task_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)
    
    try:
        # Get task status
        task_status = query_task_status(task_id)
        
        if task_status["status"] == "not_found":
            error_message = f"Task with ID {task_id} not found. Please check if the task ID is correct."
            result["error"] = error_message
            return jsonify(result)
        
        result["success"] = True
        result["output"] = task_status
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while querying task status: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/generate_draft_url', methods=['POST'])
def generate_draft_url():
    data = request.get_json()
    
    # Get required parameters
    draft_id = data.get('draft_id')
    draft_folder = data.get('draft_folder')  # New draft_folder parameter
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    # Validate required parameters
    if not draft_id:
        error_message = "Hi, the required parameter 'draft_id' is missing. Please add it and try again."
        result["error"] = error_message
        return jsonify(result)
    
    try:
        draft_result = { "draft_url" : f"{DRAFT_DOMAIN}{PREVIEW_ROUTER}?={draft_id}"}
        
        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)
        
    except Exception as e:
        error_message = f"Error occurred while saving draft: {str(e)}."
        result["error"] = error_message
        return jsonify(result)

@app.route('/add_sticker', methods=['POST'])
def add_sticker():
    data = request.get_json()
    # Get required parameters
    resource_id = data.get('sticker_id')
    start = data.get('start', 0)
    end = data.get('end', 5.0)  # Default display 5 seconds
    draft_id = data.get('draft_id')
    transform_y = data.get('transform_y', 0)
    transform_x = data.get('transform_x', 0)
    alpha = data.get('alpha', 1.0)
    flip_horizontal = data.get('flip_horizontal', False)
    flip_vertical = data.get('flip_vertical', False)
    rotation = data.get('rotation', 0.0)
    scale_x = data.get('scale_x', 1.0)
    scale_y = data.get('scale_y', 1.0)
    track_name = data.get('track_name', 'sticker_main')
    relative_index = data.get('relative_index', 0)
    width = data.get('width', 1080)
    height = data.get('height', 1920)

    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    # Validate required parameters
    if not resource_id:
        error_message = "Hi, the required parameter 'sticker_id' is missing. Please add it and try again. "
        result["error"] = error_message
        return jsonify(result)

    try:
        # Call add_sticker_impl method
        draft_result = add_sticker_impl(
            resource_id=resource_id,
            start=start,
            end=end,
            draft_id=draft_id,
            transform_y=transform_y,
            transform_x=transform_x,
            alpha=alpha,
            flip_horizontal=flip_horizontal,
            flip_vertical=flip_vertical,
            rotation=rotation,
            scale_x=scale_x,
            scale_y=scale_y,
            track_name=track_name,
            relative_index=relative_index,
            width=width,
            height=height
        )

        result["success"] = True
        result["output"] = draft_result
        return jsonify(result)

    except Exception as e:
        error_message = f"Error occurred while adding sticker: {str(e)}. "
        result["error"] = error_message
        return jsonify(result)

@app.route('/get_intro_animation_types', methods=['GET'])
def get_intro_animation_types():
    """Return supported entrance animation type list
    
    If IS_CAPCUT_ENV is True, return entrance animation types in CapCut environment
    Otherwise return entrance animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        animation_types = []
        
        if IS_CAPCUT_ENV:
            # Return entrance animation types in CapCut environment
            for name, member in CapCut_Intro_type.__members__.items():
                animation_types.append({
                    "name": name
                })
        else:
            # Return entrance animation types in JianYing environment
            for name, member in Intro_type.__members__.items():
                animation_types.append({
                    "name": name
                })
        
        result["output"] = animation_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting entrance animation types: {str(e)}"
        return jsonify(result)
        
@app.route('/get_outro_animation_types', methods=['GET'])
def get_outro_animation_types():
    """Return supported exit animation type list
    
    If IS_CAPCUT_ENV is True, return exit animation types in CapCut environment
    Otherwise return exit animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        animation_types = []
        
        if IS_CAPCUT_ENV:
            # Return exit animation types in CapCut environment
            for name, member in CapCut_Outro_type.__members__.items():
                animation_types.append({
                    "name": name
                })
        else:
            # Return exit animation types in JianYing environment
            for name, member in Outro_type.__members__.items():
                animation_types.append({
                    "name": name
                })
        
        result["output"] = animation_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting exit animation types: {str(e)}"
        return jsonify(result)


@app.route('/get_combo_animation_types', methods=['GET'])
def get_combo_animation_types():
    """Return supported combo animation type list
    
    If IS_CAPCUT_ENV is True, return combo animation types in CapCut environment
    Otherwise return combo animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        animation_types = []
        
        if IS_CAPCUT_ENV:
            # Return combo animation types in CapCut environment
            for name, member in CapCut_Group_animation_type.__members__.items():
                animation_types.append({
                    "name": name
                })
        else:
            # Return combo animation types in JianYing environment
            for name, member in Group_animation_type.__members__.items():
                animation_types.append({
                    "name": name
                })
        
        result["output"] = animation_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting combo animation types: {str(e)}"
        return jsonify(result)


@app.route('/get_transition_types', methods=['GET'])
def get_transition_types():
    """Return supported transition animation type list
    
    If IS_CAPCUT_ENV is True, return transition animation types in CapCut environment
    Otherwise return transition animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        transition_types = []
        
        if IS_CAPCUT_ENV:
            # Return transition animation types in CapCut environment
            for name, member in CapCut_Transition_type.__members__.items():
                transition_types.append({
                    "name": name
                })
        else:
            # Return transition animation types in JianYing environment
            for name, member in Transition_type.__members__.items():
                transition_types.append({
                    "name": name
                })
        
        result["output"] = transition_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting transition animation types: {str(e)}"
        return jsonify(result)


@app.route('/get_mask_types', methods=['GET'])
def get_mask_types():
    """Return supported mask type list
    
    If IS_CAPCUT_ENV is True, return mask types in CapCut environment
    Otherwise return mask types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        mask_types = []
        
        if IS_CAPCUT_ENV:
            # Return mask types in CapCut environment
            for name, member in CapCut_Mask_type.__members__.items():
                mask_types.append({
                    "name": name
                })
        else:
            # Return mask types in JianYing environment
            for name, member in Mask_type.__members__.items():
                mask_types.append({
                    "name": name
                })
        
        result["output"] = mask_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting mask types: {str(e)}"
        return jsonify(result)


@app.route('/get_audio_effect_types', methods=['GET'])
def get_audio_effect_types():
    """Return supported audio effect type list
    
    If IS_CAPCUT_ENV is True, return audio effect types in CapCut environment
    Otherwise return audio effect types in JianYing environment
    
    The returned structure includes name, type and Effect_param information
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        audio_effect_types = []
        
        if IS_CAPCUT_ENV:
            # Return audio effect types in CapCut environment
            # 1. Voice filters effect types
            for name, member in CapCut_Voice_filters_effect_type.__members__.items():
                params_info = []
                for param in member.value.params:
                    params_info.append({
                        "name": param.name,
                        "default_value": param.default_value * 100,
                        "min_value": param.min_value * 100,
                        "max_value": param.max_value * 100
                    })
                
                audio_effect_types.append({
                    "name": name,
                    "type": "Voice_filters",
                    "params": params_info
                })
            
            # 2. Voice characters effect types
            for name, member in CapCut_Voice_characters_effect_type.__members__.items():
                params_info = []
                for param in member.value.params:
                    params_info.append({
                        "name": param.name,
                        "default_value": param.default_value * 100,
                        "min_value": param.min_value * 100,
                        "max_value": param.max_value * 100
                    })
                
                audio_effect_types.append({
                    "name": name,
                    "type": "Voice_characters",
                    "params": params_info
                })
            
            # 3. Speech to song effect types
            for name, member in CapCut_Speech_to_song_effect_type.__members__.items():
                params_info = []
                for param in member.value.params:
                    params_info.append({
                        "name": param.name,
                        "default_value": param.default_value * 100,
                        "min_value": param.min_value * 100,
                        "max_value": param.max_value * 100
                    })
                
                audio_effect_types.append({
                    "name": name,
                    "type": "Speech_to_song",
                    "params": params_info
                })
        else:
            # Return audio effect types in JianYing environment
            # 1. Tone effect types
            for name, member in Tone_effect_type.__members__.items():
                params_info = []
                for param in member.value.params:
                    params_info.append({
                        "name": param.name,
                        "default_value": param.default_value * 100,
                        "min_value": param.min_value * 100,
                        "max_value": param.max_value * 100
                    })
                
                audio_effect_types.append({
                    "name": name,
                    "type": "Tone",
                    "params": params_info
                })
            
            # 2. Audio scene effect types
            for name, member in Audio_scene_effect_type.__members__.items():
                params_info = []
                for param in member.value.params:
                    params_info.append({
                        "name": param.name,
                        "default_value": param.default_value * 100,
                        "min_value": param.min_value * 100,
                        "max_value": param.max_value * 100
                    })
                
                audio_effect_types.append({
                    "name": name,
                    "type": "Audio_scene",
                    "params": params_info
                })
            
            # 3. Speech to song effect types
            for name, member in Speech_to_song_type.__members__.items():
                params_info = []
                for param in member.value.params:
                    params_info.append({
                        "name": param.name,
                        "default_value": param.default_value * 100,
                        "min_value": param.min_value * 100,
                        "max_value": param.max_value * 100
                    })
                
                audio_effect_types.append({
                    "name": name,
                    "type": "Speech_to_song",
                    "params": params_info
                })
        
        result["output"] = audio_effect_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting audio effect types: {str(e)}"
        return jsonify(result)


@app.route('/get_font_types', methods=['GET'])
def get_font_types():
    """Return supported font type list
    
    Return font types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        font_types = []
        
        # Return font types in JianYing environment
        for name, member in Font_type.__members__.items():
            font_types.append({
                "name": name
            })
        
        result["output"] = font_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting font types: {str(e)}"
        return jsonify(result)


@app.route('/get_text_intro_types', methods=['GET'])
def get_text_intro_types():
    """Return supported text entrance animation type list
    
    If IS_CAPCUT_ENV is True, return text entrance animation types in CapCut environment
    Otherwise return text entrance animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        text_intro_types = []
        
        if IS_CAPCUT_ENV:
            # Return text entrance animation types in CapCut environment
            for name, member in CapCut_Text_intro.__members__.items():
                text_intro_types.append({
                    "name": name
                })
        else:
            # Return text entrance animation types in JianYing environment
            for name, member in Text_intro.__members__.items():
                text_intro_types.append({
                    "name": name
                })
        
        result["output"] = text_intro_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting text entrance animation types: {str(e)}"
        return jsonify(result)

@app.route('/get_text_outro_types', methods=['GET'])
def get_text_outro_types():
    """Return supported text exit animation type list
    
    If IS_CAPCUT_ENV is True, return text exit animation types in CapCut environment
    Otherwise return text exit animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        text_outro_types = []
        
        if IS_CAPCUT_ENV:
            # Return text exit animation types in CapCut environment
            for name, member in CapCut_Text_outro.__members__.items():
                text_outro_types.append({
                    "name": name
                })
        else:
            # Return text exit animation types in JianYing environment
            for name, member in Text_outro.__members__.items():
                text_outro_types.append({
                    "name": name
                })
        
        result["output"] = text_outro_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting text exit animation types: {str(e)}"
        return jsonify(result)

@app.route('/get_text_loop_anim_types', methods=['GET'])
def get_text_loop_anim_types():
    """Return supported text loop animation type list
    
    If IS_CAPCUT_ENV is True, return text loop animation types in CapCut environment
    Otherwise return text loop animation types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        text_loop_anim_types = []
        
        if IS_CAPCUT_ENV:
            # Return text loop animation types in CapCut environment
            for name, member in CapCut_Text_loop_anim.__members__.items():
                text_loop_anim_types.append({
                    "name": name
                })
        else:
            # Return text loop animation types in JianYing environment
            for name, member in Text_loop_anim.__members__.items():
                text_loop_anim_types.append({
                    "name": name
                })
        
        result["output"] = text_loop_anim_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting text loop animation types: {str(e)}"
        return jsonify(result)


@app.route('/get_video_scene_effect_types', methods=['GET'])
def get_video_scene_effect_types():
    """Return supported scene effect type list
    
    If IS_CAPCUT_ENV is True, return scene effect types in CapCut environment
    Otherwise return scene effect types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        effect_types = []
        
        if IS_CAPCUT_ENV:
            # Return scene effect types in CapCut environment
            for name, member in CapCut_Video_scene_effect_type.__members__.items():
                effect_types.append({
                    "name": name
                })
        else:
            # Return scene effect types in JianYing environment
            for name, member in Video_scene_effect_type.__members__.items():
                effect_types.append({
                    "name": name
                })
        
        result["output"] = effect_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting scene effect types: {str(e)}"
        return jsonify(result)


@app.route('/get_video_character_effect_types', methods=['GET'])
def get_video_character_effect_types():
    """Return supported character effect type list
    
    If IS_CAPCUT_ENV is True, return character effect types in CapCut environment
    Otherwise return character effect types in JianYing environment
    """
    result = {
        "success": True,
        "output": "",
        "error": ""
    }
    
    try:
        effect_types = []
        
        if IS_CAPCUT_ENV:
            # Return character effect types in CapCut environment
            for name, member in CapCut_Video_character_effect_type.__members__.items():
                effect_types.append({
                    "name": name
                })
        else:
            # Return character effect types in JianYing environment
            for name, member in Video_character_effect_type.__members__.items():
                effect_types.append({
                    "name": name
                })
        
        result["output"] = effect_types
        return jsonify(result)
    
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error occurred while getting character effect types: {str(e)}"
        return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
