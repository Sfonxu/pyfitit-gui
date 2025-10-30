import sys
import re
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .datatypes import Deformation
from pathlib import Path
from string import Template

from .main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    MW = MainWindow()
    MW.show()
    app.exec()

if __name__ == "__main__":
    sys.exit(main())

