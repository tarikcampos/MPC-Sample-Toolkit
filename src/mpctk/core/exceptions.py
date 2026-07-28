"""
MPCTK - MPC Sample Toolkit

Custom exceptions used throughout the project.
"""

from __future__ import annotations


class MPCTKError(Exception):
    """
    Base exception for every MPCTK error.
    """

    pass


class XPJError(MPCTKError):
    """
    Base class for XPJ related errors.
    """

    pass


class InvalidXPJError(XPJError):
    """
    Raised when a file is not recognized as a valid XPJ project.
    """

    pass


class UnsupportedVersionError(XPJError):
    """
    Raised when the XPJ version is not yet supported.
    """

    pass


class InvalidHeaderError(XPJError):
    """
    Raised when the XPJ header cannot be parsed.
    """

    pass


class CompressionError(XPJError):
    """
    Raised when GZIP decompression or compression fails.
    """

    pass


class JSONPayloadError(XPJError):
    """
    Raised when the JSON payload is invalid.
    """

    pass


class ProjectSaveError(XPJError):
    """
    Raised when a project cannot be written back to disk.
    """

    pass
