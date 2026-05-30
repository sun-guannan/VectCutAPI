import uuid
import pyJianYingDraft as draft
import time
from settings.local import IS_CAPCUT_ENV
from util import generate_draft_url, url_to_hash, build_draft_asset_path
from pyJianYingDraft import trange, Clip_settings
from typing import Optional, Dict
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft

def add_image_impl(
    image_url: str,
    draft_folder: Optional[str] = None,
    width: int = 1080,
    height: int = 1920,
    start: float = 0,
    end: float = 3.0,  # Default display time: 3 seconds
    draft_id: Optional[str] = None,
    transform_y: float = 0,
    scale_x: float = 1,
    scale_y: float = 1,
    transform_x: float = 0,
    track_name: str = "main",
    relative_index: int = 0,
    animation: Optional[str] = None,  # Entrance animation parameter (backward compatibility)
    animation_duration: float = 0.5,  # Entrance animation duration parameter, default 0.5 seconds
    intro_animation: Optional[str] = None,  # New entrance animation parameter, higher priority than animation
    intro_animation_duration: float = 0.5,  # New entrance animation duration parameter, default 0.5 seconds
    outro_animation: Optional[str] = None,  # Exit animation parameter
    outro_animation_duration: float = 0.5,  # Exit animation duration parameter, default 0.5 seconds
    combo_animation: Optional[str] = None,  # Combo animation parameter
    combo_animation_duration: float = 0.5,  # Combo animation duration parameter, default 0.5 seconds
    transition: Optional[str] = None,  # Transition type parameter
    transition_duration: Optional[float] = 0.5,  # Transition duration parameter (seconds), default 0.5 seconds
    # Mask related parameters
    mask_type: Optional[str] = None,  # Mask type: Linear, Mirror, Circle, Rectangle, Heart, Star
    mask_center_x: float = 0.0,  # Mask center X coordinate
    mask_center_y: float = 0.0,  # Mask center Y coordinate
    mask_size: float = 0.5,  # Mask main size
    mask_rotation: float = 0.0,  # Mask rotation angle
    mask_feather: float = 0.0,  # Mask feather parameter (0-100)
    mask_invert: bool = False,  # Whether to invert the mask
    mask_rect_width: Optional[float] = None,  # Rectangle mask width (rectangle mask only)
    mask_round_corner: Optional[float] = None,  # Rectangle mask rounded corner (rectangle mask only, 0-100)
    background_blur: Optional[int] = None  # Background blur level, 1-4, corresponding to four blur intensity levels
) -> Dict[str, str]:
    """
    Add an image track to the specified draft
    :param animation: Entrance animation name, supported animations include: Zoom Out, Fade In, Zoom In, Rotate, Kira Float, Shake Down, Mirror Flip, Rotate Open, Fold Open, Vortex Rotate, Jump Open, etc.
    :param animation_duration: Entrance animation duration (seconds), default 0.5 seconds
    :param intro_animation: New entrance animation parameter, higher priority than animation
    :param intro_animation_duration: New entrance animation duration (seconds), default 0.5 seconds
    :param outro_animation: Exit animation parameter
    :param outro_animation_duration: Exit animation duration (seconds), default 0.5 seconds
    :param combo_animation: Combo animation parameter
    :param combo_animation_duration: Combo animation duration (seconds), default 0.5 seconds
    :param transition: Transition type, supported transitions include: Dissolve, Move Up, Move Down, Move Left, Move Right, Split, Compress, Anime Cloud, Anime Vortex, etc.
    :param transition_duration: Transition duration (seconds), default 0.5 seconds
    :param draft_folder: Draft folder path, optional parameter
    :param image_url: Image URL
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :param start: Start time (seconds), default 0
    :param end: End time (seconds), default 3 seconds
    :param draft_id: Draft ID, if None or corresponding zip file not found, a new draft will be created
    :param transform_y: Y-axis transformation, default 0
    :param scale_x: X-axis scaling, default 1
    :param scale_y: Y-axis scaling, default 1
    :param transform_x: X-axis transformation, default 0
    :param track_name: When there is only one video, track name can be omitted
    :param relative_index: Track rendering order index, default 0
    :param mask_type: Mask type, supports: Linear, Mirror, Circle, Rectangle, Heart, Star
    :param mask_center_x: Mask center X coordinate (in material pixels), default set at material center
    :param mask_center_y: Mask center Y coordinate (in material pixels), default set at material center
    :param mask_size: Main size of the mask, represented as a proportion of material height, default is 0.5
    :param mask_rotation: Clockwise rotation angle of the mask, default no rotation
    :param mask_feather: Mask feather parameter, range 0~100, default no feathering
    :param mask_invert: Whether to invert the mask, default not inverted
    :param mask_rect_width: Rectangle mask width, only allowed when mask type is rectangle, represented as a proportion of material width
    :param mask_round_corner: Rectangle mask rounded corner parameter, only allowed when mask type is rectangle, range 0~100
    :param background_blur: Background blur level, 1-4, corresponding to four blur intensity levels (0.0625, 0.375, 0.75, 1.0)
    :return: Updated draft information, including draft_id and draft_url
    """
    # Get or create draft
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )
    
    # Check if video track exists, if not, add a default video track
    try:
        script.get_track(draft.Track_type.video, track_name=None)
    except exceptions.TrackNotFound:
        script.add_track(draft.Track_type.video, relative_index=0)
    except NameError:
        # If multiple video tracks exist (NameError), do nothing
        pass

    # Add video track (only when track doesn't exist)
    if track_name is not None:
        try:
            imported_track=script.get_imported_track(draft.Track_type.video, name=track_name)
            # If no exception is thrown, the track already exists
        except exceptions.TrackNotFound:
            # Track doesn't exist, create a new track
            script.add_track(draft.Track_type.video, track_name=track_name, relative_index=relative_index)
    else:
        script.add_track(draft.Track_type.video, relative_index=relative_index)
    
    # Generate material_name but don't download the image
    material_name = f"image_{url_to_hash(image_url)}.png"
    
    # Build draft_image_path
    draft_image_path = None
    if draft_folder:
        draft_image_path = build_draft_asset_path(draft_folder, draft_id, "image", material_name)
        # Print path information
        print('replace_path:', draft_image_path)
    
    # Create image material
    if draft_image_path:
        image_material = draft.Video_material(path=None, material_type='photo', replace_path=draft_image_path, remote_url=image_url, material_name=material_name)
    else:
        image_material = draft.Video_material(path=None, material_type='photo', remote_url=image_url, material_name=material_name)
    
    # Create target_timerange (image)
    duration = end - start
    target_timerange = trange(f"{start}s", f"{duration}s")
    source_timerange = trange(f"{0}s", f"{duration}s")
    
    # Create image segment
    image_segment = draft.Video_segment(
        image_material,
        target_timerange=target_timerange,
        source_timerange=source_timerange,
        clip_settings=Clip_settings(
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x
        )
    )
    
    # Add entrance animation (prioritize intro_animation, then use animation)
    intro_anim = intro_animation if intro_animation is not None else animation
    intro_animation_duration = intro_animation_duration if intro_animation_duration is not None else animation_duration
    if intro_anim:
        try:
            if IS_CAPCUT_ENV:
                animation_type = getattr(draft.CapCut_Intro_type, intro_anim)
            else:
                animation_type = getattr(draft.Intro_type, intro_anim)
            image_segment.add_animation(animation_type, intro_animation_duration * 1e6)  # Use microsecond unit for animation duration
        except AttributeError:
            raise ValueError(f"Warning: Unsupported entrance animation type {intro_anim}, this parameter will be ignored")
    
    # Add exit animation
    if outro_animation:
        try:
            if IS_CAPCUT_ENV:
                outro_type = getattr(draft.CapCut_Outro_type, outro_animation)
            else:
                outro_type = getattr(draft.Outro_type, outro_animation)
            image_segment.add_animation(outro_type, outro_animation_duration * 1e6)  # Use microsecond unit for animation duration
        except AttributeError:
            raise ValueError(f"Warning: Unsupported exit animation type {outro_animation}, this parameter will be ignored")
    
    # Add combo animation
    if combo_animation:
        try:
            if IS_CAPCUT_ENV:
                combo_type = getattr(draft.CapCut_Group_animation_type, combo_animation)
            else:
                combo_type = getattr(draft.Group_animation_type, combo_animation)
            image_segment.add_animation(combo_type, combo_animation_duration * 1e6)  # Use microsecond unit for animation duration
        except AttributeError:
            raise ValueError(f"Warning: Unsupported combo animation type {combo_animation}, this parameter will be ignored")
    
    # Add transition effect
    if transition:
        try:
            if IS_CAPCUT_ENV:
                transition_type = getattr(draft.CapCut_Transition_type, transition)
            else:
                transition_type = getattr(draft.Transition_type, transition)
            # Convert seconds to microseconds (multiply by 1000000)
            duration_microseconds = int(transition_duration * 1000000) if transition_duration is not None else None
            image_segment.add_transition(transition_type, duration=duration_microseconds)
        except AttributeError:
            raise ValueError(f"Warning: Unsupported transition type {transition}, this parameter will be ignored")
    
    # Add mask effect
    if mask_type:
        try:
            if IS_CAPCUT_ENV:
                mask_type_enum = getattr(draft.CapCut_Mask_type, mask_type)
            else:
                mask_type_enum = getattr(draft.Mask_type, mask_type)
            image_segment.add_mask(
                script,
                mask_type_enum,  # Remove keyword name, pass as positional argument
                center_x=mask_center_x,
                center_y=mask_center_y,
                size=mask_size,
                rotation=mask_rotation,
                feather=mask_feather,
                invert=mask_invert,
                rect_width=mask_rect_width,
                round_corner=mask_round_corner
            )
        except:
            raise ValueError(f"Unsupported mask type {mask_type}, supported types include: Linear, Mirror, Circle, Rectangle, Heart, Star")
    
    # Add background blur effect
    if background_blur is not None:
        # Background blur level mapping table
        blur_levels = {
            1: 0.0625,  # Light blur
            2: 0.375,   # Medium blur
            3: 0.75,    # Heavy blur
            4: 1.0      # Maximum blur
        }
        
        # Validate background blur level
        if background_blur not in blur_levels:
            raise ValueError(f"Invalid background blur level {background_blur}, valid values are 1-4")
        
        # Add background blur effect
        image_segment.add_background_filling("blur", blur=blur_levels[background_blur])
    
    # Add image segment to track
    script.add_segment(image_segment, track_name=track_name)
    
    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
