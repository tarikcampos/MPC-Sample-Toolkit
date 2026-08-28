from collections.abc import Sequence


CHROMATIC_INTERVALS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
MAJOR_INTERVALS = (0, 2, 4, 5, 7, 9, 11)
NATURAL_MINOR_INTERVALS = (0, 2, 3, 5, 7, 8, 10)


def build_scale_offsets(
    intervals: Sequence[int],
    count: int,
    *,
    start_octave: int = 0,
) -> list[int]:
    """Expand scale intervals into semitone offsets across octaves."""
    if count <= 0:
        raise ValueError("Count must be greater than zero")

    if not intervals:
        raise ValueError("Intervals must not be empty")

    normalized = tuple(intervals)

    if any(
        isinstance(interval, bool) or not isinstance(interval, int)
        for interval in normalized
    ):
        raise TypeError("Scale intervals must be integers")

    if any(interval < 0 or interval >= 12 for interval in normalized):
        raise ValueError("Scale intervals must be between 0 and 11")

    if tuple(sorted(set(normalized))) != normalized:
        raise ValueError(
            "Scale intervals must be unique and in ascending order"
        )

    offsets: list[int] = []
    base = start_octave * 12

    for index in range(count):
        octave, degree = divmod(index, len(normalized))
        offsets.append(base + octave * 12 + normalized[degree])

    return offsets
