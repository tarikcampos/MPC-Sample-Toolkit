import pytest

from mpctk.music import (
    BankSpec,
    LAYOUT_CHROMATIC_KEYBOARD,
    LAYOUT_SCALE_PADS,
)


def test_bank_spec_builds_chromatic_keyboard():
    spec = BankSpec(
        source_root="C",
        target_root="D",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        pads=8,
    )

    assert spec.build_offsets() == [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
    ]


def test_bank_spec_builds_major_scale_pads():
    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_SCALE_PADS,
        scale="major",
        pads=8,
    )

    assert spec.build_offsets() == [
        0,
        2,
        4,
        5,
        7,
        9,
        11,
        12,
    ]


def test_bank_spec_builds_minor_scale_pads_with_root_transposition():
    spec = BankSpec(
        source_root="C",
        target_root="D",
        layout=LAYOUT_SCALE_PADS,
        scale="natural_minor",
        pads=16,
        start_octave=-1,
    )

    assert spec.build_offsets() == [
        -10,
        -8,
        -7,
        -5,
        -3,
        -2,
        0,
        2,
        4,
        5,
        7,
        9,
        10,
        12,
        14,
        16,
    ]


def test_bank_spec_chromatic_layout_rejects_scale():
    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        scale="major",
        pads=8,
    )

    with pytest.raises(
        ValueError,
        match="does not use a scale",
    ):
        spec.build_offsets()


def test_bank_spec_scale_layout_requires_scale():
    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_SCALE_PADS,
        pads=8,
    )

    with pytest.raises(
        ValueError,
        match="requires a scale",
    ):
        spec.build_offsets()


def test_bank_spec_rejects_unknown_scale():
    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_SCALE_PADS,
        scale="dorian",
        pads=8,
    )

    with pytest.raises(
        ValueError,
        match="Unknown scale",
    ):
        spec.build_offsets()


def test_bank_spec_rejects_unknown_layout():
    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout="piano_mode",
        pads=8,
    )

    with pytest.raises(
        ValueError,
        match="Unknown layout",
    ):
        spec.build_offsets()


def test_bank_spec_rejects_zero_pads():
    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        pads=0,
    )

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        spec.build_offsets()
