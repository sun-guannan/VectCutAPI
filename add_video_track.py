import pyJianYingDraft as draft
import time
from settings.local import IS_CAPCUT_ENV
from util import generate_draft_url, url_to_hash, build_draft_asset_path
from pyJianYingDraft import trange, Clip_settings
from typing import Optional, Dict
from pyJianYingDraft import exceptions
from create_draft import get_or_create_draft

def add_video_track(
    video_url: str,
    draft_folder: Optional[str] = None,
    width: int = 1080,
    height: int = 1920,
    start: float = 0,
    end: Optional[float] = None,
    target_start: float = 0,
    draft_id: Optional[str] = None,
    transform_y: float = 0,
    scale_x: float = 1,
    scale_y: float = 1,
    transform_x: float = 0,
    speed: float = 1.0,
    track_name: str = "main",
    relative_index: int = 0,
    duration: Optional[float] = None,  # Added duration parameter
    transition: Optional[str] = None,  # Transition type
    transition_duration: Optional[float] = 0.5,  # Transition duration (seconds)
    # Mask related parameters
    mask_type: Optional[str] = None,  # Mask type
    mask_center_x: float = 0.5,  # Mask center X coordinate (0-1)
    mask_center_y: float = 0.5,  # Mask center Y coordinate (0-1)
    mask_size: float = 1.0,  # Mask size (0-1)
    mask_rotation: float = 0.0,  # Mask rotation angle (degrees)
    mask_feather: float = 0.0,  # Mask feather level (0-1)
    mask_invert: bool = False,  # Whether to invert mask
    mask_rect_width: Optional[float] = None,  # Rectangle mask width (only for rectangle mask)
    mask_round_corner: Optional[float] = None,  # Rectangle mask rounded corner (only for rectangle mask, 0-100)
    volume: float = 1.0,  # Volume level, default 1.0
    background_blur: Optional[int] = None  # Background blur level, optional values: 1 (light), 2 (medium), 3 (strong), 4 (maximum), default None (no background blur)
) -> Dict[str, str]:
    """
    Add video track to specified draft
    :param draft_folder: Draft folder path, optional parameter
    :param video_url: Video URL
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :param start: Source video start time (seconds), default 0
    :param end: Source video end time (seconds), default None (use total video duration)
    :param target_start: Target video start time (seconds), default 0
    :param draft_id: Draft ID, if None or corresponding zip file not found, create new draft
    :param transform_y: Y-axis transform, default 0
    :param scale_x: X-axis scale, default 1
    :param scale_y: Y-axis scale, default 1
    :param transform_x: X-axis transform, default 0
    :param speed: Video playback speed, default 1.0
    :param track_name: When there is only one video, track name can be omitted
    :param relative_index: Track rendering order index, default 0
    :param duration: Video duration (seconds), if provided, skip duration detection
    :param transition: Transition type, optional parameter
    :param transition_duration: Transition duration (seconds), default uses the default duration of transition type
    :param mask_type: Mask type (linear, mirror, circle, rectangle, heart, star), optional parameter
    :param mask_center_x: Mask center X coordinate (0-1), default 0.5
    :param mask_center_y: Mask center Y coordinate (0-1), default 0.5
    :param mask_size: Mask size (0-1), default 1.0
    :param mask_rotation: Mask rotation angle (degrees), default 0.0
    :param mask_feather: Mask feather level (0-1), default 0.0
    :param mask_invert: Whether to invert mask, default False
    :param mask_rect_width: Rectangle mask width, only allowed when mask type is rectangle, represented as a proportion of material width
    :param mask_round_corner: Rectangle mask rounded corner parameter, only allowed when mask type is rectangle, range 0~100
    :param volume: Volume level, default 1.0 (0.0 is mute, 1.0 is original volume)
    :param background_blur: Background blur level, optional values: 1 (light), 2 (medium), 3 (strong), 4 (maximum), default None (no background blur)
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
            # Track doesn't exist, create new track
            script.add_track(draft.Track_type.video, track_name=track_name, relative_index=relative_index)
    else:
        script.add_track(draft.Track_type.video, relative_index=relative_index)
    
    # If duration parameter is passed, use it preferentially; otherwise use default duration of 0 seconds, and get the real duration when downloading the draft
    if duration is not None:
        # Use the passed duration, skip duration retrieval and check
        video_duration = duration
    else:
        # Use default duration of 0 seconds, and get the real duration when downloading the draft
        video_duration = 0.0  # Default video duration is 0 seconds
        # duration_result = get_video_duration(video_url)
        # if not duration_result["success"]:
        #     print(f"Failed to get video duration: {duration_result['error']}")
        
        # # Check if video duration exceeds 2 minutes
        # if duration_result["output"] > 120:  # 120 seconds = 2 minutes
        #     raise Exception(f"Video duration exceeds 2-minute limit, current duration: {duration_result['output']} seconds")
        
        # video_duration = duration_result["output"]
    
    # Generate local filename
    material_name = f"video_{url_to_hash(video_url)}.mp4"
    # local_video_path = download_video(video_url, draft_dir)
    
    # Build draft_video_path
    draft_video_path = None
    if draft_folder:
        draft_video_path = build_draft_asset_path(draft_folder, draft_id, "video", material_name)
        # Print path information
        print('replace_path:', draft_video_path)

    # Set video end time
    video_end = end if end is not None else video_duration
    
    # Calculate source video duration
    source_duration = video_end - start
    # Calculate target video duration (considering speed factor)
    target_duration = source_duration / speed
    
    # Create video clip
    if draft_video_path:
        video_material = draft.Video_material(material_type='video', replace_path=draft_video_path, remote_url=video_url, material_name=material_name, duration=video_duration, width=0, height=0)
    else:
        video_material = draft.Video_material(material_type='video', remote_url=video_url, material_name=material_name, duration = video_duration, width=0, height=0)
    
    # Create source_timerange and target_timerange
    source_timerange = trange(f"{start}s", f"{source_duration}s")
    target_timerange = trange(f"{target_start}s", f"{target_duration}s")
    
    video_segment = draft.Video_segment(
        video_material,
        target_timerange=target_timerange,
        source_timerange=source_timerange,
        speed=speed,
        clip_settings=Clip_settings(
            transform_y=transform_y,
            scale_x=scale_x,
            scale_y=scale_y,
            transform_x=transform_x
        ),
        volume=volume
    )
    
    # Add transition effect
    if transition:
        try:
            # Get transition type
            if IS_CAPCUT_ENV:
                transition_type = getattr(draft.CapCut_Transition_type, transition)
            else:
                transition_type = getattr(draft.Transition_type, transition)
            
            # Set transition duration (convert to microseconds)
            duration_microseconds = int(transition_duration * 1e6)
            
            # Add transition
            video_segment.add_transition(transition_type, duration=duration_microseconds)
        except AttributeError:
            raise ValueError(f"Unsupported transition type: {transition}, transition setting skipped")
    
    # Add mask effect
    if mask_type:
        try:
            if IS_CAPCUT_ENV:
                mask_type_enum = getattr(draft.CapCut_Mask_type, mask_type)
            else:
                mask_type_enum = getattr(draft.Mask_type, mask_type)
            video_segment.add_mask(
                script,
                mask_type_enum,
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
            raise ValueError(f"Unsupported mask type {mask_type}, supported types include: linear, mirror, circle, rectangle, heart, star")
    
    # Add background blur effect
    if background_blur is not None:
        # Validate if background blur level is valid
        if background_blur not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid background blur level: {background_blur}, valid values are: 1, 2, 3, 4")
        
        # Map blur level to specific blur values
        blur_values = {
            1: 0.0625,  # Light blur
            2: 0.375,   # Medium blur
            3: 0.75,    # Strong blur
            4: 1.0      # Maximum blur
        }
        
        # Add background blur
        video_segment.add_background_filling("blur", blur=blur_values[background_blur])
    
    # Add video segment to track
    # if imported_track is not None:
    #     imported_track.add_segment(video_segment)
    # else:
    script.add_segment(video_segment, track_name=track_name)
    
    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
