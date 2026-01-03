"""Module contatining a helper function to launch the app from command line"""

import sys

from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow


def main():
    """Helper function to launch the GUI app"""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    sys.exit(main())
