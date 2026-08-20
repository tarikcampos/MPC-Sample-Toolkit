from pathlib import Path

import pytest

from mpctk.xpj.reader import XPJReader


PROJECT_PATH = Path("research/xpj/Tune-12.xpj")


@pytest.mark.skipif(
    not PROJECT_PATH.is_file(),
    reason="Local XPJ research file is not available",
)
def test_read_real_xpj():
    header, data = XPJReader().read(PROJECT_PATH)

    assert header.magic == "ACVS"
    assert header.version == "1.3.0.12"
    assert header.data_type == "SerialisableProjectData"
    assert header.serialization_format == "json"
    assert header.platform == "Linux"

    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], dict)

    assert data["data"]["version"] == 28
    assert data["data"]["key"] == "C Major"


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        XPJReader().read("research/xpj/does-not-exist.xpj")
