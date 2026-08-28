import pytest

from mpctk.music import pitch_class, root_offset


@pytest.mark.parametrize(
    ("note", "expected"),
    [
        ("C", 0),
        ("C#", 1),
        ("Db", 1),
        ("D", 2),
        ("Eb", 3),
        ("E", 4),
        ("F", 5),
        ("F#", 6),
        ("Gb", 6),
        ("G", 7),
        ("Ab", 8),
        ("A", 9),
        ("Bb", 10),
        ("B", 11),
    ],
)
def test_pitch_class(note, expected):
    assert pitch_class(note) == expected


def test_pitch_class_accepts_unicode_accidentals():
    assert pitch_class("C♯") == 1
    assert pitch_class("D♭") == 1


def test_pitch_class_is_case_insensitive_and_strips_whitespace():
    assert pitch_class("  f#  ") == 6
    assert pitch_class("  gb  ") == 6


def test_pitch_class_accepts_common_enharmonic_spellings():
    assert pitch_class("Cb") == 11
    assert pitch_class("B#") == 0
    assert pitch_class("Fb") == 4
    assert pitch_class("E#") == 5


def test_pitch_class_rejects_non_string():
    with pytest.raises(TypeError, match="must be a string"):
        pitch_class(60)


def test_pitch_class_rejects_unknown_note():
    with pytest.raises(ValueError, match="Unknown note"):
        pitch_class("H")


@pytest.mark.parametrize(
    ("source", "target", "expected"),
    [
        ("C", "C", 0),
        ("C", "D", 2),
        ("C", "F#", 6),
        ("C", "G", -5),
        ("G", "C", 5),
        ("B", "C", 1),
        ("C", "B", -1),
        ("Db", "Eb", 2),
    ],
)
def test_root_offset_uses_shortest_signed_distance(
    source,
    target,
    expected,
):
    assert root_offset(source, target) == expected
