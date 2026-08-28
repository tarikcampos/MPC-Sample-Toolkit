import json
from pathlib import Path
from typing import Any

from mpctk.core.gzip_utils import compress

from .header import XPJHeader


class XPJWriter:
    """Serialize MPC Sample XPJ project data to a gzip-compressed XPJ file."""

    def dumps(
        self,
        header: XPJHeader,
        data: dict[str, Any],
    ) -> bytes:
        if not isinstance(data, dict):
            raise TypeError("XPJ project data must be a dictionary")

        header_text = "\n".join(
            (
                header.magic,
                header.version,
                header.data_type,
                header.serialization_format,
                header.platform,
            )
        )

        json_text = json.dumps(
            data,
            ensure_ascii=False,
            indent=0,
        )

        payload = f"{header_text}\n{json_text}".encode("utf-8")

        return compress(payload)

    def write(
        self,
        path: str | Path,
        header: XPJHeader,
        data: dict[str, Any],
    ) -> Path:
        destination = Path(path)
        destination.write_bytes(self.dumps(header, data))
        return destination
