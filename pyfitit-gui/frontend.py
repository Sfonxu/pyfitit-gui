from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from backend import ProjectGenerator, Project
from datatypes import Deformation

class SaveAndExitDialog(Toplevel):
    def __init__(self, root=None):
        super().__init__(root)
        self.title("Save and Exit")
        self.geometry("400x70")

        save_and_exit_label = ttk.Label(self, text="Are you sure you want to save and exit?").pack()
        save_and_exit_lb = ttk.Frame(self)

        save_and_exit_yes = ttk.Button(save_and_exit_lb, text="Yes", command=root.generate_project).pack(side=LEFT)
        save_and_exit_no = ttk.Button(save_and_exit_lb, text="No", command=self.destroy).pack(side=LEFT)

        save_and_exit_lb.pack()
        

class DeformationDialog(Toplevel):
    def __init__(self, root=None):
        super().__init__(root)
        self.title("Add molecular deformations")
        self.geometry("400x400")
        self.root = root

        self.part = IntVar()
        self.atom1 = IntVar()
        self.atom2 = IntVar()
        self.def_type = StringVar()
        self.name = StringVar()

        deform_label_part = ttk.Label(
            self, text="Input structure part index"
        ).pack()
        deform_input_part = ttk.Entry(self, textvariable=self.part).pack()
        
        deform_label_atom1 = ttk.Label(
            self, text="Input first atom position index"
        ).pack()
        deform_input_atom1 = ttk.Entry(self, textvariable=self.atom1).pack()

        deform_label_atom2 = ttk.Label(
            self, text="Input second atom position index "
        ).pack()
        deform_input_atom2 = ttk.Entry(self, textvariable=self.atom2).pack()

        deform_label_type = ttk.Label(self, text="Choose deformation type").pack()
        deform_input_type = ttk.Combobox(self, textvariable=self.def_type)
        deform_input_type['values'] = ['rotation', 'shift']
        deform_input_type['state'] = 'readonly'
        deform_input_type.pack()

        deform_label_name = ttk.Label(self, text="Input unique deformation name").pack()
        deform_input_name = ttk.Entry(self, textvariable=self.name).pack()

        self.deform_btn = ttk.Button(
            self,
            text="Add a deformation",
            state=DISABLED,
            command=self.save_deformation,
        )
        self.deform_btn.pack()

        delete_btn = ttk.Button(
            self, text="Remove selected deformation", command=self.remove_deformation
        )
        delete_btn.pack()
        
        self.atom1.trace_add("write", self.refresh)
        self.atom2.trace_add("write", self.refresh)
        self.def_type.trace_add("write", self.refresh)
        self.name.trace_add("write", self.refresh)
        self.part.trace_add("write", self.refresh)

    def save_deformation(self):
        temp = Deformation(
            self.atom1.get(), self.atom2.get(), self.def_type.get(), self.name.get(), self.part.get()
        )
        self.root.DEFORMATIONS.append(temp)
        self.root.deformation_list.insert("end", self.name.get())
        self.destroy()

    def remove_deformation(self):
        selection = self.root.deformation_list.curselection()
        for item in selection:
            self.root.DEFORMATIONS.pop(item)
            self.root.deformation_list.delete(item)

    def refresh(self, _, __, ___):
        if (
            self.atom1.get() != self.atom2.get()
            and self.def_type.get()
            and self.name.get()
        ):
            self.deform_btn.config(state=NORMAL)
        else:
            self.deform_btn.config(state=DISABLED)

