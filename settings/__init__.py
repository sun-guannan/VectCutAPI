"""
配置包入口，导出所有配置
"""

# 从local模块导入所有配置，local模块已经导入了env和base模块的配置
from .local import *

__all__ = [
    "IS_CAPCUT_ENV",
    "DRAFT_PROFILE",
    "API_KEYS",
    "MODEL_CONFIG",
    "PURCHASE_LINKS",
    "LICENSE_CONFIG"
]

# 提供一个获取平台信息的辅助函数
def get_platform_info():
    """
    获取平台信息，用于script_file.py中的dumps方法，cap_cut需要返回platform信息
    
    Returns:
        dict: 平台信息字典
    """
    if not IS_CAPCUT_ENV:
        return None
        
    return {
        "app_id": 359289,
        "app_source": "cc",
        "app_version": "6.5.0",
        "device_id": "c4ca4238a0b923820dcc509a6f75849b",
        "hard_disk_id": "307563e0192a94465c0e927fbc482942",
        "mac_address": "c3371f2d4fb02791c067ce44d8fb4ed5",
        "os": "mac",
        "os_version": "15.5"
    }
