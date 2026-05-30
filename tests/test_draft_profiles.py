import json
from pathlib import Path

import pytest


def test_jianying_10_profile_uses_versioned_template_and_content_names():
    from draft_profiles import get_draft_profile

    profile = get_draft_profile("jianying_pro_10")

    assert profile.name == "jianying_pro_10"
    assert profile.template_dir == "template_jianying_10_2"
    assert profile.content_file == "draft_content.json"
    assert "template-2.tmp" in profile.content_mirrors
    assert profile.is_capcut_env is False


def test_legacy_profiles_keep_existing_template_names():
    from draft_profiles import get_draft_profile

    capcut = get_draft_profile("capcut_legacy")
    jianying = get_draft_profile("jianying_legacy")

    assert capcut.template_dir == "template"
    assert capcut.content_file == "draft_info.json"
    assert capcut.is_capcut_env is True
    assert jianying.template_dir == "template_jianying"
    assert jianying.content_file == "draft_info.json"
    assert jianying.is_capcut_env is False


def test_write_profile_content_updates_main_mirrors_and_timeline(tmp_path):
    from draft_profiles import get_draft_profile, write_profile_content

    draft_dir = tmp_path / "draft"
    timeline_dir = draft_dir / "Timelines" / "timeline-1"
    timeline_dir.mkdir(parents=True)

    payload = {"tracks": [], "materials": {}, "duration": 0}
    profile = get_draft_profile("jianying_pro_10")

    written = write_profile_content(profile, draft_dir, json.dumps(payload, ensure_ascii=False))

    expected = {
        draft_dir / "draft_content.json",
        draft_dir / "template-2.tmp",
        timeline_dir / "template.tmp",
    }
    assert expected.issubset(set(written))
    for path in expected:
        assert json.loads(path.read_text(encoding="utf-8")) == payload


def test_windows_draft_asset_path_keeps_drive_root():
    from save_draft_impl import build_asset_path

    path = build_asset_path(
        r"D:\JianyingPro Drafts",
        "draft-1",
        "video",
        "clip.mp4",
    )

    assert path == r"D:\JianyingPro Drafts\draft-1\assets\video\clip.mp4"


def test_shared_draft_asset_path_keeps_drive_root():
    from util import build_draft_asset_path

    assert build_draft_asset_path(
        r"D:\JianyingPro Drafts",
        "draft-1",
        "image",
        "cover.png",
    ) == r"D:\JianyingPro Drafts\draft-1\assets\image\cover.png"
