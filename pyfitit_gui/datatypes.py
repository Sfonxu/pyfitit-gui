from dataclasses import dataclass

@dataclass
class Deformation:
    part: int
    atom_1: int
    atom_2: int
    def_type: str
    name: str
