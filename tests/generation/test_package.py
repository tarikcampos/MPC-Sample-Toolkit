from pathlib import Path
import wave

import pytest

from mpctk.generation import (
    generate_project_package,
    project_data_directory_name,
)
from mpctk.music import (
    BankSpec,
    LAYOUT_SCALE_PADS,
)
from mpctk.xpj import (
    XPJProject,
    XPJReader,
    XPJWriter,
)


def write_test_wav(
    path: Path,
    *,
    frames: int = 100,
):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00" * frames * 2)


def make_template(path: Path):
    instruments = []

    for _ in range(128):
        layers = []

        for _ in range(8):
            layers.append(
                {
                    "active": True,
                    "volume": {
                        "gainCoefficient": 1.0,
                        "controlValue": 1.0,
                        "law": 1,
                    },
                    "pan": 0.5,
                    "pitch": 0.0,
                    "coarseTune": 0,
                    "fineTune": 0,
                    "velocityStart": 0,
                    "velocityEnd": 127,
                    "sampleStart": 0,
                    "sampleEnd": 0,
                    "loop": False,
                    "loopStart": 0,
                    "loopEnd": 0,
                    "loopCrossfadeLength": 0,
                    "loopFineTune": 0,
                    "mute": False,
                    "rootNote": 0,
                    "keyTrackEnable": False,
                    "sampleName": "",
                    "sampleFile": "",
                    "sliceIndex": 129,
                    "direction": 0,
                    "offset": 0,
                    "sliceInfo": {
                        "Start": 0,
                        "End": 0,
                        "LoopStart": 0,
                        "LoopMode": 0,
                        "PulsePosition": 0,
                        "LoopCrossfadeLength": 0,
                        "LoopCrossfadeType": 0,
                        "TailLength": 0.0,
                        "TailLoopPosition": 0.5,
                    },
                    "version": 11,
                    "pitchRandom": 0.0,
                    "VolumeRandom": 0.0,
                    "PanRandom": 0.0,
                    "OffsetRandom": 0.0,
                    "layerLoopModeOverridesSliceLoopMode": True,
                    "loopMode": 0,
                }
            )

        instruments.append(
            {
                "layersv": layers,
            }
        )

    data = {
        "data": {
            "version": 28,
            "key": "test",
            "samples": [],
            "tracks": [
                {
                    "samples": [],
                    "program": {
                        "drum": {
                            "instruments": instruments,
                        }
                    },
                }
            ],
        }
    }

    project = XPJProject.from_dict(data)

    from mpctk.xpj.reader import XPJHeader

    header = XPJHeader(
        magic="ACVS",
        version="1.3.0.12",
        data_type="SerialisableProjectData",
        serialization_format="json",
        platform="Linux",
    )

    XPJWriter().write(
        path,
        header,
        project.raw_data,
    )


def test_project_data_directory_name():
    assert (
        project_data_directory_name("My Project")
        == "My Project_[ProjectData]"
    )

    assert (
        project_data_directory_name("My Project.xpj")
        == "My Project_[ProjectData]"
    )


def test_project_data_directory_name_rejects_path():
    with pytest.raises(ValueError):
        project_data_directory_name(
            "folder/My Project"
        )


def test_generate_project_package(tmp_path):
    source = tmp_path / "Source.wav"
    template = tmp_path / "Template.xpj"
    destination = tmp_path / "output"

    write_test_wav(
        source,
        frames=56546,
    )
    make_template(template)

    spec = BankSpec(
        source_root="C",
        target_root="D",
        layout=LAYOUT_SCALE_PADS,
        scale="natural_minor",
        pads=16,
        start_octave=-1,
    )

    project_path, project_data_dir = (
        generate_project_package(
            source,
            template,
            destination,
            "Generated Project",
            spec,
            source_instrument_index=0,
            start_bank="B",
            start_pad=1,
        )
    )

    assert project_path == (
        destination / "Generated Project.xpj"
    )

    assert project_data_dir == (
        destination
        / "Generated Project_[ProjectData]"
    )

    copied_wav = (
        project_data_dir / "Source.wav"
    )

    assert project_path.is_file()
    assert project_data_dir.is_dir()
    assert copied_wav.read_bytes() == source.read_bytes()

    _, data = XPJReader().read(project_path)
    project = XPJProject.from_dict(data)

    assert data["data"]["samples"][0]["path"] == "Source.wav"

    track_samples = (
        data["data"]["tracks"][0]["samples"]
    )

    assert track_samples[0]["path"] == "Source.wav"

    source_layer = (
        project.tracks[0]
        .instruments[0]
        .layers[0]
    )

    assert source_layer.sample.file == "Source.wav"
    assert source_layer.slice_info.end == 56545

    expected_offsets = [
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

    actual_offsets = [
        project.tracks[0]
        .instruments[index]
        .layers[0]
        .coarse_tune
        for index in range(16, 32)
    ]

    assert actual_offsets == expected_offsets


def test_generate_project_package_rejects_existing_project(
    tmp_path,
):
    source = tmp_path / "Source.wav"
    template = tmp_path / "Template.xpj"
    destination = tmp_path / "output"

    write_test_wav(source)
    make_template(template)

    destination.mkdir()
    (destination / "Existing.xpj").write_bytes(b"")

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_SCALE_PADS,
        scale="natural_minor",
        pads=1,
    )

    with pytest.raises(
        FileExistsError,
        match="Project already exists",
    ):
        generate_project_package(
            source,
            template,
            destination,
            "Existing",
            spec,
        )


def test_generate_project_package_rejects_existing_data_dir(
    tmp_path,
):
    source = tmp_path / "Source.wav"
    template = tmp_path / "Template.xpj"
    destination = tmp_path / "output"

    write_test_wav(source)
    make_template(template)

    destination.mkdir()
    (
        destination
        / "Existing_[ProjectData]"
    ).mkdir()

    spec = BankSpec(
        source_root="C",
        target_root="C",
        layout=LAYOUT_SCALE_PADS,
        scale="natural_minor",
        pads=1,
    )

    with pytest.raises(
        FileExistsError,
        match="Project data directory already exists",
    ):
        generate_project_package(
            source,
            template,
            destination,
            "Existing",
            spec,
        )
