import pytest

from mpctk.generation import find_first_sample_instrument
from mpctk.xpj import Track


def make_track(sample_instrument=None):
    instruments = []

    for index in range(4):
        sample_name = ""
        sample_file = ""

        if index == sample_instrument:
            sample_name = "Source"
            sample_file = "Source.wav"

        instruments.append(
            {
                "layersv": [
                    {
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
                ]
            }
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


def test_find_first_sample_instrument():
    track = make_track(sample_instrument=2)

    assert find_first_sample_instrument(track) == 2


def test_find_first_sample_instrument_rejects_empty_track():
    track = make_track()

    with pytest.raises(ValueError, match="No sample found"):
        find_first_sample_instrument(track)