class MainWindow(Tk):
# init main window and global variables with default values
    def __init__(self):
        super().__init__()
        self.resizable(height=False, width=False)
        self.title("PyFitIt GUI")
        self.columnconfigure(list(range(2)), weight=1)

        self.filename_molecule = StringVar()
        self.filename_spectrum = StringVar()
        self.project_directory = StringVar()
        self.DEFORMATIONS = []
        self.part = StringVar()

        self.project_name = StringVar()
        self.project_energy_intervals_left = DoubleVar()
        self.project_energy_intervals_right = DoubleVar()
        self.FDMNES_energy_range = StringVar()
        self.FDMNES_Green = BooleanVar()
        self.FDMNES_radius = DoubleVar()
        
        self.Smooth_GH = DoubleVar()
        self.Smooth_Ecent = DoubleVar()
        self.Smooth_Elarg = DoubleVar()
        self.Smooth_Gmax = DoubleVar()
        self.Smooth_Efermi = DoubleVar()
        self.Smooth_shift = DoubleVar()
        self.Smooth_norm = DoubleVar()
        
        self.Calc_sample_count = IntVar()
        self.Calc_method = StringVar()
        self.Calc_parallel = IntVar()
        self.Calc_output_folder = StringVar()
        
        
        self.mainframe = ttk.Frame(self, width=600, height=600, borderwidth=5, relief="ridge")
        self.mainframe.grid(column=0, row=0)
        self.__column_left()
        self.__column_middle()
        self.__column_right()

    def __column_left(self):
        # 1st column widgets - IO, basic params
        self.column_left = ttk.Frame(self.mainframe, borderwidth=5, relief="ridge")
        self.column_left.pack(side=LEFT, fill="both")
        # temp frame for side by side packing
        self.temp_lb = ttk.Frame(self.column_left)
        
        label_input_molecule = ttk.Label(self.column_left, text="Select path to .xyz molecule file").pack()
        self.input_molecule = ttk.Button(self.column_left, text="Click to open selection", command=self.sf_molecule)
        self.input_molecule.pack()
        
        label_input_spectrum = ttk.Label(
            self.column_left, text="Select path to experimental spectrum file"
        ).pack()
        self.input_experimental_spectrum = ttk.Button(
            self.column_left, text="Click to open selection", command=self.sf_spectrum
        )
        self.input_experimental_spectrum.pack()
        
        label_input_project_directory = ttk.Label(
            self.column_left, text="Select project working directory"
        ).pack()
        self.input_project_directory = ttk.Button(
            self.column_left, text="Click to open selection", command=self.sf_directory
        )
        self.input_project_directory.pack()
        
        label_input_project_name = ttk.Label(self.column_left, text="Input project name").pack()
        input_project_name = ttk.Entry(self.column_left, textvariable=self.project_name).pack()

        label_calc_section = ttk.Label(self.column_left, text="Calculation parameters").pack()
        
        label_project_energy_intervals = ttk.Label(self.column_left, text="Fitting energy interval").pack()
        input_project_energy_intervals_left = ttk.Entry(
            self.temp_lb, textvariable=self.project_energy_intervals_left
        ).pack(side=LEFT)
        input_project_energy_intervals_right = ttk.Entry(
            self.temp_lb, textvariable=self.project_energy_intervals_right
        ).pack(side=LEFT)

        label_FDMNES_energy_range = ttk.Label(
            self.column_left, text="FDMNES calculation energy intervals"
        ).pack()
        input_FDMNES_energy_range = ttk.Entry(self.column_left, textvariable=self.FDMNES_energy_range).pack()
        
        label_FDMNES_Green = ttk.Label(
            self.column_left, text="Use Muffin-Tin (Green functions) approximation?"
        ).pack()
        input_FDMNES_green = ttk.Checkbutton(self.column_left, variable=self.FDMNES_Green, onvalue=True).pack()

        label_FDMNES_radius = ttk.Label(self.column_left, text="Calculation radius (angstrom)").pack()
        input_FDMNES_radius = ttk.Entry(self.column_left, textvariable=self.FDMNES_radius).pack()

        label_Smooth = ttk.Label(self.column_left, text="FDMNES smoothing parameters").pack()

        label_Smooth_GH = ttk.Label(self.column_left, text="Gamma hole").pack()
        input_Smooth_GH = ttk.Entry(self.column_left, textvariable=self.Smooth_GH).pack()
        
        label_Smooth_Ecent = ttk.Label(self.column_left, text="Ecent").pack()
        input_Smooth_Ecent = ttk.Entry(self.column_left, textvariable=self.Smooth_Ecent).pack()
        
        label_Smooth_Elarg = ttk.Label(self.column_left, text="Elarg").pack()
        input_Smooth_Elarg = ttk.Entry(self.column_left, textvariable=self.Smooth_Elarg).pack()

        label_Smooth_Gmax = ttk.Label(self.column_left, text="Gamma max").pack()
        input_Smooth_Gmax = ttk.Entry(self.column_left, textvariable=self.Smooth_Gmax).pack()
        
        label_Smooth_Efermi = ttk.Label(self.column_left, text="Fermi Energy").pack()
        input_Smooth_Efermi = ttk.Entry(self.column_left, textvariable=self.Smooth_Efermi).pack()
        
        label_Smooth_Shift = ttk.Label(self.column_left, text="Shift").pack()
        input_Smooth_shift = ttk.Entry(self.column_left, textvariable=self.Smooth_shift).pack()
        
        label_Smooth_norm = ttk.Label(self.column_left, text="norm").pack()
        input_Smooth_norm = ttk.Entry(self.column_left, textvariable=self.Smooth_norm).pack()


    def __column_middle(self):
        # 2nd column widgets - molecular deformation
        self.column_middle = ttk.Frame(self.mainframe, borderwidth=5, relief="ridge")
        self.column_middle.pack(side=LEFT, fill="both")

        label_middle_column = ttk.Label(self.column_middle, text="Molecular deformations").pack()

        label_molecule_partition = ttk.Label(self.column_middle, text="Define molecule partition").pack()
        input_molecular_partition = ttk.Entry(self.column_middle, textvariable=self.part).pack()

        window_button = ttk.Button(self.column_middle, text="Add deformations")
        window_button.bind("<Button>", lambda e: DeformationDialog(self))
        window_button.pack()

        self.deformation_list = Listbox(self.column_middle)
        self.deformation_list.pack()

    def __column_right(self):
        # 3rd column widgets - sampling and ML stuff
        self.column_right = ttk.Frame(self.mainframe, borderwidth=5, relief="ridge")
        self.column_right.pack(side=LEFT, fill="both")

        label_input_sample_count = ttk.Label(self.column_right, text="Sample count").pack()
        input_sample_count = ttk.Entry(self.column_right, textvariable=self.Calc_sample_count).pack()
        
        label_input_method = ttk.Label(self.column_right, text="Sampling method").pack()
        input_method = ttk.Combobox(self.column_right, textvariable=self.Calc_method)
        input_method['values'] = ['IHS', 'Line', 'Grid', 'Random']
        input_method['state'] = 'readonly'
        input_method.set("IHS")
        input_method.pack()
        
        label_input_calc_parallel = ttk.Label(
            self.column_right, text="# of parallel calculations"
        ).pack()
        input_calc_parallel = ttk.Entry(self.column_right, textvariable=self.Calc_parallel).pack()
        
        label_input_result_folder = ttk.Label(
            self.column_right, text="Folder to save resutls"
        ).pack()
        input_result_folder = ttk.Entry(self.column_right, textvariable=self.Calc_output_folder).pack()

        save_project_and_quit_button = ttk.Button(self.column_right, text="Save & Exit")
        save_project_and_quit_button.bind("<Button>", lambda e: SaveAndExitDialog(self))
        save_project_and_quit_button.pack()

    def _select_file(self, filetypes, title):
        filename = fd.askopenfilename(title=title, initialdir=".", filetypes=filetypes)
        return filename

    def sf_molecule(self):
        filetypes = [("Molecule files", "*.xyz")]
        temp = self._select_file(filetypes, "Select molecule file")
        if temp:
            self.filename_molecule.set(temp)
            self.input_molecule.config(text=temp)

    def sf_spectrum(self):
        filetypes = [("Text files", "*.txt"), ("All files", "*")]
        temp = self._select_file(filetypes, "Select experimental spectrum file")
        if temp:
            self.filename_spectrum.set(temp)
            self.input_experimental_spectrum.config(text=temp)

    def sf_directory(self):
        temp = fd.askdirectory()
        if temp:
            self.project_directory.set(temp)
            self.input_project_directory.config(text=temp)
            

    def generate_project(self):
        project = Project(
            self.filename_molecule.get(),
            self.part.get(),
            self.project_directory.get(),
            self.DEFORMATIONS,
            self.project_name.get(),
            self.filename_spectrum.get(),
            self.project_energy_intervals_left.get(),
            self.project_energy_intervals_right.get(),
            self.FDMNES_energy_range.get(),
            self.FDMNES_Green.get(),
            self.FDMNES_radius.get(),
            self.Smooth_GH.get(),
            self.Smooth_Ecent.get(),
            self.Smooth_Elarg.get(),
            self.Smooth_Gmax.get(),
            self.Smooth_Efermi.get(),
            self.Smooth_shift.get(),
            self.Smooth_norm.get()        
        )
        ProjectGenerator(project).save()
        self.destroy()
        
