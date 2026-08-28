BANK_NAMES = tuple("ABCDEFGH")
PADS_PER_BANK = 16


def pad_address_to_instrument_index(
    bank: str,
    pad: int,
) -> int:
    """Convert an MPC bank/pad address to a zero-based instrument index."""
    if not isinstance(bank, str):
        raise TypeError("Bank must be a string")

    normalized_bank = bank.strip().upper()

    if normalized_bank not in BANK_NAMES:
        raise ValueError(
            f"Bank must be one of: {', '.join(BANK_NAMES)}"
        )

    if isinstance(pad, bool) or not isinstance(pad, int):
        raise TypeError("Pad must be an integer")

    if pad < 1 or pad > PADS_PER_BANK:
        raise ValueError(
            f"Pad must be between 1 and {PADS_PER_BANK}"
        )

    bank_index = BANK_NAMES.index(normalized_bank)

    return bank_index * PADS_PER_BANK + (pad - 1)
