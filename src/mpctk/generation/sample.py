from pathlib import Path
import wave

from mpctk.xpj import XPJProject


def wav_frame_count(path: str | Path) -> int:
    """Return the number of PCM frames in a WAV file."""
    source = Path(path)

    if not source.is_file():
        raise FileNotFoundError(source)

    try:
        with wave.open(str(source), "rb") as wav:
            frames = wav.getnframes()
    except wave.Error as exc:
        raise ValueError(
            f"Unsupported or invalid WAV file: {source}"
        ) from exc

    if frames <= 0:
        raise ValueError("WAV file must contain at least one frame")

    return frames


def build_sample_pool_entry(
    wav_path: str | Path,
) -> dict:
    """Build the sample-pool entry observed in MPC Sample XPJ projects."""
    source = Path(wav_path)

    return {
        "loadImpl": 0,
        "metadata": {
            "key": "G# Major",
            "rootNote": 60,
            "tempo": 0.0,
            "tune": 0.0,
        },
        "name": source.stem,
        "path": source.name,
        "version": 1,
    }


def inject_wav_sample(
    project: XPJProject,
    wav_path: str | Path,
    *,
    track_index: int = 0,
    instrument_index: int = 0,
    layer_index: int = 0,
) -> None:
    """Inject a WAV reference into an XPJ project and source layer."""
    source = Path(wav_path)
    frames = wav_frame_count(source)

    if isinstance(track_index, bool) or not isinstance(track_index, int):
        raise TypeError("Track index must be an integer")

    if track_index < 0 or track_index >= len(project.tracks):
        raise IndexError("Track index is out of range")

    track = project.tracks[track_index]

    if (
        instrument_index < 0
        or instrument_index >= len(track.instruments)
    ):
        raise IndexError("Instrument index is out of range")

    instrument = track.instruments[instrument_index]

    if layer_index < 0 or layer_index >= len(instrument.layers):
        raise IndexError("Layer index is out of range")

    project_data = project.raw_data["data"]
    track_raw = project_data["tracks"][track_index]

    sample_entry = build_sample_pool_entry(source)

    global_samples = project_data.setdefault("samples", [])
    track_samples = track_raw.setdefault("samples", [])

    if not isinstance(global_samples, list):
        raise ValueError("Project sample pool must be a list")

    if not isinstance(track_samples, list):
        raise ValueError("Track sample pool must be a list")

    global_samples[:] = [
        item
        for item in global_samples
        if not (
            isinstance(item, dict)
            and (
                item.get("name") == sample_entry["name"]
                or item.get("path") == sample_entry["path"]
            )
        )
    ]

    track_samples[:] = [
        item
        for item in track_samples
        if not (
            isinstance(item, dict)
            and (
                item.get("name") == sample_entry["name"]
                or item.get("path") == sample_entry["path"]
            )
        )
    ]

    global_samples.append(dict(sample_entry))
    track_samples.append(dict(sample_entry))

    layer = instrument.layers[layer_index]
    raw = layer.raw_data

    raw["active"] = True
    raw["sampleName"] = sample_entry["name"]
    raw["sampleFile"] = sample_entry["path"]
    raw["sampleStart"] = 0
    raw["sampleEnd"] = 0
    raw["sliceIndex"] = 129

    raw["sliceInfo"] = {
        "Start": 0,
        "End": frames - 1,
        "LoopStart": 0,
        "LoopMode": 0,
        "PulsePosition": 0,
        "LoopCrossfadeLength": 0,
        "LoopCrossfadeType": 0,
        "TailLength": 0.0,
        "TailLoopPosition": 0.5,
    }

    reparsed = type(layer).from_dict(raw)
    instrument.layers[layer_index] = reparsed
