# 导入必要的模块
import pyJianYingDraft as draft
import time
from util import generate_draft_url, url_to_hash, build_draft_asset_path
from typing import Optional, Dict, Tuple, List
from pyJianYingDraft import exceptions, Audio_scene_effect_type, Tone_effect_type, Speech_to_song_type, CapCut_Voice_filters_effect_type,CapCut_Voice_characters_effect_type,CapCut_Speech_to_song_effect_type, trange
from create_draft import get_or_create_draft
from settings.local import IS_CAPCUT_ENV

def add_audio_track(
    audio_url: str,
    draft_folder: Optional[str] = None,
    start: float = 0,
    end: Optional[float] = None,
    target_start: float = 0,
    draft_id: Optional[str] = None,
    volume: float = 1.0,
    track_name: str = "audio_main",
    speed: float = 1.0,
    sound_effects: Optional[List[Tuple[str, Optional[List[Optional[float]]]]]]=None,
    width: int = 1080,
    height: int = 1920,
    duration: Optional[float] = None  # Added duration parameter
) -> Dict[str, str]:
    """
    Add an audio track to the specified draft
    :param draft_folder: Draft folder path, optional parameter
    :param audio_url: Audio URL
    :param start: Start time (seconds), default 0
    :param end: End time (seconds), default None (use total audio duration)
    :param target_start: Target track insertion position (seconds), default 0
    :param draft_id: Draft ID, if None or corresponding zip file not found, a new draft will be created
    :param volume: Volume level, range 0.0-1.0, default 1.0
    :param track_name: Track name, default "audio_main"
    :param speed: Playback speed, default 1.0
    :param sound_effects: Scene sound effect list, each element is a tuple containing effect type name and parameter list, default None
    :return: Updated draft information
    """
    # Get or create draft
    draft_id, script = get_or_create_draft(
        draft_id=draft_id,
        width=width,
        height=height
    )
    
    # Add audio track (only when track doesn't exist)
    if track_name is not None:
        try:
            imported_track = script.get_imported_track(draft.Track_type.audio, name=track_name)
            # If no exception is thrown, the track already exists
        except exceptions.TrackNotFound:
            # Track doesn't exist, create a new track
            script.add_track(draft.Track_type.audio, track_name=track_name)
    else:
       script.add_track(draft.Track_type.audio)

    # If duration parameter is provided, prioritize it; otherwise use default audio duration of 0 seconds, real duration will be obtained during download
    if duration is not None:
        # Use the provided duration, skip duration retrieval and checking
        audio_duration = duration
    else:
        # Use default audio duration of 0 seconds, real duration will be obtained when downloading the draft
        audio_duration = 0.0  # Default audio duration is 0 seconds
        # duration_result = get_video_duration(audio_url)  # Reuse video duration retrieval function
        # if not duration_result["success"]:
        #     print(f"Failed to get audio duration: {duration_result['error']}")
        
        # # Check if audio duration exceeds 10 minutes
        # if duration_result["output"] > 600:  # 600 seconds = 10 minutes
        #     raise Exception(f"Audio duration exceeds 10-minute limit, current duration: {duration_result['output']} seconds")
        
        # audio_duration = duration_result["output"]
    
    # Download audio to local
    # local_audio_path = download_audio(audio_url, draft_dir)

    material_name = f"audio_{url_to_hash(audio_url)}.mp3"  # Use original filename + timestamp + fixed mp3 extension
    
    # Build draft_audio_path
    draft_audio_path = None
    if draft_folder:
        draft_audio_path = build_draft_asset_path(draft_folder, draft_id, "audio", material_name)
    
    # Set default value for audio end time
    audio_end = end if end is not None else audio_duration
    
    # Calculate audio duration
    duration = audio_end - start
    
    # Create audio segment
    if draft_audio_path:
        print('replace_path:', draft_audio_path)
        audio_material = draft.Audio_material(replace_path=draft_audio_path, remote_url=audio_url, material_name=material_name, duration=audio_duration)
    else:
        audio_material = draft.Audio_material(remote_url=audio_url, material_name=material_name, duration=audio_duration)
    audio_segment = draft.Audio_segment(
        audio_material,  # Pass material object
        target_timerange=trange(f"{target_start}s", f"{duration}s"),  # Use target_start and duration
        source_timerange=trange(f"{start}s", f"{duration}s"),
        speed=speed,  # Set playback speed
        volume=volume  # Set volume
    )
    
    # Add scene sound effects
    if sound_effects:
        for effect_name, params in sound_effects:
            # Choose different effect types based on IS_CAPCUT_ENV
            effect_type = None
            
            if IS_CAPCUT_ENV:
                # In CapCut environment, look for effects in CapCut_Voice_filters_effect_type
                try:
                    effect_type = getattr(CapCut_Voice_filters_effect_type, effect_name)
                except AttributeError:
                    try:
                        # Look for effects in CapCut_Voice_characters_effect_type
                        effect_type = getattr(CapCut_Voice_characters_effect_type, effect_name)
                    except AttributeError:
                        # If still not found, look for effects in CapCut_Speech_to_song_effect_type
                        try:
                            effect_type = getattr(CapCut_Speech_to_song_effect_type, effect_name)
                        except AttributeError:
                            effect_type = None
            else:
                # In JianYing environment, look for effects in Audio_scene_effect_type
                try:
                    effect_type = getattr(Audio_scene_effect_type, effect_name)
                except AttributeError:
                    # If not found in Audio_scene_effect_type, continue searching in other effect types
                    try:
                        effect_type = getattr(Tone_effect_type, effect_name)
                    except AttributeError:
                        # If still not found, look for effects in Speech_to_song_type
                        try:
                            effect_type = getattr(Speech_to_song_type, effect_name)
                        except AttributeError:
                            effect_type = None
            
            # If corresponding effect type is found, add it to the audio segment
            if effect_type:
                audio_segment.add_effect(effect_type, params)
            else:
                print(f"Warning: Audio effect named {effect_name} not found")
    
    # Add audio segment to track
    script.add_segment(audio_segment, track_name=track_name)
    
    return {
        "draft_id": draft_id,
        "draft_url": generate_draft_url(draft_id)
    }
