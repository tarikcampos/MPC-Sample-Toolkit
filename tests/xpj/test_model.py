import pytest

from mpctk.xpj.model import (
    SLICE_INDEX_LAYER_REGION,
    SLICE_INDEX_UNKNOWN_128,
    SliceInfo,
)

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
            "active": True,
            "mute": False,
            "sampleName": "Kick",
            "sampleFile": "Kick.wav",
            "pan": 0.5,
            "pitch": 0.0,
            "coarseTune": 0,
            "fineTune": 0,
            "rootNote": 0,
            "keyTrackEnable": False,
            "velocityStart": 0,
            "velocityEnd": 127,
            "sampleStart": 0,
            "sampleEnd": 0,
            "sliceIndex": 129,
            "sliceInfo": {
                "Start": 244834,
                "End": 1020144,
                "LoopStart": 244834,
                "LoopMode": 1,
                "PulsePosition": 0,
                "LoopCrossfadeLength": 0,
                "LoopCrossfadeType": 0,
                "TailLength": 0,
                "TailLoopPosition": 0,
            },
            "direction": 0,
            "offset": 0,
            "loop": False,
            "loopStart": 0,
            "loopEnd": 0,
            "loopCrossfadeLength": 0,
            "loopFineTune": 0,
            "loopMode": 0,
        }
    )

    assert layer.sample.name == "Kick"
    assert layer.sample.file == "Kick.wav"
    assert layer.is_empty is False
    assert layer.active is True
    assert layer.mute is False
    assert layer.pan == 0.5
    assert layer.pitch == 0.0
    assert layer.coarse_tune == 0
    assert layer.fine_tune == 0
    assert layer.root_note == 0
    assert layer.key_track_enable is False
    assert layer.velocity_start == 0
    assert layer.velocity_end == 127
    assert layer.sample_start == 0
    assert layer.sample_end == 0
    assert layer.slice_index == SLICE_INDEX_LAYER_REGION
    assert layer.slice_info.start == 244834
    assert layer.slice_info.end == 1020144
    assert layer.slice_info.loop_start == 244834
    assert layer.slice_info.loop_mode == 1
    assert layer.direction == 0
    assert layer.offset == 0
    assert layer.loop is False
    assert layer.loop_start == 0
    assert layer.loop_end == 0
    assert layer.loop_crossfade_length == 0
    assert layer.loop_fine_tune == 0
    assert layer.loop_mode == 0

def test_slice_info_from_dict():
    data = {
        "Start": 510072,
        "End": 637590,
        "LoopStart": 510072,
        "LoopMode": 1,
        "PulsePosition": 12,
        "LoopCrossfadeLength": 34,
        "LoopCrossfadeType": 2,
        "TailLength": 56,
        "TailLoopPosition": 78,
        "FutureUnknownField": "preserve-me",
    }

    slice_info = SliceInfo.from_dict(data)

    assert slice_info.start == 510072
    assert slice_info.end == 637590
    assert slice_info.loop_start == 510072
    assert slice_info.loop_mode == 1
    assert slice_info.pulse_position == 12
    assert slice_info.loop_crossfade_length == 34
    assert slice_info.loop_crossfade_type == 2
    assert slice_info.tail_length == 56
    assert slice_info.tail_loop_position == 78
    assert slice_info.raw_data == data



def test_slice_info_preserves_fractional_tail_values():
    slice_info = SliceInfo.from_dict(
        {
            "TailLength": 0.25,
            "TailLoopPosition": 0.5,
        }
    )

    assert slice_info.tail_length == 0.25
    assert slice_info.tail_loop_position == 0.5


def test_layer_preserves_unknown_128_slice_index():
    layer = Layer.from_dict(
        {
            "sliceIndex": 128,
            "sliceInfo": {
                "Start": 0,
                "End": 0,
            },
        }
    )

    assert layer.slice_index == SLICE_INDEX_UNKNOWN_128


def test_layer_preserves_numbered_slice_index():
    layer = Layer.from_dict(
        {
            "sliceIndex": 4,
            "sliceInfo": {
                "Start": 0,
                "End": 0,
            },
        }
    )

    # We preserve 0-127 exactly without assigning semantics yet.
    assert layer.slice_index == 4


