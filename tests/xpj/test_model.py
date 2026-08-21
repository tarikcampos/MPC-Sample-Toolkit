import pytest

from mpctk.xpj.model import XPJProject


def test_create_project_from_dict():
    data = {
        "data": {
            "version": 28,
            "key": "C Major",
            "samples": ["sample-a", "sample-b"],
            "tracks": ["track-a"],
        }
    }

    project = XPJProject.from_dict(data)

    assert project.version == 28
    assert project.key == "C Major"
    assert project.samples == ["sample-a", "sample-b"]
    assert project.tracks == ["track-a"]
    assert project.raw_data is data


def test_project_requires_data_object():
    with pytest.raises(ValueError, match="must contain a 'data' object"):
        XPJProject.from_dict({})


def test_project_rejects_non_dictionary():
    with pytest.raises(TypeError, match="must be a dictionary"):
        XPJProject.from_dict([])
