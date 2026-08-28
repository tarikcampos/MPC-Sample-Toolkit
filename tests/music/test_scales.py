import pytest

from mpctk.music import (
    CHROMATIC_INTERVALS,
    MAJOR_INTERVALS,
    NATURAL_MINOR_INTERVALS,
    build_scale_offsets,
)


def test_build_chromatic_offsets():
    offsets = build_scale_offsets(
        CHROMATIC_INTERVALS,
        16,
    )

    assert offsets == list(range(16))


def test_build_major_scale_offsets():
    offsets = build_scale_offsets(
        MAJOR_INTERVALS,
        10,
    )

    assert offsets == [
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


def test_build_natural_minor_scale_offsets():
    offsets = build_scale_offsets(
        NATURAL_MINOR_INTERVALS,
        10,
    )

    assert offsets == [
        0,
        2,
        3,
        5,
        7,
        8,
        10,
        12,
        14,
        15,
    ]


def test_build_scale_offsets_supports_negative_start_octave():
    offsets = build_scale_offsets(
        MAJOR_INTERVALS,
        4,
        start_octave=-1,
    )

    assert offsets == [-12, -10, -8, -7]


def test_build_scale_offsets_rejects_zero_count():
    with pytest.raises(ValueError, match="greater than zero"):
        build_scale_offsets(MAJOR_INTERVALS, 0)


def test_build_scale_offsets_rejects_empty_intervals():
    with pytest.raises(ValueError, match="must not be empty"):
        build_scale_offsets([], 4)


def test_build_scale_offsets_rejects_non_integer_intervals():
    with pytest.raises(TypeError, match="must be integers"):
        build_scale_offsets([0, 2, 3.5], 4)


def test_build_scale_offsets_rejects_out_of_range_intervals():
    with pytest.raises(ValueError, match="between 0 and 11"):
        build_scale_offsets([0, 4, 12], 4)


def test_build_scale_offsets_rejects_unsorted_intervals():
    with pytest.raises(
        ValueError,
        match="unique and in ascending order",
    ):
        build_scale_offsets([0, 7, 4], 4)


def test_build_scale_offsets_rejects_duplicate_intervals():
    with pytest.raises(
        ValueError,
        match="unique and in ascending order",
    ):
        build_scale_offsets([0, 4, 4, 7], 4)


def test_build_major_scale_offsets_with_negative_start_octave():
    offsets = build_scale_offsets(
        MAJOR_INTERVALS,
        16,
        start_octave=-1,
    )

    assert offsets == [
        -12,
        -10,
        -8,
        -7,
        -5,
        -3,
        -1,
        0,
        2,
        4,
        5,
        7,
        9,
        11,
        12,
        14,
    ]
