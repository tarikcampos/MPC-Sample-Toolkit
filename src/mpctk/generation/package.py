from pathlib import Path
from shutil import copy2

from mpctk.music import BankSpec
from mpctk.xpj import XPJProject, XPJReader, XPJWriter

from .bank import build_bank_with_mpc_tuning
from .pads import pad_address_to_instrument_index
from .sample import inject_wav_sample


def project_data_directory_name(project_name: str) -> str:
    """Return the MPC ProjectData directory name for a project."""
    if not isinstance(project_name, str):
        raise TypeError("Project name must be a string")

    project_name = project_name.strip()

    if not project_name:
        raise ValueError("Project name must not be empty")

    name = Path(project_name).name

    if name != project_name:
        raise ValueError(
            "Project name must not contain directory components"
        )

    if name.lower().endswith(".xpj"):
        name = name[:-4]

    if not name:
        raise ValueError("Project name must not be empty")

    return f"{name}_[ProjectData]"


def generate_project_package(
    source_wav: str | Path,
    template_path: str | Path,
    destination_dir: str | Path,
    project_name: str,
    spec: BankSpec,
    *,
    track_index: int = 0,
    source_instrument_index: int = 0,
    start_bank: str = "A",
    start_pad: int = 1,
    layer_index: int = 0,
) -> tuple[Path, Path]:
    """Generate a complete MPC project package from a WAV and template."""
    source_wav = Path(source_wav)
    template_path = Path(template_path)
    destination_dir = Path(destination_dir)

    data_dir_name = project_data_directory_name(project_name)
    project_stem = data_dir_name.removesuffix("_[ProjectData]")

    project_path = destination_dir / f"{project_stem}.xpj"
    project_data_dir = destination_dir / data_dir_name

    if project_path.exists():
        raise FileExistsError(
            f"Project already exists: {project_path}"
        )

    if project_data_dir.exists():
        raise FileExistsError(
            f"Project data directory already exists: "
            f"{project_data_dir}"
        )

    reader = XPJReader()
    writer = XPJWriter()

    header, data = reader.read(template_path)
    project = XPJProject.from_dict(data)

    if isinstance(track_index, bool) or not isinstance(track_index, int):
        raise TypeError("Track index must be an integer")

    if track_index < 0 or track_index >= len(project.tracks):
        raise IndexError("Track index is out of range")

    track = project.tracks[track_index]

    inject_wav_sample(
        project,
        source_wav,
        track_index=track_index,
        instrument_index=source_instrument_index,
        layer_index=layer_index,
    )

    start_instrument_index = pad_address_to_instrument_index(
        start_bank,
        start_pad,
    )

    build_bank_with_mpc_tuning(
        track,
        spec,
        source_instrument_index=source_instrument_index,
        start_instrument_index=start_instrument_index,
        layer_index=layer_index,
    )

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    project_data_dir.mkdir()

    copied_wav = project_data_dir / source_wav.name
    copy2(source_wav, copied_wav)

    try:
        writer.write(
            project_path,
            header,
            project.raw_data,
        )
    except Exception:
        copied_wav.unlink(missing_ok=True)
        project_data_dir.rmdir()
        raise

    return project_path, project_data_dir
