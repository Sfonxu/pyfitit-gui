import sys
import re
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .datatypes import Deformation
from .deformation_dialog import DeformationDialog
from pathlib import Path
from string import Template

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("PyFitIt GUI")
        self.main_box = QHBoxLayout()
        self.__project_left_column()
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        self.main_box.addWidget(line_separator)

        self.__project_right_column()
        self.setLayout(self.main_box)

        self.deformations = []

    def __project_left_column(self):
        left_column_main = QVBoxLayout()
        header_font = QFont("default", 11, QFont.Bold)

        align_left = Qt.AlignLeft | Qt.AlignCenter
        align_right = Qt.AlignRight | Qt.AlignCenter
        align_center = Qt.AlignCenter | Qt.AlignCenter

        style = self.style()
        icon_dir_pixmapi = getattr(style, "SP_DirOpenIcon")
        icon_dir = QIcon(style.standardIcon(icon_dir_pixmapi))

        icon_file_pixmapi = getattr(style, "SP_FileIcon")
        icon_file = QIcon(style.standardIcon(icon_file_pixmapi))

        left_column_header_label = QLabel("Project directory setup")
        left_column_header_label.setFont(header_font)
        left_column_main.addWidget(left_column_header_label)

        project_input_frame = QFrame()
        project_input_frame.setFrameStyle(QFrame.Panel)

        project_input_layout = QGridLayout()

        project_directory_input = QPushButton()
        project_directory_input.setIcon(icon_dir)
        project_directory_input.setText("Open directory")
        project_directory_input.clicked.connect(self.get_project_directory)
        project_directory_input.setToolTip("<font>This directory is where all the generated files will appear.</font>")

        project_input_layout.addWidget(
            QLabel("Choose project directory"), 0, 0, align_left
        )
        project_input_layout.addWidget(project_directory_input, 0, 1, align_right)

        self.project_directory_label = QLabel("No directory chosen!")
        project_input_layout.addWidget(
            self.project_directory_label, 1, 0, 2, 1, align_left
        )

        self.molecule_input = QPushButton()
        self.molecule_input.setIcon(icon_file)
        self.molecule_input.setText("Open file")
        self.molecule_input.clicked.connect(self.get_molecule_file)
        self.molecule_input.setToolTip("<font>This file should describe the <b>molecule to simulate</b> and will be used to generate deformated molecules for further calculations.</font>")

        project_input_layout.addWidget(
            QLabel("Input .xyz molecule file"), 3, 0, align_left
        )
        project_input_layout.addWidget(self.molecule_input, 3, 1, align_right)

        self.molecule_file_label = QLabel("No molecule file chosen!")
        project_input_layout.addWidget(self.molecule_file_label, 4, 0, 2, 1, align_left)

        self.spectrum_input = QPushButton()
        self.spectrum_input.setIcon(icon_file)
        self.spectrum_input.setText("Open file")
        self.spectrum_input.clicked.connect(self.get_spectrum_file)
        self.spectrum_input.setToolTip("This file should contain the <b>experimental spectrum</b> of the molecule of interest and be saved in a column format, where the first column is the energy column and the second column is the intensity column.")

        project_input_layout.addWidget(
            QLabel("Input the experimental spectrum file"), 6, 0, align_left
        )
        project_input_layout.addWidget(self.spectrum_input, 6, 1, align_right)

        self.spectrum_file_label = QLabel("No spectrum file chosen!")
        project_input_layout.addWidget(self.spectrum_file_label, 7, 0, 2, 1, align_left)

        self.project_name_input = QLineEdit()
        self.project_name_input.setToolTip("A field to input a name for your project.")
        project_input_layout.addWidget(QLabel("Input project name"), 9, 0, align_left)
        project_input_layout.addWidget(self.project_name_input, 9, 1)

        project_input_frame.setLayout(project_input_layout)
        left_column_main.addWidget(project_input_frame)

        left_column_fit_label = QLabel("Fit & FDMNES parameters")
        left_column_fit_label.setFont(header_font)
        left_column_main.addWidget(left_column_fit_label)

        fit_input_layout = QGridLayout()
        fit_input_frame = QFrame()
        fit_input_frame.setFrameStyle(QFrame.Panel)

        self.project_energy_interval_left = QLineEdit()
        self.project_energy_interval_left.setValidator(QDoubleValidator())
        self.project_energy_interval_left.setToolTip("<font>Starting and ending values for the energy interval used for calculations and FDMNES smoothing.</font>")
        self.project_energy_interval_right = QLineEdit()
        self.project_energy_interval_right.setValidator(QDoubleValidator())
        self.project_energy_interval_right.setToolTip("<font>Starting and ending values for the energy interval used for calculations and FDMNES smoothing.</font>")
        fit_input_layout.addWidget(
            QLabel("Input project energy intervals"), 0, 0, align_left
        )
        fit_input_layout.addWidget(self.project_energy_interval_left, 0, 1, align_right)
        fit_input_layout.addWidget(
            self.project_energy_interval_right, 0, 2, align_right
        )

        self.FDMNES_energy_range = QLineEdit()
        self.FDMNES_energy_range.setToolTip("<font>The FDMNES energy range used in calculations. Should be structured like \'e0 step0 e1 step1 ...\'. For more info refer to FDMNES manual page 22.</font>")
        fit_input_layout.addWidget(
            QLabel("Input FDMNES energy range"), 2, 0, align_left
        )
        fit_input_layout.addWidget(self.FDMNES_energy_range, 2, 1, 1, 2)

        self.FDMNES_green = QCheckBox()
        self.FDMNES_green.setStyleSheet(
            "QCheckBox:indicator"
            "{"
            "height: 1.5em;"
            "width: 1.5em;"
            "subcontrol-position: right;"
            "}"
        )
        self.FDMNES_green.setToolTip("<font>This approximation will make calculations significantly faster but also far less accurate.</font>")
        fit_input_layout.addWidget(
            QLabel("Use Green (Muffin-tin) approximation?"), 4, 0, align_left
        )
        fit_input_layout.addWidget(self.FDMNES_green, 4, 1, 1, 2)

        self.FDMNES_radius = QLineEdit()
        self.FDMNES_radius.setValidator(QDoubleValidator())
        self.FDMNES_radius.setToolTip("<font>Final radius of the cluster where atoms are considered for calculations. The sphere is centered at the abosrbing atom. For more information refer to FDMNES manual page 17.</font>")
        fit_input_layout.addWidget(
            QLabel("Input FDMNES calculation radius"), 6, 0, align_left
        )
        fit_input_layout.addWidget(self.FDMNES_radius, 6, 2, align_right)

        self.smooth_GH = QLineEdit()
        self.smooth_GH.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("Gamma hole"), 8, 0)
        fit_input_layout.addWidget(self.smooth_GH, 8, 2)

        self.smooth_Ecent = QLineEdit()
        self.smooth_Ecent.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("Ecent"), 10, 0)
        fit_input_layout.addWidget(self.smooth_Ecent, 10, 2)

        self.smooth_Elarg = QLineEdit()
        self.smooth_Elarg.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("Elarg"), 12, 0)
        fit_input_layout.addWidget(self.smooth_Elarg, 12, 2)

        self.smooth_Gmax = QLineEdit()
        self.smooth_Gmax.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("Gmax"), 14, 0)
        fit_input_layout.addWidget(self.smooth_Gmax, 14, 2)

        self.smooth_Efermi = QLineEdit()
        self.smooth_Efermi.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("EFermi"), 16, 0)
        fit_input_layout.addWidget(self.smooth_Efermi, 16, 2)

        self.smooth_Shift = QLineEdit()
        self.smooth_Shift.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("Shift"), 18, 0)
        fit_input_layout.addWidget(self.smooth_Shift, 18, 2)

        self.smooth_Norm = QLineEdit()
        self.smooth_Norm.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(QLabel("norm"), 20, 0)
        fit_input_layout.addWidget(self.smooth_Norm, 20, 2)

        fit_input_frame.setLayout(fit_input_layout)
        left_column_main.addWidget(fit_input_frame)

        self.main_box.addLayout(left_column_main)

    def __project_right_column(self):
        right_column_main = QVBoxLayout()
        right_column = QVBoxLayout()
        header_font = QFont("default", 11, QFont.Bold)

        remove_button_pixmapi = getattr(QStyle, "SP_DialogDiscardButton")
        remove_button_icon = QIcon(self.style().standardIcon(remove_button_pixmapi))

        add_button_pixmapi = getattr(QStyle, "SP_DialogOkButton")
        add_button_icon = QIcon(self.style().standardIcon(add_button_pixmapi))

        edit_button_pixmapi = getattr(QStyle, "SP_DialogResetButton")
        edit_button_icon = QIcon(self.style().standardIcon(edit_button_pixmapi))

        right_column_header_label = QLabel("Molecular deformations creator")
        right_column_header_label.setFont(header_font)
        right_column_main.addWidget(right_column_header_label)

        molecule_deformations_frame = QFrame()
        molecule_deformations_frame.setFrameShape(QFrame.Panel)

        self.molecule_partition = QLineEdit()
        molecule_partition_regex = QRegExp(r"(?:(\d+.+\,+)|(\d\,))")
        molecule_partition_validator = QRegExpValidator(molecule_partition_regex)
        self.molecule_partition.setValidator(molecule_partition_validator)

        partition_box = QHBoxLayout()
        partition_box.addWidget(QLabel("Define molecule partition"))
        partition_box.addWidget(self.molecule_partition)
        right_column.addLayout(partition_box)

        self.deformation_list = QListWidget()
        right_column.addWidget(self.deformation_list)

        molecule_button_box = QHBoxLayout()
        self.remove_deformation = QPushButton()
        self.remove_deformation.setText("Remove")
        self.remove_deformation.setIcon(remove_button_icon)
        self.remove_deformation.clicked.connect(self.remove_deformations)
        self.edit_deformation = QPushButton()
        self.edit_deformation.setText("Edit")
        self.edit_deformation.setIcon(edit_button_icon)
        self.edit_deformation.clicked.connect(self.edit_deformation_dialog)
        self.add_deformation = QPushButton()
        self.add_deformation.setText("Add")
        self.add_deformation.setIcon(add_button_icon)
        self.add_deformation.clicked.connect(self.deformation_dialog)

        molecule_button_box.addWidget(self.remove_deformation)
        molecule_button_box.addStretch()
        molecule_button_box.addWidget(self.edit_deformation)
        molecule_button_box.addStretch()
        molecule_button_box.addWidget(self.add_deformation)

        right_column.addLayout(molecule_button_box)

        molecule_deformations_frame.setLayout(right_column)

        right_column_main.addWidget(molecule_deformations_frame)

        save_project_header = QLabel("Check & Save Project")
        save_project_header.setFont(header_font)
        right_column_main.addWidget(save_project_header)

        save_project_box = QFrame()
        save_project_box.setFrameShape(QFrame.Panel)
        save_project_layout = QHBoxLayout()

        Btns = QDialogButtonBox.Cancel | QDialogButtonBox.Save | QDialogButtonBox.Close
        BtnsBox = QDialogButtonBox(Btns)

        save_project_layout.addWidget(BtnsBox)
        cancel_button = BtnsBox.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.quit_without_saving_dialog)

        save_button = BtnsBox.button(QDialogButtonBox.Save)
        save_button.clicked.connect(lambda: self.save_project_dialog(False))
        
        close_button = BtnsBox.button(QDialogButtonBox.Close)
        close_button.setText("Save and Close")
        close_button.clicked.connect(lambda: self.save_project_dialog(True))

        save_project_box.setLayout(save_project_layout)
        right_column_main.addWidget(save_project_box)

        right_column_main.addStretch()
        self.main_box.addLayout(right_column_main)

    def deformation_dialog(self):
        dlg = DeformationDialog(self.deformations, self.deformation_list)
        dlg.exec()

    def edit_deformation_dialog(self):
        if len(self.deformation_list.selectedItems()) == 1:
            idx = self.deformation_list.row(self.deformation_list.selectedItems()[0])
            dlg = DeformationDialog(self.deformations, self.deformation_list, idx)
            dlg.exec()
        else:
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Icon.Warning)
            error_dialog.setText("Select a deformation to edit!")
            error_dialog.setWindowTitle("Deformation edit warning")
            error_dialog.exec_()

    def remove_deformations(self):
        mb = QMessageBox()
        mb.setWindowTitle("Deformation deletion dialog")
        mb.setText("Are you sure you want to delete the selected deformation?")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = mb.exec()
        if retval == QMessageBox.Yes:
            idx = self.deformation_list.selectedIndexes()
            self.deformations.pop(idx.row())
            self.deformation_list.takeItem(idx.row())

    def save_project_dialog(self, close: bool):
        mb = QMessageBox()
        mb.setWindowTitle("Save project")
        if not close:
            mb.setText("Are you sure you want to save the current project?")
        else:
            mb.setText("Are you sure you want to save the current project and exit?")
        mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = mb.exec()
        if retval == QMessageBox.Yes:
            deformations = self.expand_deformations()
            green = "True" if self.FDMNES_green.isChecked() else "False"
            if deformations:
                output_dictionary = {
                    "molecule_file": self.molecule_file_label.text(),
                    "parts": self.molecule_partition.text(),
                    "deformations": deformations,
                    "project_name": self.project_name_input.text(),
                    "project_folder": self.project_directory_label.text(),
                    "spectrum_file": self.spectrum_file_label.text(),
                    "left_interval": self.project_energy_interval_left.text(),
                    "right_interval": self.project_energy_interval_right.text(),
                    "energy_range": self.FDMNES_energy_range.text(),
                    "Green": green,
                    "Radius": self.FDMNES_radius.text(),
                    "GH": self.smooth_GH.text(),
                    "Ecent": self.smooth_Ecent.text(),
                    "Elarg": self.smooth_Elarg.text(),
                    "Gmax": self.smooth_Gmax.text(),
                    "Efermi": self.smooth_Efermi.text(),
                    "shift": self.smooth_Shift.text(),
                    "norm": self.smooth_Norm.text(),
                }
                invalidate = False
                for k, v in output_dictionary.items():
                    if (
                        v == ""
                        or v == "No directory chosen!"
                        or v == "No spectrum file chosen!"
                        or v == "No molecule file chosen!"
                    ):
                        invalidate = True
                        self.save_and_exit_error_message("Cannot generate project as there are empty fields!")
                        break

                if float(output_dictionary["left_interval"]) > float(output_dictionary["right_interval"]):
                    self.save_and_exit_error_message("Start of energy interval is larger than the end!")

                if not invalidate:
                    project_template_path = (
                        Path(__file__).parent / "templates" / "project.template"
                    )
                    with project_template_path.open() as fp:
                        template = Template(fp.read())
                        result = template.substitute(output_dictionary)
                        try:
                            with open(
                                    f"{self.project_directory_label.text()}/{self.project_name_input.text()}.py", "x"
                            ) as output:
                                output.write(result)
                        except:
                            self.save_and_exit_error_message("Failed to save, file already exists!")
                        else:
                            save_success_msgbox = QMessageBox()
                            save_success_msgbox.setText(f"Saved project successfuly as {self.project_name_input.text()}")
                            save_success_msgbox.setWindowTitle("Save successful")
                            save_success_msgbox.setStandardButtons(QMessageBox.Ok)
                            save_success_msgbox.exec()
                            if close:
                                self.close()
    

    def quit_without_saving_dialog(self):
        quit_dialog = QMessageBox(self)
        quit_dialog.setWindowTitle("Quit without saving")
        quit_dialog.setText("Are you sure you want to quit without saving?")
        quit_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = quit_dialog.exec()
        if result == QMessageBox.Yes:
            self.close()

    def get_molecule_file(self):
        path = (
            self.project_directory_label.text()
            if os.path.isdir(self.project_directory_label.text())
            else "."
        )
        fname = QFileDialog.getOpenFileName(
            self, "Choose a molecule file", path, "Molecule files (*.xyz)"
        )
        self.molecule_file_label.setText(fname[0])

    def get_spectrum_file(self):
        path = (
            self.project_directory_label.text()
            if os.path.isdir(self.project_directory_label.text())
            else "."
        )
        fname = QFileDialog.getOpenFileName(
            self, "Choose a spectrum file", path, "Any file type (*)"
        )
        self.spectrum_file_label.setText(fname[0])

    def get_project_directory(self):
        dirname = QFileDialog.getExistingDirectory(
            self, "Choose project directory", "."
        )
        self.project_directory_label.setText(dirname)

    def save_and_exit_error_message(self, warning):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(warning)
        error_dialog.setWindowTitle("Generation error!")
        error_dialog.exec_()

    def expand_deformations(self):
        deform_string_list = []
        for deformation in self.deformations:
            if deformation.def_type == "shift":
                deform_string_list.append(f'    deformation = "{deformation.name}"\n')
                deform_string_list.append(
                    f"    axis = normalize(m.atom[{deformation.atom_1}]-m.atom[{deformation.atom_2}])\n"
                )
                deform_string_list.append(
                    f"    m.part[{deformation.part}].shift(axis*params[deformation])\n\n"
                )
            elif deformation.def_type == "rotation":
                deform_string_list.append(f'    deformation = "{deformation.name}"\n')
                deform_string_list.append(
                    f"    axis = normalize(m.atom[{deformation.atom_1}]-m.atom[{deformation.atom_2}])\n"
                )
                deform_string_list.append(
                    f"    m.part[{deformation.part}].rotate(axis, m.atom[{deformation.atom_1}], params[deformation])\n\n"
                )

        if deform_string_list:
            deformation_string = "".join(deform_string_list)
            return deformation_string
        else:
            self.save_and_exit_error_message("No deformations defined, unable to generate project!")
            return ""
