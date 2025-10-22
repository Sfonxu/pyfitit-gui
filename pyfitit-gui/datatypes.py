from dataclasses import dataclass

@dataclass
class Deformation:
    part: int
    atom_1: int
    atom_2: int
    def_type: str
    name: str

@dataclass        
class Project:
        molecule_file  : str
        parts          : str
        project_folder : str
        deformations   : Deformation
        project_name   : str
        spectrum_file  : str
        left_interval  : int
        right_interval : int
        energy_range   : str
        Green          : bool
        Radius         : float
        GH             : float
        Ecent          : float
        Elarg          : float
        Gmax           : float
        Efermi         : float
        shift          : float
        norm           : float

