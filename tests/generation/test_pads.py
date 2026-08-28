import pytest

from mpctk.generation import pad_address_to_instrument_index


@pytest.mark.parametrize(
    ("bank", "pad", "expected"),
    [
        ("A", 1, 0),
        ("A", 16, 15),
        ("B", 1, 16),
        ("B", 16, 31),
        ("C", 1, 32),
        ("H", 16, 127),
        (" h ", 1, 112),
    ],
)
def test_pad_address_to_instrument_index(bank, pad, expected):
    assert pad_address_to_instrument_index(bank, pad) == expected


def test_pad_address_rejects_invalid_bank():
    with pytest.raises(ValueError, match="Bank must be one of"):
        pad_address_to_instrument_index("I", 1)


def test_pad_address_rejects_non_string_bank():
    with pytest.raises(TypeError, match="Bank must be a string"):
        pad_address_to_instrument_index(1, 1)


@pytest.mark.parametrize("pad", [0, 17])
def test_pad_address_rejects_out_of_range_pad(pad):
    with pytest.raises(ValueError, match="between 1 and 16"):
        pad_address_to_instrument_index("A", pad)


def test_pad_address_rejects_non_integer_pad():
    with pytest.raises(TypeError, match="Pad must be an integer"):
        pad_address_to_instrument_index("A", 1.5)


def test_pad_address_rejects_boolean_pad():
    with pytest.raises(TypeError, match="Pad must be an integer"):
        pad_address_to_instrument_index("A", True)
