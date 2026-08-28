import pytest

from mpctk.generation import build_bank_with_mpc_tuning
from mpctk.music import (
    BankSpec,
    LAYOUT_CHROMATIC_KEYBOARD,
    LAYOUT_SCALE_PADS,
)
from mpctk.xpj import Track


def make_track(instrument_count=32):
    def layer(sample_name="", sample_file=""):
        return {
            "active": True,
            "sampleName": sample_name,
            "sampleFile": sample_file,
            "pitch": 0.0,
            "coarseTune": 0,
            "sliceInfo": {
                "Start": 0,
                "End": 1000 if sample_name else 0,
            },
        }

    instruments = [
        {"layersv": [layer("Sample", "Sample.wav")]}
    ]

    instruments.extend(
        {"layersv": [layer()]}
        for _ in range(instrument_count - 1)
    )

    return Track.from_dict(
        {
            "program": {
                "drum": {
                    "instruments": instruments,
                }
            }
        }
    )


def test_build_bank_with_mpc_tuning_applies_scale_spec():
    track = make_track()

    spec = BankSpec(
        source_root="C",
        target_root="D",
        layout=LAYOUT_SCALE_PADS,
        scale="natural_minor",
        pads=16,
        start_octave=-1,
    )

    generated = build_bank_with_mpc_tuning(
        track,
        spec,
    )

    assert [layer.coarse_tune for layer in generated] == [
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

    for layer in generated:
        assert layer.sample.name == "Sample"
        assert layer.sample.file == "Sample.wav"


def test_build_bank_with_mpc_tuning_applies_chromatic_spec():
    track = make_track()

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        pads=16,
        start_octave=-1,
    )

    generated = build_bank_with_mpc_tuning(
        track,
        spec,
    )

    assert [layer.coarse_tune for layer in generated] == list(
        range(-12, 4)
    )


def test_build_bank_with_mpc_tuning_rejects_positive_overflow():
    track = make_track(instrument_count=64)

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        pads=32,
    )

    with pytest.raises(
        ValueError,
        match=r"requested 0 to 31",
    ):
        build_bank_with_mpc_tuning(
            track,
            spec,
        )


def test_build_bank_with_mpc_tuning_rejects_negative_overflow():
    track = make_track(instrument_count=64)

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        pads=32,
        start_octave=-3,
    )

    with pytest.raises(
        ValueError,
        match=r"requested -36 to -5",
    ):
        build_bank_with_mpc_tuning(
            track,
            spec,
        )


def test_build_bank_from_pad_address_finds_source_automatically():
    from mpctk.generation import build_bank_from_pad_address

    track = make_track(instrument_count=32)

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_SCALE_PADS,
        scale="major",
        pads=8,
    )

    generated = build_bank_from_pad_address(
        track,
        spec,
        start_bank="B",
        start_pad=1,
    )

    assert [layer.coarse_tune for layer in generated] == [
        0,
        2,
        4,
        5,
        7,
        9,
        11,
        12,
    ]

    for layer in generated:
        assert layer.sample.name == "Sample"
        assert layer.sample.file == "Sample.wav"

    assert (
        track.instruments[16].layers[0].sample.name
        == "Sample"
    )


def test_build_bank_from_pad_address_starts_inside_bank():
    from mpctk.generation import build_bank_from_pad_address

    track = make_track(instrument_count=32)

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_CHROMATIC_KEYBOARD,
        pads=4,
    )

    generated = build_bank_from_pad_address(
        track,
        spec,
        start_bank="A",
        start_pad=13,
    )

    assert [layer.coarse_tune for layer in generated] == [
        0,
        1,
        2,
        3,
    ]

    assert (
        track.instruments[12].layers[0].sample.name
        == "Sample"
    )
