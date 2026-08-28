from copy import deepcopy
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

# Experimentally verified MPC Sample tuning limits.
COARSE_TUNE_MIN = -24
COARSE_TUNE_MAX = 24
FINE_TUNE_MIN = -90
FINE_TUNE_MAX = 90


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

        if semitones < COARSE_TUNE_MIN or semitones > COARSE_TUNE_MAX:
            raise ValueError(
                "Coarse tune must be between "
                f"{COARSE_TUNE_MIN} and {COARSE_TUNE_MAX}"
            )

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

    def clone_layer(
        self,
        source_instrument_index: int,
        target_instrument_index: int,
        layer_index: int = 0,
    ) -> Layer:
        """Clone one layer from one instrument to another."""
        source_instrument = self.instruments[source_instrument_index]
        target_instrument = self.instruments[target_instrument_index]

        source_layer = source_instrument.layers[layer_index]

        layers_data = target_instrument.raw_data.get("layersv")
        if not isinstance(layers_data, list):
            raise ValueError("Target instrument does not contain a layersv list")

        cloned_data = deepcopy(source_layer.raw_data)
        layers_data[layer_index] = cloned_data

        cloned_layer = Layer.from_dict(cloned_data)
        target_instrument.layers[layer_index] = cloned_layer

        return cloned_layer

    def build_tuned_bank(
        self,
        source_instrument_index: int,
        start_instrument_index: int,
        semitone_offsets: list[int],
        layer_index: int = 0,
    ) -> list[Layer]:
        """Build a bank using explicit semitone offsets."""
        if not semitone_offsets:
            raise ValueError("Semitone offsets must not be empty")

        if any(
            isinstance(offset, bool) or not isinstance(offset, int)
            for offset in semitone_offsets
        ):
            raise TypeError("Semitone offsets must be integers")

        if source_instrument_index < 0 or source_instrument_index >= len(
            self.instruments
        ):
            raise IndexError("Source instrument index is out of range")

        end_instrument_index = (
            start_instrument_index + len(semitone_offsets)
        )

        if start_instrument_index < 0 or end_instrument_index > len(
            self.instruments
        ):
            raise IndexError("Target instrument range is out of range")

        generated_layers: list[Layer] = []

        for offset, target_index in zip(
            semitone_offsets,
            range(start_instrument_index, end_instrument_index),
        ):
            if target_index == source_instrument_index:
                layer = self.instruments[target_index].layers[layer_index]
            else:
                layer = self.clone_layer(
                    source_instrument_index=source_instrument_index,
                    target_instrument_index=target_index,
                    layer_index=layer_index,
                )

            layer.set_coarse_tune(offset)
            generated_layers.append(layer)

        return generated_layers

    def build_chromatic_bank(
        self,
        source_instrument_index: int,
        start_instrument_index: int,
        pad_count: int,
        start_semitone: int = 0,
        layer_index: int = 0,
    ) -> list[Layer]:
        """Build a chromatic run across consecutive instruments."""
        if pad_count <= 0:
            raise ValueError("Pad count must be greater than zero")

        semitone_offsets = list(
            range(
                start_semitone,
                start_semitone + pad_count,
            )
        )

        return self.build_tuned_bank(
            source_instrument_index=source_instrument_index,
            start_instrument_index=start_instrument_index,
            semitone_offsets=semitone_offsets,
            layer_index=layer_index,
        )

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
