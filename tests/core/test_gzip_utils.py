"""
Tests for MPCTK GZIP utilities.
"""

import pytest

from mpctk.core.exceptions import CompressionError
from mpctk.core.gzip_utils import (
    GZIP_MAGIC,
    compress,
    decompress,
    is_gzip,
    round_trip,
)


def test_compress_returns_gzip_data():
    data = b"MPCTK test data"

    compressed = compress(data)

    assert isinstance(compressed, bytes)
    assert compressed.startswith(GZIP_MAGIC)


def test_is_gzip_detects_gzip_data():
    data = b"MPCTK test data"

    compressed = compress(data)

    assert is_gzip(compressed) is True
    assert is_gzip(data) is False


def test_decompress_restores_original_data():
    data = b"MPCTK test data"

    compressed = compress(data)
    restored = decompress(compressed)

    assert restored == data


def test_round_trip_restores_original_data():
    data = b"MPCTK round-trip test"

    assert round_trip(data) == data


def test_round_trip_with_empty_data():
    data = b""

    assert round_trip(data) == data


def test_round_trip_with_binary_data():
    data = bytes(range(256))

    assert round_trip(data) == data


def test_invalid_gzip_raises_compression_error():
    invalid_data = b"This is not GZIP data"

    with pytest.raises(CompressionError):
        decompress(invalid_data)


def test_corrupted_gzip_raises_compression_error():
    data = b"MPCTK test data"

    compressed = compress(data)

    corrupted = compressed[:-4]

    with pytest.raises(CompressionError):
        decompress(corrupted)
