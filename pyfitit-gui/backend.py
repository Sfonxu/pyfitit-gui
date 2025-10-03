from string import Template

class Project:
    def __init__(self,
                 molecule_file,
                 parts,
                 project_folder,
                 deformations,
                 project_name,
                 spectrum_file,
                 left_interval,
                 right_interval,
                 energy_range,
                 Green,
                 Radius,
                 GH,
                 Ecent,
                 Elarg,
                 Gmax,
                 Efermi,
                 shift,
                 norm
                 ):
        self.molecule_file  = molecule_file
        self.parts          = parts,
        self.project_folder = project_folder
        self.deformations   = deformations
        self.project_name   = project_name
        self.spectrum_file  = spectrum_file
        self.left_interval  = left_interval
        self.right_interval = right_interval
        self.energy_range   = energy_range
        self.Green          = Green
        self.Radius         = Radius
        self.GH             = GH
        self.Ecent          = Ecent
        self.Elarg          = Elarg
        self.Gmax           = Gmax
        self.Efermi         = Efermi
        self.shift          = shift
        self.norm           = norm

class ProjectGenerator:
    def __init__(self, project):
        self.project = project
        print(f"Passed value of part is: {self.project.parts}")
        
    def _expand_deformations(self):
        deform_string_list = []
        for deformation in self.project.deformations:
            if deformation.def_type == "shift":
                deform_string_list.append(f"    deformation = \"{deformation.name}\"\n")
                deform_string_list.append(f"    axis = normalize(m.atom[{deformation.atom_1}]-m.atom[{deformation.atom_2}])\n")
                deform_string_list.append(f"    m.part[{deformation.part}].shift(axis*params[deformation])\n\n")
            elif deformation.def_type == "rotation":
                deform_string_list.append(f"    deformation = \"{deformation.name}\"\n")
                deform_string_list.append(f"    axis = normalize(m.atom[{deformation.atom_1}]-m.atom[{deformation.atom_2}])\n")
                deform_string_list.append(f"    m.part[{deformation.part}].rotate(axis, m.atom[{deformation.atom_1}], params[deformation])\n\n")
            else:
                raise Exception("Invalid deformation type. Deformation types availible are: 'shift' and 'rotation'")

        if deform_string_list:
            deformation_string = ''.join(deform_string_list)
        else:
            raise Exception("No deformations defined!")
        return deformation_string

    def save(self):
        deformations = self._expand_deformations()
        d = {
            "molecule_file"  : self.project.molecule_file,
            "parts"          : self.project.parts[0],
            "deformations"   : deformations,
            "project_name"   : self.project.project_name,
            "project_folder" : self.project.project_folder,
            "spectrum_file"  : self.project.spectrum_file,
            "left_interval"  : self.project.left_interval,
            "right_interval" : self.project.right_interval,
            "energy_range"   : self.project.energy_range,
            "Green"          : self.project.Green,
            "Radius"         : self.project.Radius,
            "GH"             : self.project.GH,
            "Ecent"          : self.project.Ecent,
            "Elarg"          : self.project.Elarg,
            "Gmax"           : self.project.Gmax,
            "Efermi"         : self.project.Efermi,
            "shift"          : self.project.shift,
            "norm"           : self.project.norm,
        }
        with open("../templates/project.template") as template_file:
            template = Template(template_file.read())
            result = template.substitute(d)
            with open(f"{self.project.project_folder}/project.py", 'x') as output:
                output.write(result)
                    
                
