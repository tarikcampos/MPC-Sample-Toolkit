from dataclasses import dataclass, field
from typing import Any


@dataclass
class XPJProject:
    """Structured representation of an XPJ project."""

    raw_data: dict[str, Any]
    version: int | None = None
    key: str | None = None
    samples: list[Any] = field(default_factory=list)
    tracks: list[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "XPJProject":
        if not isinstance(data, dict):
            raise TypeError("XPJ project data must be a dictionary")

        project_data = data.get("data")

        if not isinstance(project_data, dict):
            raise ValueError("XPJ project must contain a 'data' object")

        return cls(
            raw_data=data,
            version=project_data.get("version"),
            key=project_data.get("key"),
            samples=project_data.get("samples", []),
            tracks=project_data.get("tracks", []),
        )
