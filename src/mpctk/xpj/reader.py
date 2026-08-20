import gzip
import json
from pathlib import Path
from typing import Any

from .header import XPJHeader, parse_header


HEADER_LINE_COUNT = 5


class XPJReader:
    """Read an MPC Sample XPJ project without modifying the source file."""

    def read(self, path: str | Path) -> tuple[XPJHeader, dict[str, Any]]:
        source = Path(path)

        if not source.is_file():
            raise FileNotFoundError(source)

        with gzip.open(source, "rt", encoding="utf-8") as stream:
            lines = stream.readlines()

        if len(lines) < HEADER_LINE_COUNT:
            raise ValueError("XPJ file is too short to contain a valid header")

        header = parse_header(lines[:HEADER_LINE_COUNT])

        json_text = "".join(lines[HEADER_LINE_COUNT:])

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise ValueError("XPJ JSON payload is invalid") from exc

        if not isinstance(data, dict):
            raise ValueError("XPJ root must be a JSON object")

        return header, data
