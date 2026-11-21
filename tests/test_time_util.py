import pytest

from pyJianYingDraft import trange, tim, SEC


@pytest.mark.parametrize("bpm", [128, 136, 140, 174])
@pytest.mark.parametrize("beats", [1, 2, 4])
@pytest.mark.parametrize("as_string", [False, True])
def test_back_to_back_ranges_do_not_overlap(bpm, beats, as_string):
    """Regression test: trange used to round start and duration separately,
    so a range starting where the previous one ended could overlap it by 1us
    and make add_segment raise SegmentOverlap (e.g. the 6th 4-beat bar at
    136 BPM)."""
    length = 60 / bpm * beats  # seconds
    ranges = [
        trange(f"{i * length}s", f"{length}s") if as_string
        else trange(i * length * SEC, length * SEC)
        for i in range(64)
    ]
    for prev, cur in zip(ranges, ranges[1:]):
        assert cur.start == prev.end
        assert not prev.overlaps(cur)


def test_trange_rounds_end_not_duration():
    r = trange(0.6 * SEC, 0.3 * SEC)
    assert r.start == tim(0.6 * SEC)
    assert r.end == tim(0.9 * SEC)


def test_trange_string_inputs_unchanged():
    r = trange("1h2m3.5s", "0.25s")
    assert r.start == 3723_500_000
    assert r.duration == 250_000
