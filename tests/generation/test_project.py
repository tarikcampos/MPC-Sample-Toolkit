from pathlib import Path

import pytest

from mpctk.generation import generate_project_from_template
from mpctk.music import (
    BankSpec,
    LAYOUT_SCALE_PADS,
)
from mpctk.xpj import (
    XPJHeader,
    XPJProject,
    XPJReader,
    XPJWriter,
)


def make_project_data(instrument_count=32):
    instruments = []

    for index in range(instrument_count):
        has_sample = index == 0

        instruments.append(
            {
                "layersv": [
                    {
                        "active": True,
                        "sampleName": "Source" if has_sample else "",
                        "sampleFile": "Source.wav" if has_sample else "",
                        "pitch": 0.0,
                        "coarseTune": 0,
                        "sliceInfo": {
                            "Start": 0,
                            "End": 1000 if has_sample else 0,
                        },
                    }
                ]
            }
        )

    return {
        "data": {
            "version": 28,
            "key": "test",
            "samples": [],
            "tracks": [
                {
                    "program": {
                        "drum": {
                            "instruments": instruments,
                        }
                    }
                }
            ],
        }
    }


def make_header():
    return XPJHeader(
        magic="ACVS",
        version="1.3.0.12",
        data_type="SerialisableProjectData",
        serialization_format="json",
        platform="Linux",
    )


def make_spec():
    return BankSpec(
        source_root="C",
        target_root="D",
        layout=LAYOUT_SCALE_PADS,
        scale="natural_minor",
        pads=8,
        start_octave=-1,
    )


def test_generate_project_from_template_writes_finished_xpj(tmp_path):
    template = tmp_path / "template.xpj"
    output = tmp_path / "finished.xpj"

    XPJWriter().write(
        template,
        make_header(),
        make_project_data(),
    )

    result = generate_project_from_template(
        template,
        output,
        make_spec(),
        start_bank="B",
        start_pad=1,
    )

    assert result == output
    assert output.is_file()

    header, data = XPJReader().read(output)
    project = XPJProject.from_dict(data)

    assert header == make_header()

    expected_offsets = [
        -10,
        -8,
        -7,
        -5,
        -3,
        -2,
        0,
        2,
    ]

    generated = [
        project.tracks[0].instruments[index].layers[0]
        for index in range(16, 24)
    ]

    assert [
        layer.coarse_tune
        for layer in generated
    ] == expected_offsets

    for layer in generated:
        assert layer.sample.name == "Source"
        assert layer.sample.file == "Source.wav"


def test_generate_project_preserves_source_template(tmp_path):
    template = tmp_path / "template.xpj"
    output = tmp_path / "finished.xpj"

    writer = XPJWriter()
    reader = XPJReader()

    writer.write(
        template,
        make_header(),
        make_project_data(),
    )

    original_bytes = template.read_bytes()

    generate_project_from_template(
        template,
        output,
        make_spec(),
        start_bank="B",
        start_pad=1,
    )

    assert template.read_bytes() == original_bytes

    _, template_data = reader.read(template)
    template_project = XPJProject.from_dict(template_data)

    assert (
        template_project.tracks[0]
        .instruments[16]
        .layers[0]
        .sample.is_empty
    )


def test_generate_project_rejects_invalid_track_index(tmp_path):
    template = tmp_path / "template.xpj"
    output = tmp_path / "finished.xpj"

    XPJWriter().write(
        template,
        make_header(),
        make_project_data(),
    )

    with pytest.raises(
        IndexError,
        match="Track index is out of range",
    ):
        generate_project_from_template(
            template,
            output,
            make_spec(),
            track_index=1,
        )


def test_generate_project_rejects_non_integer_track_index(tmp_path):
    template = tmp_path / "template.xpj"
    output = tmp_path / "finished.xpj"

    XPJWriter().write(
        template,
        make_header(),
        make_project_data(),
    )

    with pytest.raises(
        TypeError,
        match="Track index must be an integer",
    ):
        generate_project_from_template(
            template,
            output,
            make_spec(),
            track_index=True,
        )
