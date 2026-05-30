import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class DraftProfile:
    name: str
    template_dir: str
    content_file: str
    content_mirrors: tuple[str, ...] = ()
    timeline_content_file: Optional[str] = None
    is_capcut_env: bool = True
    platform: Optional[Dict[str, object]] = None


CAPCUT_PLATFORM = {
    "app_id": 359289,
    "app_source": "cc",
    "app_version": "6.5.0",
    "device_id": "c4ca4238a0b923820dcc509a6f75849b",
    "hard_disk_id": "307563e0192a94465c0e927fbc482942",
    "mac_address": "c3371f2d4fb02791c067ce44d8fb4ed5",
    "os": "mac",
    "os_version": "15.5",
}

JIANYING_10_PLATFORM = {
    "app_id": 3704,
    "app_source": "lv",
    "app_version": "10.2.0",
    "os": "windows",
}

PROFILES: Dict[str, DraftProfile] = {
    "capcut_legacy": DraftProfile(
        name="capcut_legacy",
        template_dir="template",
        content_file="draft_info.json",
        is_capcut_env=True,
        platform=CAPCUT_PLATFORM,
    ),
    "jianying_legacy": DraftProfile(
        name="jianying_legacy",
        template_dir="template_jianying",
        content_file="draft_info.json",
        is_capcut_env=False,
        platform=JIANYING_10_PLATFORM,
    ),
    "jianying_pro_10": DraftProfile(
        name="jianying_pro_10",
        template_dir="template_jianying_10_2",
        content_file="draft_content.json",
        content_mirrors=("draft_content.json.bak", "template-2.tmp"),
        timeline_content_file="template.tmp",
        is_capcut_env=False,
        platform=JIANYING_10_PLATFORM,
    ),
}

PROFILE_ALIASES = {
    "capcut": "capcut_legacy",
    "capcut_legacy": "capcut_legacy",
    "jianying": "jianying_legacy",
    "jianying_legacy": "jianying_legacy",
    "jianying_10": "jianying_pro_10",
    "jianying_10_x": "jianying_pro_10",
    "jianying_pro_10": "jianying_pro_10",
    "jianying_pro_10_2": "jianying_pro_10",
    "jianying_pro_10_2_0": "jianying_pro_10",
}


def normalize_profile_name(name: Optional[str]) -> str:
    if not name:
        return "capcut_legacy"
    key = name.strip().lower().replace(".", "_").replace("-", "_")
    if key not in PROFILE_ALIASES:
        raise ValueError(
            f"Unknown draft profile '{name}'. Supported profiles: {', '.join(sorted(PROFILE_ALIASES))}"
        )
    return PROFILE_ALIASES[key]


def get_draft_profile(name: Optional[str] = None) -> DraftProfile:
    if name is None:
        try:
            from settings.local import DRAFT_PROFILE
        except Exception:
            DRAFT_PROFILE = "capcut_legacy"
        name = DRAFT_PROFILE
    return PROFILES[normalize_profile_name(name)]


def get_template_dir(name: Optional[str] = None) -> str:
    return get_draft_profile(name).template_dir


def write_profile_content(profile: DraftProfile, draft_dir: os.PathLike, content: str) -> List[Path]:
    draft_path = Path(draft_dir)
    written: List[Path] = []

    targets = [profile.content_file, *profile.content_mirrors]
    for relative_path in targets:
        path = draft_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    if profile.timeline_content_file:
        timelines_dir = draft_path / "Timelines"
        if timelines_dir.exists():
            for timeline_dir in timelines_dir.iterdir():
                if timeline_dir.is_dir():
                    path = timeline_dir / profile.timeline_content_file
                    path.write_text(content, encoding="utf-8")
                    written.append(path)

    return written
