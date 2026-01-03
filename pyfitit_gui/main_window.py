"""Module with main application window logic and functionality"""

import os
from collections.abc import Callable
from pathlib import Path
from string import Template

from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QIcon, QRegExpValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .deformation_dialog import DeformationDialog


class MainWindow(QWidget):
    """Main application class holding the layout and logic of the program"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = {}
        self.deformations = []
        self.setWindowTitle("PyFitIt GUI")
        self.main_box = QHBoxLayout()
        self.draw_left_column()
        self.draw_sperator()
        self.draw_right_column()
        self.setLayout(self.main_box)

    def draw_left_column(self):
        """Helper function to draw the left column of the UI"""
        left_column_main = QVBoxLayout()

        icon_dir_pixmapi = getattr(self.style(), "SP_DirOpenIcon")
        icon_dir = QIcon(self.style().standardIcon(icon_dir_pixmapi))

        icon_file_pixmapi = getattr(self.style(), "SP_FileIcon")
        icon_file = QIcon(self.style().standardIcon(icon_file_pixmapi))

        left_column_header_label = QLabel("Project directory setup")
        left_column_header_label.setFont(QFont("default", 11, QFont.Bold))
        left_column_main.addWidget(left_column_header_label)

        project_input_frame = QFrame()
        project_input_frame.setFrameStyle(QFrame.Panel)

        project_input_layout = QGridLayout()

        self.__add_file_input_widget(
            project_input_layout,
            "project_directory",
            self.get_project_directory,
            "<font>This directory is where all the generated files will appear.</font>",
            icon_dir,
            0,
        )

        self.__add_file_input_widget(
            project_input_layout,
            "molecule_file",
            self.get_molecule_file,
            """<font>This file should describe the
            <b>molecule to simulate</b> and will be used to generate deformated
            molecules for further calculations.</font>
            """,
            icon_file,
            1,
        )

        self.__add_file_input_widget(
            project_input_layout,
            "spectrum_file",
            self.get_spectrum_file,
            """This file should contain the <b>experimental spectrum</b>
            of the molecule of interest and be saved in a column format,
            where the first column is the energy column
            and the second column is the intensity column.
            """,
            icon_file,
            2,
        )

        self.__add_parameter_input_widget(
            project_input_layout,
            "project_name",
            "Name of the project that will be reflected in the generated filename",
            3,
            left_col_grid=True,
        )

        project_input_frame.setLayout(project_input_layout)
        left_column_main.addWidget(project_input_frame)

        left_column_fit_label = QLabel("Fit & FDMNES parameters")
        left_column_fit_label.setFont(QFont("default", 11, QFont.Bold))
        left_column_main.addWidget(left_column_fit_label)

        fit_input_layout = QGridLayout()
        fit_input_frame = QFrame()
        fit_input_frame.setFrameStyle(QFrame.Panel)

        self.widgets["project_energy_interval_left"] = QLineEdit()
        self.widgets["project_energy_interval_left"].setValidator(QDoubleValidator())
        self.widgets["project_energy_interval_left"].setToolTip(
            """<font>Starting and ending values for the energy interval used
            for calculations and FDMNES smoothing.</font>"""
        )
        self.widgets["project_energy_interval_right"] = QLineEdit()
        self.widgets["project_energy_interval_right"].setValidator(QDoubleValidator())
        self.widgets["project_energy_interval_right"].setToolTip(
            """<font>Starting and ending values for the energy interval used
            for calculations and FDMNES smoothing.</font>"""
        )
        fit_input_layout.addWidget(
            QLabel("Input project energy intervals"),
            0,
            0,
            Qt.AlignLeft | Qt.AlignCenter,
        )
        fit_input_layout.addWidget(
            self.widgets["project_energy_interval_left"],
            0,
            1,
            Qt.AlignRight | Qt.AlignCenter,
        )
        fit_input_layout.addWidget(
            self.widgets["project_energy_interval_right"],
            0,
            2,
            Qt.AlignRight | Qt.AlignCenter,
        )

        self.__add_parameter_input_widget(
            fit_input_layout,
            "FDMNES_energy_range",
            """<font>The FDMNES energy range used in calculations.
            Should be structured like 'e0 step0 e1 step1 ...'.
            For more info refer to FDMNES manual page 22.</font>
            """,
            1,
            long_input=True,
        )

        self.widgets["FDMNES_green"] = QCheckBox()
        self.widgets["FDMNES_green"].setStyleSheet(
            "QCheckBox:indicator"
            "{"
            "height: 1.5em;"
            "width: 1.5em;"
            "subcontrol-position: right;"
            "}"
        )
        self.widgets["FDMNES_green"].setToolTip(
            """<font>This approximation will make calculations significantly
            faster but also far less accurate.</font>"""
        )
        fit_input_layout.addWidget(
            QLabel("Use Green (Muffin-tin) approximation?"),
            4,
            0,
            Qt.AlignLeft | Qt.AlignCenter,
        )
        fit_input_layout.addWidget(self.widgets["FDMNES_green"], 4, 1, 1, 2)

        self.__add_parameter_input_widget(
            fit_input_layout,
            "FDMNES_radius",
            """<font>Final radius of the cluster where atoms are
            considered for calculations. The sphere is centered at the
            abosrbing atom. For more information
            refer to FDMNES manual page 17.</font>
            """,
            3,
            validator=QDoubleValidator(),
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "FDMNES_gamma_hole", "", 4, validator=QDoubleValidator()
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "FDMNES_Ecent", "", 5, validator=QDoubleValidator()
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "FDMNES_Elarg", "", 6, validator=QDoubleValidator()
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "FDMNES_Gmax", "", 7, validator=QDoubleValidator()
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "FDMNES_Efermi", "", 8, validator=QDoubleValidator()
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "FDMNES_Shift", "", 9, validator=QDoubleValidator()
        )

        self.__add_parameter_input_widget(
            fit_input_layout, "PyFitIt_norm", "", 10, validator=QDoubleValidator()
        )

        fit_input_frame.setLayout(fit_input_layout)
        left_column_main.addWidget(fit_input_frame)

        self.main_box.addLayout(left_column_main)

    def draw_right_column(self):
        """Helper function to draw the right column of the UI"""
        right_column_main = QVBoxLayout()
        right_column = QVBoxLayout()

        right_column_header_label = QLabel("Molecular deformations creator")
        right_column_header_label.setFont(QFont("default", 11, QFont.Bold))
        right_column_main.addWidget(right_column_header_label)

        molecule_deformations_frame = QFrame()
        molecule_deformations_frame.setFrameShape(QFrame.Panel)

        partition_box = QHBoxLayout()
        molecule_partition_regex = QRegExp(r"(?:(\d+.+\,+)|(\d\,))")
        molecule_partition_validator = QRegExpValidator(molecule_partition_regex)
        self.__add_parameter_input_widget(
            partition_box,
            "molecule_partition",
            "",
            validator=molecule_partition_validator,
        )
        right_column.addLayout(partition_box)

        self.deformation_list = QListWidget()
        right_column.addWidget(self.deformation_list)

        molecule_button_box = QHBoxLayout()
        self.__create_deformations_list(molecule_button_box)
        right_column.addLayout(molecule_button_box)

        molecule_deformations_frame.setLayout(right_column)

        right_column_main.addWidget(molecule_deformations_frame)

        save_project_header = QLabel("Check & Save Project")
        save_project_header.setFont(QFont("default", 11, QFont.Bold))
        right_column_main.addWidget(save_project_header)

        save_project_box = QFrame()
        save_project_box.setFrameShape(QFrame.Panel)
        save_project_layout = QHBoxLayout()

        self.__create_save_and_exit_box(save_project_layout)

        save_project_box.setLayout(save_project_layout)
        right_column_main.addWidget(save_project_box)

        right_column_main.addStretch()
        self.main_box.addLayout(right_column_main)

    def draw_sperator(self):
        """Helper function to draw a vertical separator between the columns"""
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.VLine)
        line_separator.setFrameShadow(QFrame.Plain)
        self.main_box.addWidget(line_separator)

    def deformation_dialog(self):
        """Helper callback function to start the deformation addition dialog"""
        dlg = DeformationDialog(self.deformations, self.deformation_list)
        dlg.exec()

    def edit_deformation_dialog(self):
        """Helper callback function to start the deformation edit dialog"""
        if len(self.deformation_list.selectedItems()) == 1:
            idx = self.deformation_list.row(self.deformation_list.selectedItems()[0])
            dlg = DeformationDialog(self.deformations, self.deformation_list, idx)
            dlg.exec()
        else:
            error_dialog = QMessageBox(self)
            # pylint: disable=no-member
            error_dialog.setIcon(QMessageBox.Icon.Warning)
            error_dialog.setText("Select a deformation to edit!")
            error_dialog.setWindowTitle("Deformation edit warning")
            error_dialog.exec_()

    def remove_deformations(self):
        """Callback that removes a deformation selected on the ListWidget object"""
        message_box = QMessageBox()
        message_box.setWindowTitle("Deformation deletion dialog")
        message_box.setText("Are you sure you want to delete the selected deformation?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = message_box.exec()
        if retval == QMessageBox.Yes:
            idx = self.deformation_list.selectedIndexes()
            self.deformations.pop(idx.row())
            self.deformation_list.takeItem(idx.row())

    # pylint: disable=too-many-locals
    def save_project_dialog(self, close: bool):
        """Start the save project dialog, optionally closing the program after a successful save
        Arguments:
        Close: boolean value that defines wheather to close the program (true to close)
        """
        message_box = QMessageBox()
        message_box.setWindowTitle("Save project")
        if not close:
            message_box.setText("Are you sure you want to save the current project?")
        else:
            message_box.setText(
                "Are you sure you want to save the current project and exit?"
            )
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = message_box.exec()
        if retval == QMessageBox.Yes:
            deformations = self.expand_deformations()
            green = "True" if self.widgets["FDMNES_green"].isChecked() else "False"
            project_dir = self.widgets["project_directory_label"].text()
            project_name = self.widgets["project_name_input"].text()
            if deformations:
                output_dictionary = {
                    "molecule_file": self.widgets["molecule_file_label"].text(),
                    "parts": self.widgets["molecule_partition"].text(),
                    "deformations": deformations,
                    "project_name": project_name,
                    "project_folder": project_dir,
                    "spectrum_file": self.widgets["spectrum_file_label"].text(),
                    "left_interval": self.widgets[
                        "project_energy_interval_left"
                    ].text(),
                    "right_interval": self.widgets[
                        "project_energy_interval_right"
                    ].text(),
                    "energy_range": self.widgets["FDMNES_energy_range_input"].text(),
                    "Green": green,
                    "Radius": self.widgets["FDMNES_radius_input"].text(),
                    "GH": self.widgets["smooth_GH_input"].text(),
                    "Ecent": self.widgets["smooth_Ecent_input"].text(),
                    "Elarg": self.widgets["smooth_Elarg_input"].text(),
                    "Gmax": self.widgets["smooth_Gmax_input"].text(),
                    "Efermi": self.widgets["smooth_Efermi_input"].text(),
                    "shift": self.widgets["smooth_Shift_input"].text(),
                    "norm": self.widgets["smooth_Norm_input"].text(),
                }
                invalidate = False
                for _, value in output_dictionary.items():
                    if value in (
                        "",
                        "No directory chosen!",
                        "No spectrum file chosen!",
                        "No molecule file chosen!",
                    ):
                        invalidate = True
                        self.save_and_exit_error_message(
                            "Cannot generate project as there are empty fields!"
                        )
                        break

                if float(output_dictionary["left_interval"]) > float(
                    output_dictionary["right_interval"]
                ):
                    self.save_and_exit_error_message(
                        "Start of energy interval is larger than the end!"
                    )

                if not invalidate:
                    project_template_path = (
                        Path(__file__).parent / "templates" / "project.template"
                    )
                    with project_template_path.open() as file_path:
                        template = Template(file_path.read())
                        result = template.substitute(output_dictionary)
                        # pylint: disable=bare-except
                        try:
                            with open(
                                # pylint: disable=line-too-long
                                f"{project_dir}/{project_name}.py",
                                "w+",
                                encoding="utf-8",
                            ) as output:
                                output.write(result)
                        except:
                            self.save_and_exit_error_message(
                                "Failed to save, file already exists!"
                            )
                        else:
                            save_success_msgbox = QMessageBox()
                            save_success_msgbox.setText(
                                f"Saved project successfuly as {project_name}.py"
                            )
                            save_success_msgbox.setWindowTitle("Save successful")
                            save_success_msgbox.setStandardButtons(QMessageBox.Ok)
                            save_success_msgbox.exec()
                            if close:
                                self.close()

    def quit_without_saving_dialog(self):
        """Helper callback function that calls save_project_dialog(close = False)"""
        quit_dialog = QMessageBox(self)
        quit_dialog.setWindowTitle("Quit without saving")
        quit_dialog.setText("Are you sure you want to quit without saving?")
        quit_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = quit_dialog.exec()
        if result == QMessageBox.Yes:
            self.close()

    def get_molecule_file(self):
        """Callback function that updates the path to the molecule file based on user choice"""
        path = (
            self.widgets["project_directory_label"].text()
            if os.path.isdir(self.widgets["project_directory_label"].text())
            else "."
        )
        fname = QFileDialog.getOpenFileName(
            self, "Choose a molecule file", path, "Molecule files (*.xyz)"
        )
        self.widgets["molecule_file_label"].setText(fname[0])

    def get_spectrum_file(self):
        """Callback function that updates spectrum file path based on user choice"""
        path = (
            self.widgets["project_directory_label"].text()
            if os.path.isdir(self.widgets["project_directory_label"].text())
            else "."
        )
        fname = QFileDialog.getOpenFileName(
            self, "Choose a spectrum file", path, "Any file type (*)"
        )
        self.widgets["spectrum_file_label"].setText(fname[0])

    def get_project_directory(self):
        """Callback function that updates the project directory based on user choice"""
        dirname = QFileDialog.getExistingDirectory(
            self, "Choose project directory", "."
        )
        self.widgets["project_directory_label"].setText(dirname)

    def save_and_exit_error_message(self, warning):
        """Helper function that displays an error dialog
        when saving a project enocunters an error
        """
        error_dialog = QMessageBox(self)
        # pylint: disable=no-member
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(warning)
        error_dialog.setWindowTitle("Generation error!")
        error_dialog.exec_()

    def expand_deformations(self):
        """Fucntion that translates a list of deformations into a string
        representation that would be encountered in a PyFitIt project file"""
        # pylint: disable=line-too-long
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
        self.save_and_exit_error_message(
            "No deformations defined, unable to generate project!"
        )
        return ""

    def __create_deformations_list(self, layout: QHBoxLayout):
        style = self.style()
        remove_button_pixmapi = getattr(style, "SP_DialogDiscardButton")
        remove_button_icon = QIcon(self.style().standardIcon(remove_button_pixmapi))

        add_button_pixmapi = getattr(style, "SP_DialogOkButton")
        add_button_icon = QIcon(self.style().standardIcon(add_button_pixmapi))

        edit_button_pixmapi = getattr(style, "SP_DialogResetButton")
        edit_button_icon = QIcon(self.style().standardIcon(edit_button_pixmapi))

        remove_deformation = QPushButton()
        remove_deformation.setText("Remove")
        remove_deformation.setIcon(remove_button_icon)
        remove_deformation.clicked.connect(self.remove_deformations)
        edit_deformation = QPushButton()
        edit_deformation.setText("Edit")
        edit_deformation.setIcon(edit_button_icon)
        edit_deformation.clicked.connect(self.edit_deformation_dialog)
        add_deformation = QPushButton()
        add_deformation.setText("Add")
        add_deformation.setIcon(add_button_icon)
        add_deformation.clicked.connect(self.deformation_dialog)

        layout.addWidget(remove_deformation)
        layout.addStretch()
        layout.addWidget(edit_deformation)
        layout.addStretch()
        layout.addWidget(add_deformation)

    def __create_save_and_exit_box(self, layout: QHBoxLayout):
        buttons = (
            QDialogButtonBox.Cancel | QDialogButtonBox.Save | QDialogButtonBox.Close
        )
        buttons_box = QDialogButtonBox(buttons)

        layout.addWidget(buttons_box)
        cancel_button = buttons_box.button(QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.quit_without_saving_dialog)

        save_button = buttons_box.button(QDialogButtonBox.Save)
        save_button.clicked.connect(lambda: self.save_project_dialog(False))

        close_button = buttons_box.button(QDialogButtonBox.Close)
        close_button.setText("Save and Close")
        close_button.clicked.connect(lambda: self.save_project_dialog(True))

    # pylint: disable=too-many-arguments
    def __add_file_input_widget(
        self,
        layout: QGridLayout,
        name: str,
        callback: Callable,
        tooltip: str,
        icon: QIcon,
        position: int,
    ):
        position *= 3
        input_button = QPushButton()
        input_button.setIcon(icon)
        label_text = name.replace("_", " ")
        input_button.setText(f"Open {label_text}")
        input_button.clicked.connect(callback)
        input_button.setToolTip(tooltip)

        layout.addWidget(
            QLabel(f"Choose {name}"), position, 0, Qt.AlignLeft | Qt.AlignCenter
        )
        layout.addWidget(input_button, position, 1, Qt.AlignRight | Qt.AlignCenter)

        self.widgets[f"{name}_label"] = QLabel("No directory chosen!")
        layout.addWidget(
            self.widgets[f"{name}_label"],
            position + 1,
            0,
            2,
            1,
            Qt.AlignLeft | Qt.AlignCenter,
        )

    # pylint: disable=too-many-arguments
    def __add_parameter_input_widget(
        self,
        layout: QGridLayout | QHBoxLayout,
        name: str,
        tooltip: str,
        position: int = None,
        validator: QDoubleValidator | QRegExpValidator = None,
        long_input: bool = False,
        left_col_grid: bool = False,
    ):
        self.widgets[f"{name}_input"] = QLineEdit()
        self.widgets[f"{name}_input"].setToolTip(tooltip)
        label_text = name.replace("_", " ")
        if validator is not None:
            self.widgets[f"{name}_input"].setValidator(validator)
        if position is not None:
            max_x = 2
            if left_col_grid:
                position *= 3
                max_x = 1
            else:
                position *= 2
            layout.addWidget(
                QLabel(f"Input {label_text}"),
                position,
                0,
                Qt.AlignLeft | Qt.AlignCenter,
            )
            if long_input:
                layout.addWidget(
                    self.widgets[f"{name}_input"], position, 1, 2, position
                )
            else:
                layout.addWidget(self.widgets[f"{name}_input"], position, max_x)
        else:
            layout.addWidget(QLabel(f"Input {label_text}"))
            layout.addWidget(self.widgets[f"{name}_input"])
