import pytest

from mpctk.xpj.header import XPJHeader, parse_header


def test_parse_valid_header():
    header = parse_header(
        [
            "ACVS\n",
            "1.3.0.12\n",
            "SerialisableProjectData\n",
            "json\n",
            "Linux\n",
        ]
    )

    assert header == XPJHeader(
        magic="ACVS",
        version="1.3.0.12",
        data_type="SerialisableProjectData",
        serialization_format="json",
        platform="Linux",
    )


def test_reject_invalid_magic():
    with pytest.raises(ValueError, match="Invalid XPJ magic"):
        parse_header(
            [
                "XXXX\n",
                "1.3.0.12\n",
                "SerialisableProjectData\n",
                "json\n",
                "Linux\n",
            ]
        )


def test_reject_invalid_data_type():
    with pytest.raises(ValueError, match="Unsupported XPJ data type"):
        parse_header(
            [
                "ACVS\n",
                "1.3.0.12\n",
                "SomethingElse\n",
                "json\n",
                "Linux\n",
            ]
        )


def test_reject_invalid_serialization_format():
    with pytest.raises(ValueError, match="Unsupported XPJ serialization"):
        parse_header(
            [
                "ACVS\n",
                "1.3.0.12\n",
                "SerialisableProjectData\n",
                "xml\n",
                "Linux\n",
            ]
        )