def test_slice_info_is_independent_from_sample_start():
    layer = Layer.from_dict(
        {
            "sampleStart": 0,
            "sampleEnd": 0,
            "sliceIndex": 129,
            "sliceInfo": {
                "Start": 244834,
                "End": 1020144,
            },
        }
    )

    assert layer.sample_start == 0
    assert layer.sample_end == 0
    assert layer.slice_info.start == 244834
    assert layer.slice_info.end == 1020144



def test_layer_set_coarse_tune_updates_model_and_raw_data():
    data = {
        "pitch": 12.0,
        "coarseTune": 12,
    }

    layer = Layer.from_dict(data)
    layer.set_coarse_tune(7)

    assert layer.coarse_tune == 7
    assert layer.pitch == 7.0
    assert layer.raw_data["coarseTune"] == 7
    assert layer.raw_data["pitch"] == 7.0
    assert data["coarseTune"] == 7
    assert data["pitch"] == 7.0


def test_layer_set_coarse_tune_rejects_non_integer():
    layer = Layer.from_dict({})

    with pytest.raises(TypeError, match="must be an integer"):
        layer.set_coarse_tune(7.5)


def test_project_layer_edit_updates_project_raw_data():
    data = {
        "data": {
            "tracks": [
                {
                    "program": {
                        "drum": {
                            "instruments": [
                                {
                                    "layersv": [
                                        {
                                            "pitch": 12.0,
                                            "coarseTune": 12,
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }

    project = XPJProject.from_dict(data)

    layer = project.tracks[0].instruments[0].layers[0]
    layer.set_coarse_tune(7)

    raw_layer = (
        project.raw_data["data"]["tracks"][0]
        ["program"]["drum"]["instruments"][0]
        ["layersv"][0]
    )

    assert raw_layer["coarseTune"] == 7
    assert raw_layer["pitch"] == 7.0


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



def test_track_clone_layer_updates_target_and_raw_data():
    data = {
        "program": {
            "drum": {
                "instruments": [
                    {
                        "layersv": [
                            {
                                "sampleName": "Kick",
                                "sampleFile": "Kick.wav",
                                "pitch": 0.0,
                                "coarseTune": 0,
                                "sliceInfo": {
                                    "Start": 0,
                                    "End": 1000,
                                },
                            }
                        ]
                    },
                    {
                        "layersv": [
                            {
                                "sampleName": "",
                                "sampleFile": "",
                                "pitch": 0.0,
                                "coarseTune": 0,
                                "sliceInfo": {
                                    "Start": 0,
                                    "End": 0,
                                },
                            }
                        ]
                    },
                ]
            }
        }
    }

    track = Track.from_dict(data)

    cloned = track.clone_layer(0, 1)

    assert cloned.sample.name == "Kick"
    assert cloned.sample.file == "Kick.wav"
    assert cloned.slice_info.end == 1000

    raw_target = (
        data["program"]["drum"]["instruments"][1]["layersv"][0]
    )

    assert raw_target["sampleName"] == "Kick"
    assert raw_target["sampleFile"] == "Kick.wav"
    assert raw_target["sliceInfo"]["End"] == 1000


def test_track_clone_layer_uses_independent_nested_data():
    data = {
        "program": {
            "drum": {
                "instruments": [
                    {
                        "layersv": [
                            {
                                "sampleName": "Kick",
                                "sampleFile": "Kick.wav",
                                "sliceInfo": {
                                    "Start": 0,
                                    "End": 1000,
                                },
                            }
                        ]
                    },
                    {
                        "layersv": [
                            {
                                "sampleName": "",
                                "sampleFile": "",
                                "sliceInfo": {
                                    "Start": 0,
                                    "End": 0,
                                },
                            }
                        ]
                    },
                ]
            }
        }
    }

    track = Track.from_dict(data)

    cloned = track.clone_layer(0, 1)
    cloned.raw_data["sliceInfo"]["End"] = 500

    assert (
        track.instruments[0].layers[0].raw_data["sliceInfo"]["End"]
        == 1000
    )
    assert (
        track.instruments[1].layers[0].raw_data["sliceInfo"]["End"]
        == 500
    )



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
