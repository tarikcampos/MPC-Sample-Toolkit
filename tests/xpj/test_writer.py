import gzip
from pathlib import Path

import pytest

from mpctk.xpj import XPJHeader, XPJReader, XPJWriter


PROJECT_PATH = Path("research/xpj/Tune-12.xpj")


def test_writer_creates_readable_xpj(tmp_path):
    header = XPJHeader(
        magic="ACVS",
        version="1.3.0.12",
        data_type="SerialisableProjectData",
        serialization_format="json",
        platform="Linux",
    )

    data = {
        "data": {
            "version": 28,
            "key": "C Major",
        }
    }

    output = tmp_path / "test.xpj"

    result = XPJWriter().write(
        output,
        header,
        data,
    )

    assert result == output
    assert output.is_file()

    read_header, read_data = XPJReader().read(output)

    assert read_header == header
    assert read_data == data


def test_writer_uses_expected_text_format(tmp_path):
    header = XPJHeader(
        magic="ACVS",
        version="1.3.0.12",
        data_type="SerialisableProjectData",
        serialization_format="json",
        platform="Linux",
    )

    data = {
        "data": {
            "version": 28,
            "key": "C Major",
        }
    }

    output = tmp_path / "format.xpj"
    XPJWriter().write(output, header, data)

    with gzip.open(output, "rb") as stream:
        raw = stream.read()

    assert raw.startswith(
        b"ACVS\n"
        b"1.3.0.12\n"
        b"SerialisableProjectData\n"
        b"json\n"
        b"Linux\n"
        b"{\n"
    )

    assert b"\r\n" not in raw
    assert b"\t" not in raw
    assert not raw.endswith(b"\n")


def test_writer_rejects_non_dictionary():
    header = XPJHeader(
        magic="ACVS",
        version="1.3.0.12",
        data_type="SerialisableProjectData",
        serialization_format="json",
        platform="Linux",
    )

    with pytest.raises(
        TypeError,
        match="must be a dictionary",
    ):
        XPJWriter().dumps(header, [])


@pytest.mark.skipif(
    not PROJECT_PATH.is_file(),
    reason="Local XPJ research file is not available",
)
def test_real_xpj_semantic_round_trip(tmp_path):
    reader = XPJReader()
    writer = XPJWriter()

    original_header, original_data = reader.read(PROJECT_PATH)

    output = tmp_path / "Tune-12-roundtrip.xpj"

    writer.write(
        output,
        original_header,
        original_data,
    )

    rewritten_header, rewritten_data = reader.read(output)

    assert rewritten_header == original_header
    assert rewritten_data == original_data
