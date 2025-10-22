import sys
import re
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from datatypes import Project, Deformation
from pathlib import Path
from string import Template


class DeformationDialog(QDialog):
    def __init__(self, deformations, deformation_listbox, deformation_to_edit_idx=None):
        super().__init__()
        self.setWindowTitle("Deformation manager")

        main = QVBoxLayout()
        main.addWidget(QLabel("Input structure part index"))
        self.deformation_parts = QLineEdit()
        self.deformation_parts.setValidator(QIntValidator())
        main.addWidget(self.deformation_parts)
        main.addWidget(QLabel("Input first atom index"))
        self.deformation_first_atom = QLineEdit()
        self.deformation_first_atom.setValidator(QIntValidator())
        main.addWidget(self.deformation_first_atom)
        main.addWidget(QLabel("Input second atom index"))
        self.deformation_second_atom = QLineEdit()
        self.deformation_second_atom.setValidator(QIntValidator())
        main.addWidget(self.deformation_second_atom)
        main.addWidget(QLabel("Choose deformation type"))
        self.deformation_type = QComboBox()
        self.deformation_type.addItems(["rotation", "shift"])
        self.deformation_type.isEditable = False
        main.addWidget(self.deformation_type)
        main.addWidget(QLabel("Input a unique deformation name"))
        self.deformation_name = QLineEdit()
        main.addWidget(self.deformation_name)

        if deformation_to_edit_idx is not None:
            temp_deformation = deformations[deformation_to_edit_idx]
            self.deformation_parts.setText(temp_deformation.part)
            self.deformation_first_atom.setText(temp_deformation.atom_1)
            self.deformation_second_atom.setText(temp_deformation.atom_2)
            self.deformation_name.setText(temp_deformation.name)
            combobox_idx = self.deformation_type.setCurrentText(
                temp_deformation.def_type
            )

        QBtn = QDialogButtonBox.Save | QDialogButtonBox.Cancel

        ButtonBox = QDialogButtonBox(QBtn)
        ButtonBox.accepted.connect(
            lambda: self.validate(
                deformations, deformation_listbox, deformation_to_edit_idx
            )
        )

        ButtonBox.rejected.connect(self.reject)

        main.addWidget(ButtonBox)
        main.addStretch()

        self.setLayout(main)

    def validate(
        self, deformations, deformation_listbox, deformation_to_edit_idx=None
    ) -> bool:
        invalidate = False
        deformation_holder = [
            self.deformation_parts.text(),
            self.deformation_first_atom.text(),
            self.deformation_second_atom.text(),
            self.deformation_type.currentText(),
            self.deformation_name.text(),
        ]

        for item in deformation_holder:
            if not item:
                invalidate = True
                self.deformation_warning_message(
                    "Warning: All fields must have a value!"
                )
                break

        if not invalidate:
            if (
                not deformation_holder[1].isdigit()
                or not deformation_holder[2].isdigit()
            ):
                invalidate = True
                self.deformation_warning_message(
                    "Warning: Axis atom indices must be intigers!"
                )

        if not invalidate:
            for item in deformations:
                if item.name == self.deformation_name.text():
                    invalidate = True
                    self.deformation_warning_message(
                        "Warning: Deformation names must be unique!"
                    )

        if not invalidate:
            if deformation_to_edit_idx is not None:
                self.edit_deformation(
                    deformations, deformation_listbox, deformation_to_edit_idx
                )
            else:
                self.append_deformation(deformations, deformation_listbox)
            self.close()

    def edit_deformation(
        self, deformations, deformation_listbox, deformation_to_edit_idx
    ):
        deformations[deformation_to_edit_idx] = Deformation(
            self.deformation_parts.text(),
            self.deformation_first_atom.text(),
            self.deformation_second_atom.text(),
            self.deformation_type.currentText(),
            self.deformation_name.text(),
        )

        deformation_listbox.item(deformation_to_edit_idx).setText(
            self.deformation_name.text()
        )

    def append_deformation(self, deformations, deformation_listbox):

        deformations.append(
            Deformation(
                self.deformation_parts.text(),
                self.deformation_first_atom.text(),
                self.deformation_second_atom.text(),
                self.deformation_type.currentText(),
                self.deformation_name.text(),
            )
        )
        deformation_listbox.addItem(self.deformation_name.text())

    def deformation_warning_message(self, warning):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setText(warning)
        error_dialog.setWindowTitle("Deformation input warning!")
        error_dialog.exec_()


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
        project_directory_input.setText("Open direcotry")
        project_directory_input.clicked.connect(self.get_project_directory)

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

        project_input_layout.addWidget(
            QLabel("Input the experimental spectrum file"), 6, 0, align_left
        )
        project_input_layout.addWidget(self.spectrum_input, 6, 1, align_right)

        self.spectrum_file_label = QLabel("No spectrum file chosen!")
        project_input_layout.addWidget(self.spectrum_file_label, 7, 0, 2, 1, align_left)

        self.project_name_input = QLineEdit()
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
        self.project_energy_interval_right = QLineEdit()
        self.project_energy_interval_right.setValidator(QDoubleValidator())
        fit_input_layout.addWidget(
            QLabel("Input project energy intervals"), 0, 0, align_left
        )
        fit_input_layout.addWidget(self.project_energy_interval_left, 0, 1, align_right)
        fit_input_layout.addWidget(
            self.project_energy_interval_right, 0, 2, align_right
        )

        self.FDMNES_energy_range = QLineEdit()
        fit_input_layout.addWidget(
            QLabel("Input FDMNES energy ranges"), 2, 0, align_left
        )
        fit_input_layout.addWidget(self.FDMNES_energy_range, 2, 2)

        self.FDMNES_green = QCheckBox()
        self.FDMNES_green.setStyleSheet(
            "QCheckBox:indicator"
            "{"
            "height: 1.5em;"
            "width: 1.5em;"
            "subcontrol-position: right;"
            "}"
        )

        fit_input_layout.addWidget(
            QLabel("Use Green (Muffin-tin) approximation?"), 4, 0, align_left
        )
        fit_input_layout.addWidget(self.FDMNES_green, 4, 1, 1, 2)

        self.FDMNES_radius = QLineEdit()
        self.FDMNES_radius.setValidator(QDoubleValidator())
        self.FDMNES_radius.setFixedWidth(50)
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
        fit_input_layout.addWidget(QLabel("Gmax"), 16, 0)
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
        molecule_partition_regex = QRegExp(r"(?:\d+-\d+,)+")
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

        Btns = QDialogButtonBox.Cancel | QDialogButtonBox.Save
        BtnsBox = QDialogButtonBox(Btns)

        save_project_layout.addWidget(BtnsBox)
        BtnsBox.accepted.connect(self.save_and_exit_dialog)
        BtnsBox.rejected.connect(self.quit_without_saving_dialog)

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

    def save_and_exit_dialog(self):
        mb = QMessageBox()
        mb.setWindowTitle("Save and Exit")
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
                        print(f"MISSING VALUE {v} FOR KEY {k}")
                        invalidate = True
                        error_dialog = QMessageBox(self)
                        error_dialog.setIcon(QMessageBox.Icon.Critical)
                        error_dialog.setWindowTitle("Generation error!")
                        error_dialog.setText(
                            "Cannot generate project as there are still empty fields!"
                        )
                        error_dialog.exec_()
                        break

                if not invalidate:
                    project_template_path = (
                        Path(__file__).parent / "templates" / "project.template"
                    )
                    with project_template_path.open() as fp:
                        template = Template(fp.read())
                        result = template.substitute(output_dictionary)
                        with open(
                            f"{self.project_directory_label.text()}/project.py", "x"
                        ) as output:
                            output.write(result)

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
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Generation error!")
            error_dialog.setText("Cannot generate project: no deformations defined!")
            error_dialog.exec_()
            return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MW = MainWindow()
    MW.show()
    sys.exit(app.exec())
