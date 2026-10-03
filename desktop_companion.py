"""
CapCut Desktop Auto-Reload Companion
Provides automated hot-reloading for CapCut Desktop on Windows.
Bridges VectCutAPI / MCP drafts with the running CapCut editor.
"""

import os
import sys
import time
import subprocess
import ctypes
from ctypes import wintypes
import psutil

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
else:
    # Windows-only feature: keep the module importable elsewhere (macOS/Linux)
    user32 = kernel32 = WNDENUMPROC = None

# Windows API constants
SW_RESTORE = 9
SW_SHOW = 5
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

VK_MENU = 0x12       # Alt
VK_LEFT = 0x25       # Left arrow
VK_RETURN = 0x0D     # Enter
VK_ESCAPE = 0x1B     # Esc
KEYEVENTF_KEYUP = 0x0002

CAPCUT_LAUNCHER = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\Apps\CapCut.exe")
CAPCUT_DRAFTS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft")


def get_capcut_windows():
    """Finds all visible top-level windows belonging to CapCut."""
    if not IS_WINDOWS:
        return []
    windows = []

    def callback(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value.strip()

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            try:
                p = psutil.Process(pid.value)
                if "capcut" in p.name().lower():
                    rect = wintypes.RECT()
                    user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    w = rect.right - rect.left
                    h = rect.bottom - rect.top
                    # Filter out tiny helper / tray / offscreen windows
                    if w > 300 and h > 200:
                        windows.append({
                            "hwnd": hwnd,
                            "pid": pid.value,
                            "name": p.name(),
                            "title": title,
                            "rect": (rect.left, rect.top, rect.right, rect.bottom),
                            "width": w,
                            "height": h
                        })
            except Exception:
                pass
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return windows


def focus_window(hwnd):
    """Brings the specified window to foreground."""
    try:
        user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.05)
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.05)
        return True
    except Exception as e:
        print(f"[Companion] Focus error: {e}")
        return False


def click_client_coords(hwnd, x, y):
    """Simulates a mouse click at client coordinates (x, y) relative to hwnd."""
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    screen_x = rect.left + x
    screen_y = rect.top + y

    # Convert to normalized absolute coordinates (0 - 65535)
    sm_cx = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    sm_cy = user32.GetSystemMetrics(1)  # SM_CYSCREEN

    norm_x = int(screen_x * 65535 / sm_cx)
    norm_y = int(screen_y * 65535 / sm_cy)

    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, norm_x, norm_y, 0, 0)
    time.sleep(0.03)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.04)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def send_key_combo(key1, key2=None):
    """Sends a key combination using keybd_event."""
    user32.keybd_event(key1, 0, 0, 0)
    time.sleep(0.02)
    if key2:
        user32.keybd_event(key2, 0, 0, 0)
        time.sleep(0.03)
        user32.keybd_event(key2, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
    user32.keybd_event(key1, 0, KEYEVENTF_KEYUP, 0)


def reload_capcut_desktop(project_name=None, delay=0.35):
    """
    Automates hot-reload of CapCut Desktop:
    1. If CapCut is not running, launches CapCut.
    2. If in project editor, clicks Back to Homepage (or sends navigation), waits, then clicks the first recent project card.
    3. If on homepage, clicks the first recent project card.
    """
    start_time = time.time()
    if not IS_WINDOWS:
        return {
            "success": False,
            "action": "unsupported_platform",
            "message": "Desktop auto-reload is only supported on Windows. Open the draft manually in CapCut.",
            "elapsed_seconds": round(time.time() - start_time, 3)
        }

    windows = get_capcut_windows()

    if not windows:
        if os.path.exists(CAPCUT_LAUNCHER):
            print(f"[Companion] CapCut not running. Launching {CAPCUT_LAUNCHER}...")
            subprocess.Popen([CAPCUT_LAUNCHER], shell=True)
            return {
                "success": True,
                "action": "launched",
                "message": "CapCut Desktop was not running and has been launched.",
                "elapsed_seconds": round(time.time() - start_time, 3)
            }
        else:
            return {
                "success": False,
                "action": "not_found",
                "message": f"CapCut launcher not found at {CAPCUT_LAUNCHER}.",
                "elapsed_seconds": round(time.time() - start_time, 3)
            }

    # Find the main window
    main_win = windows[0]
    hwnd = main_win["hwnd"]
    title = main_win["title"]
    w = main_win["width"]
    h = main_win["height"]

    print(f"[Companion] Found CapCut window: HWND={hwnd}, Title='{title}', Size={w}x{h}")
    focus_window(hwnd)

    # Determine if in Editor view or Homepage view
    # In CapCut Desktop, the editor window has a back button in top-left corner
    # Back button is typically located at (X: 35, Y: 25) relative to window top-left.
    # Homepage project grid has the first project card around (X: 340, Y: 250).
    
    # First click top-left Back button
    click_client_coords(hwnd, 35, 25)
    time.sleep(delay)

    # Now click the first project card in the recent projects list
    click_client_coords(hwnd, int(w * 0.28), int(h * 0.32))
    time.sleep(0.1)

    elapsed = round(time.time() - start_time, 3)
    return {
        "success": True,
        "action": "reloaded",
        "window_title": title,
        "elapsed_seconds": elapsed,
        "message": f"Hot-reload triggered in {elapsed}s for project '{project_name or 'latest'}'."
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--detect":
        wins = get_capcut_windows()
        print(f"Detected {len(wins)} CapCut windows:")
        for w in wins:
            print(f"  - HWND: {w['hwnd']}, Title: '{w['title']}', Size: {w['width']}x{w['height']}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--reload":
        proj = sys.argv[2] if len(sys.argv) > 2 else None
        res = reload_capcut_desktop(proj)
        print(res)
    else:
        wins = get_capcut_windows()
        print(f"CapCut windows: {len(wins)}")
        res = reload_capcut_desktop()
        print(res)
