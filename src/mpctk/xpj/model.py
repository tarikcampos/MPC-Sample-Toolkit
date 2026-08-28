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


# Observed MPC Sample slice-index sentinel values.
#
# 129 has been experimentally observed when the playable region is defined
# by the Layer's own sliceInfo Start/End values.
#
# 128 is also legitimately produced by the MPC Sample, but its precise
# semantics are not yet known.
SLICE_INDEX_UNKNOWN_128 = 128
SLICE_INDEX_LAYER_REGION = 129


@dataclass
class SliceInfo:
    """Region and loop information persisted inside an XPJ layer."""

    raw_data: dict[str, Any] = field(default_factory=dict)

    start: int = 0
    end: int = 0
    loop_start: int = 0
    loop_mode: int = 0
    pulse_position: int = 0
    loop_crossfade_length: int = 0
    loop_crossfade_type: int = 0
    tail_length: float = 0.0
    tail_loop_position: float = 0.5

    @classmethod
    def from_dict(cls, data: Any) -> "SliceInfo":
        if not isinstance(data, dict):
            return cls()

        return cls(
            raw_data=data,
            start=int(data.get("Start", 0)),
            end=int(data.get("End", 0)),
            loop_start=int(data.get("LoopStart", 0)),
            loop_mode=int(data.get("LoopMode", 0)),
            pulse_position=int(data.get("PulsePosition", 0)),
            loop_crossfade_length=int(
                data.get("LoopCrossfadeLength", 0)
            ),
            loop_crossfade_type=int(
                data.get("LoopCrossfadeType", 0)
            ),
            tail_length=float(data.get("TailLength", 0.0)),
            tail_loop_position=float(data.get("TailLoopPosition", 0.5)),
        )


@dataclass
class Layer:
    """One sample layer belonging to an MPC instrument."""

    raw_data: dict[str, Any] = field(default_factory=dict)

    active: bool = False
    mute: bool = False

    sample: SampleReference = field(default_factory=SampleReference)

    volume: dict[str, Any] = field(default_factory=dict)
    pan: float = 0.5

    pitch: float = 0.0
    coarse_tune: int = 0
    fine_tune: int = 0
    root_note: int = 0
    key_track_enable: bool = False

    velocity_start: int = 0
    velocity_end: int = 127

    sample_start: int = 0
    sample_end: int = 0

    slice_index: int = SLICE_INDEX_LAYER_REGION
    slice_info: SliceInfo = field(default_factory=SliceInfo)

    direction: int = 0
    offset: int = 0

    loop: bool = False
    loop_start: int = 0
    loop_end: int = 0
    loop_crossfade_length: int = 0
    loop_fine_tune: int = 0
    loop_mode: int = 0

    @property
    def is_empty(self) -> bool:
        return self.sample.is_empty

    def set_coarse_tune(self, semitones: int) -> None:
        """Set the layer's coarse tuning in semitones."""
        if isinstance(semitones, bool) or not isinstance(semitones, int):
            raise TypeError("Coarse tune must be an integer")

        self.coarse_tune = semitones
        self.pitch = float(semitones)

        self.raw_data["coarseTune"] = semitones
        self.raw_data["pitch"] = float(semitones)

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
            active=bool(data.get("active", False)),
            mute=bool(data.get("mute", False)),
            sample=sample,
            volume=data.get("volume", {}),
            pan=float(data.get("pan", 0.5)),
            pitch=float(data.get("pitch", 0.0)),
            coarse_tune=int(data.get("coarseTune", 0)),
            fine_tune=int(data.get("fineTune", 0)),
            root_note=int(data.get("rootNote", 0)),
            key_track_enable=bool(data.get("keyTrackEnable", False)),
            velocity_start=int(data.get("velocityStart", 0)),
            velocity_end=int(data.get("velocityEnd", 127)),
            sample_start=int(data.get("sampleStart", 0)),
            sample_end=int(data.get("sampleEnd", 0)),
            slice_index=int(
                data.get("sliceIndex", SLICE_INDEX_LAYER_REGION)
            ),
            slice_info=SliceInfo.from_dict(data.get("sliceInfo")),
            direction=int(data.get("direction", 0)),
            offset=int(data.get("offset", 0)),
            loop=bool(data.get("loop", False)),
            loop_start=int(data.get("loopStart", 0)),
            loop_end=int(data.get("loopEnd", 0)),
            loop_crossfade_length=int(
                data.get("loopCrossfadeLength", 0)
            ),
            loop_fine_tune=int(data.get("loopFineTune", 0)),
            loop_mode=int(data.get("loopMode", 0)),
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
