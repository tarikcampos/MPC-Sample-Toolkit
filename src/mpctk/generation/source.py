from mpctk.xpj import Track


def find_first_sample_instrument(
    track: Track,
    *,
    layer_index: int = 0,
) -> int:
    """Return the first instrument whose selected layer has a sample."""
    for instrument_index, instrument in enumerate(track.instruments):
        if layer_index >= len(instrument.layers):
            continue

        layer = instrument.layers[layer_index]

        if not layer.is_empty:
            return instrument_index

    raise ValueError(
        f"No sample found on layer {layer_index}"
    )
