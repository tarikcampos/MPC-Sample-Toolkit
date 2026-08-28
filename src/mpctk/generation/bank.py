from mpctk.music import BankSpec
from mpctk.xpj import Layer, Track
from mpctk.xpj.model import (
    COARSE_TUNE_MAX,
    COARSE_TUNE_MIN,
)


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
