import argparse
from pathlib import Path
from typing import Sequence

from mpctk.generation import (
    BANK_NAMES,
    generate_project_package,
)
from mpctk.music import (
    BankSpec,
    LAYOUT_CHROMATIC_KEYBOARD,
    LAYOUT_SCALE_PADS,
)


CLI_LAYOUTS = {
    "chromatic-keyboard": LAYOUT_CHROMATIC_KEYBOARD,
    "scale-pads": LAYOUT_SCALE_PADS,
}

CLI_SCALES = {
    "major": "major",
    "natural-minor": "natural_minor",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the MPCTK command-line parser."""
    parser = argparse.ArgumentParser(
        prog="mpctk",
        description=(
            "Create MPC Sample projects from WAV files."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    generate = subparsers.add_parser(
        "generate",
        help="Generate a complete MPC project package.",
    )

    generate.add_argument(
        "source_wav",
        type=Path,
        help="Source WAV file.",
    )

    generate.add_argument(
        "--template",
        required=True,
        type=Path,
        help="Structural XPJ template.",
    )

    generate.add_argument(
        "--source-root",
        required=True,
        help="Musical root of the source sample, e.g. C or F#.",
    )

    generate.add_argument(
        "--target-root",
        required=True,
        help="Root note for the generated bank.",
    )

    generate.add_argument(
        "--layout",
        required=True,
        choices=sorted(CLI_LAYOUTS),
        help="Pad layout.",
    )

    generate.add_argument(
        "--scale",
        choices=sorted(CLI_SCALES),
        help="Scale used by the scale-pads layout.",
    )

    generate.add_argument(
        "--pads",
        type=int,
        default=16,
        help="Number of pads to generate (default: 16).",
    )

    generate.add_argument(
        "--bank",
        choices=BANK_NAMES,
        default="A",
        help="Starting MPC bank (default: A).",
    )

    generate.add_argument(
        "--start-pad",
        type=int,
        default=1,
        help="Starting pad within the bank (default: 1).",
    )

    generate.add_argument(
        "--start-octave",
        type=int,
        default=0,
        help="Starting octave offset (default: 0).",
    )

    generate.add_argument(
        "--name",
        help=(
            "Project name. Defaults to the source WAV filename."
        ),
    )

    generate.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Destination directory.",
    )

    return parser


def _generate(args: argparse.Namespace) -> int:
    source_wav = args.source_wav

    project_name = (
        args.name
        if args.name is not None
        else source_wav.stem
    )

    scale = (
        CLI_SCALES[args.scale]
        if args.scale is not None
        else None
    )

    spec = BankSpec(
        source_root=args.source_root,
        target_root=args.target_root,
        layout=CLI_LAYOUTS[args.layout],
        pads=args.pads,
        scale=scale,
        start_octave=args.start_octave,
    )

    project_path, project_data_dir = (
        generate_project_package(
            source_wav=source_wav,
            template_path=args.template,
            destination_dir=args.output,
            project_name=project_name,
            spec=spec,
            start_bank=args.bank,
            start_pad=args.start_pad,
        )
    )

    print("MPC project generated successfully.")
    print(f"XPJ: {project_path}")
    print(f"ProjectData: {project_data_dir}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """MPCTK command-line entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "generate":
            return _generate(args)
    except (
        FileExistsError,
        FileNotFoundError,
        IndexError,
        TypeError,
        ValueError,
    ) as exc:
        parser.error(str(exc))

    parser.error(f"Unknown command: {args.command}")
    return 2
