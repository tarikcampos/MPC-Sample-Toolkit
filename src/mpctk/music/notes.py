NOTE_TO_PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "FB": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
    "CB": 11,
    "B#": 0,
}


def pitch_class(note: str) -> int:
    """Return the pitch class (0-11) for a musical note name."""
    if not isinstance(note, str):
        raise TypeError("Note must be a string")

    normalized = note.strip().upper().replace("♯", "#").replace("♭", "B")

    try:
        return NOTE_TO_PITCH_CLASS[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown note: {note!r}") from exc


def root_offset(source_root: str, target_root: str) -> int:
    """Return the shortest signed semitone offset between two roots."""
    source = pitch_class(source_root)
    target = pitch_class(target_root)

    offset = (target - source) % 12

    if offset > 6:
        offset -= 12

    return offset
