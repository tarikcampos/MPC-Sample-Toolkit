import pytest

from mpctk.xpj import (
    Instrument,
    Layer,
    SampleReference,
    Track,
    XPJProject,
)


def test_empty_sample_reference():
    sample = SampleReference()

    assert sample.name is None
    assert sample.file is None
    assert sample.is_empty is True


def test_sample_reference():
    sample = SampleReference(
        name="BD 808 Sat Click Decay C 04",
        file="BD 808 Sat Click Decay C 04.wav",
    )

    assert sample.name == "BD 808 Sat Click Decay C 04"
    assert sample.file == "BD 808 Sat Click Decay C 04.wav"
    assert sample.is_empty is False


def test_layer_from_dict():
    layer = Layer.from_dict(
        {
            "sampleName": "Kick",
            "sampleFile": "Kick.wav",
        }
    )

    assert layer.sample.name == "Kick"
    assert layer.sample.file == "Kick.wav"
    assert layer.is_empty is False


def test_empty_layer():
    layer = Layer.from_dict({})

    assert layer.is_empty is True


def test_instrument_from_dict():
    instrument = Instrument.from_dict(
        {
            "layersv": [
                {
                    "sampleName": "Kick",
                    "sampleFile": "Kick.wav",
                },
                {},
            ]
        }
    )

    assert len(instrument.layers) == 2
    assert instrument.layers[0].sample.name == "Kick"
    assert instrument.layers[1].is_empty is True


def test_track_from_dict():
    track = Track.from_dict(
        {
            "program": {
                "drum": {
                    "instruments": [
                        {
                            "layersv": [
                                {
                                    "sampleName": "Kick",
                                    "sampleFile": "Kick.wav",
                                }
                            ]
                        }
                    ]
                }
            }
        }
    )

    assert len(track.instruments) == 1
    assert len(track.instruments[0].layers) == 1
    assert track.instruments[0].layers[0].sample.file == "Kick.wav"


def test_project_builds_instruments_and_layers():
    data = {
        "data": {
            "version": 28,
            "key": "C Major",
            "tracks": [
                {
                    "program": {
                        "drum": {
                            "instruments": [
                                {
                                    "layersv": [
                                        {
                                            "sampleName": "Kick",
                                            "sampleFile": "Kick.wav",
                                        },
                                        {},
                                    ]
                                }
                            ]
                        }
                    }
                }
            ],
        }
    }

    project = XPJProject.from_dict(data)

    assert project.version == 28
    assert project.key == "C Major"
    assert len(project.tracks) == 1
    assert len(project.tracks[0].instruments) == 1
    assert len(project.tracks[0].instruments[0].layers) == 2
    assert project.tracks[0].instruments[0].layers[0].sample.name == "Kick"
    assert project.tracks[0].instruments[0].layers[1].is_empty is True


def test_project_requires_data_object():
    with pytest.raises(ValueError, match="must contain a 'data' object"):
        XPJProject.from_dict({})


def test_project_rejects_non_dictionary():
    with pytest.raises(TypeError, match="must be a dictionary"):
        XPJProject.from_dict([])
