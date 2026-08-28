from pathlib import Path

from mpctk.music import BankSpec
from mpctk.xpj import XPJProject, XPJReader, XPJWriter

from .bank import build_bank_from_pad_address


def generate_project_from_template(
    source_path: str | Path,
    output_path: str | Path,
    spec: BankSpec,
    *,
    track_index: int = 0,
    start_bank: str = "A",
    start_pad: int = 1,
    layer_index: int = 0,
) -> Path:
    """Generate an MPC XPJ project from an existing template."""
    reader = XPJReader()
    writer = XPJWriter()

    header, data = reader.read(source_path)
    project = XPJProject.from_dict(data)

    if isinstance(track_index, bool) or not isinstance(track_index, int):
        raise TypeError("Track index must be an integer")

    if track_index < 0 or track_index >= len(project.tracks):
        raise IndexError("Track index is out of range")

    track = project.tracks[track_index]

    build_bank_from_pad_address(
        track,
        spec,
        start_bank=start_bank,
        start_pad=start_pad,
        layer_index=layer_index,
    )

    return writer.write(
        output_path,
        header,
        project.raw_data,
    )
