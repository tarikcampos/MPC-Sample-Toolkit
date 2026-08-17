"""
GZIP utilities for MPCTK.

This module provides a small, dependency-free wrapper around Python's
standard-library ``gzip`` module.

The functions here intentionally do not make assumptions about the MPC
Sample / XPJ file format. They are generic building blocks that can be
used by the XPJ parser once the real file structure has been verified.
"""

from __future__ import annotations

import gzip

from .exceptions import CompressionError


GZIP_MAGIC = b"\x1f\x8b"
"""Magic bytes used to identify a GZIP stream."""


def is_gzip(data: bytes | bytearray | memoryview) -> bool:
    """
    Return ``True`` when *data* starts with the GZIP magic bytes.

    This is only a lightweight signature check; it does not validate the
    complete GZIP stream.
    """
    return bytes(data[:2]) == GZIP_MAGIC


def compress(
    data: bytes | bytearray | memoryview,
    *,
    compresslevel: int = 9,
    mtime: int | None = 0,
) -> bytes:
    """
    Compress *data* using GZIP.

    ``mtime=0`` is used by default so generated data is reproducible.
    Pass ``None`` to use the current time in the GZIP header.
    """
    try:
        raw = bytes(data)
        return gzip.compress(
            raw,
            compresslevel=compresslevel,
            mtime=mtime,
        )
    except (TypeError, ValueError, OSError) as exc:
        raise CompressionError(
            f"Unable to compress data with GZIP: {exc}"
        ) from exc


def decompress(
    data: bytes | bytearray | memoryview,
) -> bytes:
    """
    Decompress a complete GZIP stream.

    Raises ``CompressionError`` when the input is not a valid or complete
    GZIP stream.
    """
    try:
        compressed = bytes(data)

        if not is_gzip(compressed):
            raise CompressionError(
                "Data does not start with a valid GZIP signature."
            )

        return gzip.decompress(compressed)
    except CompressionError:
        raise
    except (EOFError, OSError, TypeError, ValueError) as exc:
        raise CompressionError(
            f"Unable to decompress GZIP data: {exc}"
        ) from exc


def round_trip(
    data: bytes | bytearray | memoryview,
    *,
    compresslevel: int = 9,
    mtime: int | None = 0,
) -> bytes:
    """
    Compress and immediately decompress *data*.

    This helper is useful for diagnostics and tests.
    """
    compressed = compress(
        data,
        compresslevel=compresslevel,
        mtime=mtime,
    )
    return decompress(compressed)
