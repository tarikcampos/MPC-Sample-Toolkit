import pytest

from mpctk.music import (
    MAJOR_INTERVALS,
    NATURAL_MINOR_INTERVALS,
    build_chromatic_offsets,
    build_scale_pad_offsets,
)


def test_build_chromatic_offsets_from_same_root():
    assert build_chromatic_offsets(
        "C",
        "C",
        8,
    ) == [0, 1, 2, 3, 4, 5, 6, 7]


def test_build_chromatic_offsets_transposes_source_root():
    assert build_chromatic_offsets(
        "C",
        "D",
        8,
    ) == [2, 3, 4, 5, 6, 7, 8, 9]


def test_build_chromatic_offsets_can_start_lower_octave():
    assert build_chromatic_offsets(
        "C",
        "C",
        8,
        start_octave=-1,
    ) == [-12, -11, -10, -9, -8, -7, -6, -5]


def test_build_chromatic_offsets_uses_shortest_root_transposition():
    assert build_chromatic_offsets(
        "C",
        "G",
        4,
    ) == [-5, -4, -3, -2]


def test_build_chromatic_offsets_rejects_invalid_count():
    with pytest.raises(ValueError, match="greater than zero"):
        build_chromatic_offsets("C", "C", 0)


def test_build_major_scale_pad_offsets():
    assert build_scale_pad_offsets(
        "C",
        "C",
        MAJOR_INTERVALS,
        10,
    ) == [
        0,
        2,
        4,
        5,
        7,
        9,
        11,
        12,
        14,
        16,
    ]


def test_build_minor_scale_pad_offsets_with_target_root():
    assert build_scale_pad_offsets(
        "C",
        "D",
        NATURAL_MINOR_INTERVALS,
        10,
    ) == [
        2,
        4,
        5,
        7,
        9,
        10,
        12,
        14,
        16,
        17,
    ]


def test_build_scale_pad_offsets_can_start_lower_octave():
    assert build_scale_pad_offsets(
        "C",
        "C",
        MAJOR_INTERVALS,
        8,
        start_octave=-1,
    ) == [
        -12,
        -10,
        -8,
        -7,
        -5,
        -3,
        -1,
        0,
    ]


def test_chromatic_and_scale_layouts_are_intentionally_different():
    chromatic = build_chromatic_offsets(
        "C",
        "C",
        8,
    )

    scale = build_scale_pad_offsets(
        "C",
        "C",
        MAJOR_INTERVALS,
        8,
    )

    assert chromatic == [0, 1, 2, 3, 4, 5, 6, 7]
    assert scale == [0, 2, 4, 5, 7, 9, 11, 12]
    assert chromatic != scale
