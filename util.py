import shutil
import subprocess
import json
import re
import os
import hashlib
import functools
import time
from settings.local import DRAFT_DOMAIN, PREVIEW_ROUTER, IS_CAPCUT_ENV

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hexadecimal color code to RGB tuple (range 0.0-1.0)"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])  # Handle shorthand form (e.g. #fff)
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    except ValueError:
        raise ValueError(f"Invalid hexadecimal color code: {hex_color}")


def is_windows_path(path):
    """Detect if the path is Windows style"""
    # Check if it starts with a drive letter (e.g. C:\) or contains Windows style separators
    return re.match(r'^[a-zA-Z]:\\|\\\\', path) is not None

def build_draft_asset_path(draft_folder: str, draft_id: str, asset_type: str, material_name: str) -> str:
    """Build the path Jianying/CapCut should use for a material inside a draft."""
    if is_windows_path(draft_folder):
        if os.name == 'nt':
            return os.path.join(draft_folder, draft_id, "assets", asset_type, material_name)

        windows_drive, windows_path = re.match(r'([a-zA-Z]:)(.*)', draft_folder).groups()
        parts = [p for p in windows_path.split('\\') if p]
        return os.path.join(f"{windows_drive}\\", *parts, draft_id, "assets", asset_type, material_name).replace('/', '\\')

    return os.path.join(draft_folder, draft_id, "assets", asset_type, material_name)


def zip_draft(draft_id):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Compress folder
    zip_dir = os.path.join(current_dir, "tmp/zip")
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, f"{draft_id}.zip")
    shutil.make_archive(os.path.join(zip_dir, draft_id), 'zip', os.path.join(current_dir, draft_id))
    return zip_path

def url_to_hash(url, length=16):
    """
    Convert URL to a fixed-length hash string (without extension)
    
    Parameters:
    - url: Original URL string
    - length: Length of the hash string (maximum 64, default 16)
    
    Returns:
    - Hash string (e.g.: 3a7f9e7d9a1b4e2d)
    """
    # Ensure URL is bytes type
    url_bytes = url.encode('utf-8')
    
    # Use SHA-256 to generate hash (secure and highly unique)
    hash_object = hashlib.sha256(url_bytes)
    
    # Truncate to specified length of hexadecimal string
    return hash_object.hexdigest()[:length]


def timing_decorator(func_name):
    """Decorator: Used to monitor function execution time"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            print(f"[{func_name}] Starting execution...")
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                print(f"[{func_name}] Execution completed, time taken: {duration:.3f} seconds")
                return result
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                print(f"[{func_name}] Execution failed, time taken: {duration:.3f} seconds, error: {e}")
                raise
        return wrapper
    return decorator

def generate_draft_url(draft_id):
    return f"{DRAFT_DOMAIN}{PREVIEW_ROUTER}?draft_id={draft_id}&is_capcut={1 if IS_CAPCUT_ENV else 0}"
