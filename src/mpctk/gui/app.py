from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from .window import MainWindow


def main(argv: Sequence[str] | None = None) -> int:
    """Launch the MPCTK graphical application."""
    application = QApplication(
        list(argv) if argv is not None else sys.argv
    )

    window = MainWindow()
    window.show()

    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
