from dataclasses import dataclass


@dataclass(frozen=True)
class XPJHeader:
    magic: str
    version: str
    data_type: str
    serialization_format: str
    platform: str


EXPECTED_MAGIC = "ACVS"
EXPECTED_DATA_TYPE = "SerialisableProjectData"
EXPECTED_SERIALIZATION_FORMAT = "json"


def parse_header(lines: list[str]) -> XPJHeader:
    if len(lines) < 5:
        raise ValueError("XPJ header must contain at least 5 lines")

    header = XPJHeader(
        magic=lines[0].strip(),
        version=lines[1].strip(),
        data_type=lines[2].strip(),
        serialization_format=lines[3].strip(),
        platform=lines[4].strip(),
    )

    if header.magic != EXPECTED_MAGIC:
        raise ValueError(f"Invalid XPJ magic: {header.magic!r}")

    if header.data_type != EXPECTED_DATA_TYPE:
        raise ValueError(
            f"Unsupported XPJ data type: {header.data_type!r}"
        )

    if header.serialization_format != EXPECTED_SERIALIZATION_FORMAT:
        raise ValueError(
            "Unsupported XPJ serialization format: "
            f"{header.serialization_format!r}"
        )

    return header
