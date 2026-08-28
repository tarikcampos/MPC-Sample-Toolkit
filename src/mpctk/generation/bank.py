from mpctk.music import BankSpec
from mpctk.xpj import Layer, Track
from mpctk.xpj.model import (
    COARSE_TUNE_MAX,
    COARSE_TUNE_MIN,
)

from .pads import pad_address_to_instrument_index
from .source import find_first_sample_instrument


def build_bank_with_mpc_tuning(
    track: Track,
    spec: BankSpec,
    *,
    source_instrument_index: int = 0,
    start_instrument_index: int = 0,
    layer_index: int = 0,
) -> list[Layer]:
    """Apply a musical bank specification using MPC real-time tuning."""
    offsets = spec.build_offsets()

    minimum = min(offsets)
    maximum = max(offsets)

    if minimum < COARSE_TUNE_MIN or maximum > COARSE_TUNE_MAX:
        raise ValueError(
            "Bank exceeds MPC coarse-tune range "
            f"({COARSE_TUNE_MIN} to {COARSE_TUNE_MAX}): "
            f"requested {minimum} to {maximum}"
        )

    return track.build_tuned_bank(
        source_instrument_index=source_instrument_index,
        start_instrument_index=start_instrument_index,
        semitone_offsets=offsets,
        layer_index=layer_index,
    )


def build_bank_from_pad_address(
    track: Track,
    spec: BankSpec,
    *,
    start_bank: str = "A",
    start_pad: int = 1,
    layer_index: int = 0,
) -> list[Layer]:
    """Build a bank using MPC bank/pad addressing and automatic source discovery."""
    source_instrument_index = find_first_sample_instrument(
        track,
        layer_index=layer_index,
    )

    start_instrument_index = pad_address_to_instrument_index(
        start_bank,
        start_pad,
    )

    return build_bank_with_mpc_tuning(
        track,
        spec,
        source_instrument_index=source_instrument_index,
        start_instrument_index=start_instrument_index,
        layer_index=layer_index,
    )
