"""Module holding data types used for saving and loading data into the app"""

from dataclasses import dataclass


@dataclass
class Deformation:
    """Class holding information on a deformation's type and placement in the structure"""

    part: int
    atom_1: int
    atom_2: int
    def_type: str
    name: str
