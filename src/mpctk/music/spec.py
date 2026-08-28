from dataclasses import dataclass

from .layouts import (
    build_chromatic_offsets,
    build_scale_pad_offsets,
)
from .scales import (
    MAJOR_INTERVALS,
    NATURAL_MINOR_INTERVALS,
)


LAYOUT_CHROMATIC_KEYBOARD = "chromatic_keyboard"
LAYOUT_SCALE_PADS = "scale_pads"

SCALES = {
    "major": MAJOR_INTERVALS,
    "natural_minor": NATURAL_MINOR_INTERVALS,
}


@dataclass(frozen=True)
class BankSpec:
    """Musical specification for a generated pad bank."""

    source_root: str
    target_root: str
    layout: str
    pads: int
    scale: str | None = None
    start_octave: int = 0

    def build_offsets(self) -> list[int]:
        """Convert this musical specification into semitone offsets."""
        if self.pads <= 0:
            raise ValueError("Pads must be greater than zero")

        if self.layout == LAYOUT_CHROMATIC_KEYBOARD:
            if self.scale is not None:
                raise ValueError(
                    "Chromatic keyboard layout does not use a scale"
                )

            return build_chromatic_offsets(
                source_root=self.source_root,
                target_root=self.target_root,
                count=self.pads,
                start_octave=self.start_octave,
            )

        if self.layout == LAYOUT_SCALE_PADS:
            if self.scale is None:
                raise ValueError(
                    "Scale pads layout requires a scale"
                )

            try:
                intervals = SCALES[self.scale]
            except KeyError as exc:
                raise ValueError(
                    f"Unknown scale: {self.scale!r}"
                ) from exc

            return build_scale_pad_offsets(
                source_root=self.source_root,
                target_root=self.target_root,
                intervals=intervals,
                count=self.pads,
                start_octave=self.start_octave,
            )

        raise ValueError(
            f"Unknown layout: {self.layout!r}"
        )
