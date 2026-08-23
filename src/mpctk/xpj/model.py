from dataclasses import dataclass, field
from typing import Any


@dataclass
class SampleReference:
    """Reference to a sample used by an XPJ layer."""

    name: str | None = None
    file: str | None = None

    @property
    def is_empty(self) -> bool:
        return not self.name and not self.file


@dataclass
class Layer:
    """One sample layer belonging to an MPC instrument."""

    raw_data: dict[str, Any] = field(default_factory=dict)
    sample: SampleReference = field(default_factory=SampleReference)

    @property
    def is_empty(self) -> bool:
        return self.sample.is_empty

    @classmethod
    def from_dict(cls, data: Any) -> "Layer":
        if not isinstance(data, dict):
            return cls()

        name = data.get("sampleName")
        file = data.get("sampleFile")

        sample = SampleReference(
            name=name if isinstance(name, str) and name else None,
            file=file if isinstance(file, str) and file else None,
        )

        return cls(
            raw_data=data,
            sample=sample,
        )


@dataclass
class Instrument:
    """MPC instrument containing up to eight sample layers."""

    raw_data: dict[str, Any] = field(default_factory=dict)
    layers: list[Layer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "Instrument":
        if not isinstance(data, dict):
            return cls()

        layers_data = data.get("layersv", [])

        if not isinstance(layers_data, list):
            layers_data = []

        layers = [
            Layer.from_dict(layer)
            for layer in layers_data
        ]

        return cls(
            raw_data=data,
            layers=layers,
        )


@dataclass
class Track:
    """Structured representation of an XPJ track."""

    raw_data: dict[str, Any] = field(default_factory=dict)
    instruments: list[Instrument] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "Track":
        if not isinstance(data, dict):
            return cls()

        program = data.get("program")

        if not isinstance(program, dict):
            return cls(raw_data=data)

        drum = program.get("drum")

        if not isinstance(drum, dict):
            return cls(raw_data=data)

        instruments_data = drum.get("instruments", [])

        if not isinstance(instruments_data, list):
            instruments_data = []

        instruments = [
            Instrument.from_dict(instrument)
            for instrument in instruments_data
        ]

        return cls(
            raw_data=data,
            instruments=instruments,
        )


@dataclass
class XPJProject:
    """Structured representation of an XPJ project."""

    raw_data: dict[str, Any]
    version: int | None = None
    key: str | None = None
    samples: list[Any] = field(default_factory=list)
    tracks: list[Track] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "XPJProject":
        if not isinstance(data, dict):
            raise TypeError("XPJ project data must be a dictionary")

        project_data = data.get("data")

        if not isinstance(project_data, dict):
            raise ValueError("XPJ project must contain a 'data' object")

        tracks_data = project_data.get("tracks", [])

        if not isinstance(tracks_data, list):
            tracks_data = []

        tracks = [
            Track.from_dict(track)
            for track in tracks_data
        ]

        return cls(
            raw_data=data,
            version=project_data.get("version"),
            key=project_data.get("key"),
            samples=project_data.get("samples", []),
            tracks=tracks,
        )
