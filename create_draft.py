import uuid
import pyJianYingDraft as draft
import time
from draft_cache import DRAFT_CACHE, update_cache

def create_draft(width=1080, height=1920, fps=30):
    """
    Create new CapCut draft
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :param fps: Timeline frame rate, default 30
    :return: (draft_name, draft_path, draft_id, draft_url)
    """
    # Generate timestamp and draft_id
    unix_time = int(time.time())
    unique_id = uuid.uuid4().hex[:8]  # Take the first 8 digits of UUID
    draft_id = f"dfd_cat_{unix_time}_{unique_id}"  # Use Unix timestamp and UUID combination
    
    # Create CapCut draft with specified resolution
    script = draft.Script_file(width, height, fps=fps)
    
    # Store in global cache
    update_cache(draft_id, script)
    
    return script, draft_id

def get_or_create_draft(draft_id=None, width=1080, height=1920, fps=30):
    """
    Get or create CapCut draft
    :param draft_id: Draft ID, if None or corresponding zip file not found, create new draft
    :param width: Video width, default 1080
    :param height: Video height, default 1920
    :param fps: Timeline frame rate of a newly created draft, default 30
    :return: (draft_name, draft_path, draft_id, draft_dir, script)
    """
    global DRAFT_CACHE  # Declare use of global variable
    
    if draft_id is not None and draft_id in DRAFT_CACHE:
        # Get existing draft information from cache
        print(f"Getting draft from cache: {draft_id}")
        # Update last access time
        update_cache(draft_id, DRAFT_CACHE[draft_id])
        return draft_id, DRAFT_CACHE[draft_id]

    # Create new draft logic
    print("Creating new draft")
    script, generate_draft_id = create_draft(
        width=width,
        height=height,
        fps=fps,
    )
    return generate_draft_id, script
    