from collections.abc import Sequence

from .notes import root_offset
from .scales import build_scale_offsets


def build_chromatic_offsets(
    source_root: str,
    target_root: str,
    count: int,
    *,
    start_octave: int = 0,
) -> list[int]:
    """Build semitone offsets for a chromatic keyboard layout."""
    if count <= 0:
        raise ValueError("Count must be greater than zero")

    base_offset = (
        root_offset(source_root, target_root)
        + start_octave * 12
    )

    return [
        base_offset + index
        for index in range(count)
    ]


def build_scale_pad_offsets(
    source_root: str,
    target_root: str,
    intervals: Sequence[int],
    count: int,
    *,
    start_octave: int = 0,
) -> list[int]:
    """Build semitone offsets for a scale-only pad layout."""
    base_offset = root_offset(source_root, target_root)

    scale_offsets = build_scale_offsets(
        intervals,
        count,
        start_octave=start_octave,
    )

    return [
        base_offset + offset
        for offset in scale_offsets
    ]
