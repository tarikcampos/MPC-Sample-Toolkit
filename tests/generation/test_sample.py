from pathlib import Path
import wave

import pytest

from mpctk.generation import (
    build_sample_pool_entry,
    inject_wav_sample,
    wav_frame_count,
)
from mpctk.xpj import XPJProject


def write_test_wav(
    path: Path,
    *,
    frames: int = 100,
    channels: int = 1,
    sample_width: int = 2,
    sample_rate: int = 44100,
):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(sample_rate)
        wav.writeframes(
            b"\x00" * frames * channels * sample_width
        )


def make_project():
    instruments = []

    for _ in range(4):
        instruments.append(
            {
                "layersv": [
                    {
                        "active": True,
                        "sampleName": "",
                        "sampleFile": "",
                        "pitch": 0.0,
                        "coarseTune": 0,
                        "sampleStart": 0,
                        "sampleEnd": 0,
                        "sliceIndex": 129,
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
                    }
                ]
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

    return XPJProject.from_dict(data)


def test_wav_frame_count(tmp_path):
    wav_path = tmp_path / "Sample.wav"
    write_test_wav(wav_path, frames=56546)

    assert wav_frame_count(wav_path) == 56546


def test_wav_frame_count_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        wav_frame_count(tmp_path / "missing.wav")


def test_build_sample_pool_entry():
    entry = build_sample_pool_entry(
        Path("/tmp/My Sample.wav")
    )

    assert entry == {
        "loadImpl": 0,
        "metadata": {
            "key": "G# Major",
            "rootNote": 60,
            "tempo": 0.0,
            "tune": 0.0,
        },
        "name": "My Sample",
        "path": "My Sample.wav",
        "version": 1,
    }


def test_inject_wav_sample_populates_project(tmp_path):
    wav_path = tmp_path / "Injected.wav"
    write_test_wav(wav_path, frames=56546)

    project = make_project()

    inject_wav_sample(
        project,
        wav_path,
        track_index=0,
        instrument_index=2,
    )

    project_data = project.raw_data["data"]
    track_raw = project_data["tracks"][0]

    assert len(project_data["samples"]) == 1
    assert len(track_raw["samples"]) == 1

    assert (
        project_data["samples"][0]
        == track_raw["samples"][0]
    )

    entry = project_data["samples"][0]

    assert entry["name"] == "Injected"
    assert entry["path"] == "Injected.wav"

    layer = project.tracks[0].instruments[2].layers[0]

    assert layer.sample.name == "Injected"
    assert layer.sample.file == "Injected.wav"
    assert layer.sample_start == 0
    assert layer.sample_end == 0
    assert layer.slice_index == 129
    assert layer.slice_info.start == 0
    assert layer.slice_info.end == 56545


def test_inject_wav_sample_replaces_duplicate_pool_entry(tmp_path):
    wav_path = tmp_path / "Injected.wav"
    write_test_wav(wav_path)

    project = make_project()

    inject_wav_sample(project, wav_path)
    inject_wav_sample(project, wav_path)

    project_data = project.raw_data["data"]
    track_raw = project_data["tracks"][0]

    assert len(project_data["samples"]) == 1
    assert len(track_raw["samples"]) == 1


def test_inject_wav_sample_rejects_bad_track_index(tmp_path):
    wav_path = tmp_path / "Injected.wav"
    write_test_wav(wav_path)

    project = make_project()

    with pytest.raises(
        IndexError,
        match="Track index is out of range",
    ):
        inject_wav_sample(
            project,
            wav_path,
            track_index=1,
        )
