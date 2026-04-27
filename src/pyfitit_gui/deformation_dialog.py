"""Module holding the logic of adding deformations to the simulation input file"""

from PyQt5.QtGui import (
    QDoubleValidator,
    QIntValidator,
)
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QVBoxLayout,
)

from .datatypes import Deformation


class DeformationDialog(QDialog):
    """Main dialog window definition
    Init:
    deformations: a list of deformations in the main app
    deformation_listbox: QListBox object in the main app to display the deformation
    deformation_to_edit_idx: index of a deformation on the deformations list to edit
    """

    def __init__(
        self,
        deformations: list[Deformation],
        deformation_listbox: QListWidget,
        deformation_to_edit_idx: int = None,
    ):
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

        deformation_range_box = QHBoxLayout()

        deformation_range_box.addWidget(QLabel("Input deformation ranges"))
        self.deformation_range_left = QLineEdit()
        self.deformation_range_left.setValidator(QDoubleValidator())
        self.deformation_range_right = QLineEdit()
        self.deformation_range_right.setValidator(QDoubleValidator())

        deformation_range_box.addWidget(self.deformation_range_left)
        deformation_range_box.addWidget(self.deformation_range_right)

        main.addLayout(deformation_range_box)

        if deformation_to_edit_idx is not None:
            temp_deformation = deformations[deformation_to_edit_idx]
            self.deformation_parts.setText(temp_deformation.part)
            self.deformation_first_atom.setText(temp_deformation.atom_1)
            self.deformation_second_atom.setText(temp_deformation.atom_2)
            self.deformation_name.setText(temp_deformation.name)
            self.deformation_type.setCurrentText(temp_deformation.def_type)
            self.deformation_range_left.setText(temp_deformation.range_left)
            self.deformation_range_right.setText(temp_deformation.range_right)

        button = QDialogButtonBox.Save | QDialogButtonBox.Cancel

        button_box = QDialogButtonBox(button)
        button_box.accepted.connect(
            lambda: self.validate(
                deformations, deformation_listbox, deformation_to_edit_idx
            )
        )

        button_box.rejected.connect(self.reject)

        main.addWidget(button_box)
        main.addStretch()

        self.setLayout(main)

    def validate(
        self,
        deformations: list[Deformation],
        deformation_listbox: QListWidget,
        deformation_to_edit_idx: int = None,
    ):
        """Method that checks if input data conforms to pyfitit way of defining a deformation
        Arguments:
        deformations: a list of deformations in the main app
        deformation_listbox: QListBox object in the main app to display the deformation
        deformation_to_edit_idx: index of a deformation on the deformations list to edit
        """
        invalidate = False
        deformation_holder = [
            self.deformation_parts.text(),
            self.deformation_first_atom.text(),
            self.deformation_second_atom.text(),
            self.deformation_type.currentText(),
            self.deformation_name.text(),
            self.deformation_range_left.text(),
            self.deformation_range_right.text(),
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
            deformation_left = deformation_holder[5].replace(",", ".")
            deformation_right = deformation_holder[6].replace(",", ".")
            if float(deformation_left) > float(deformation_right):
                invalidate = True
                self.deformation_warning_message(
                    "Warning: Left-hand-side value of deformation range must be smaller than the right-hand-side value!"
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
        self,
        deformations: list[Deformation],
        deformation_listbox: QListWidget,
        deformation_to_edit_idx: int,
    ):
        """Method that loads a defined deformation and allows the user to edit it in GUI
        Arguments:
        deformations: a list of deformations in the main app
        deformation_listbox: QListBox object in the main app to display the deformation
        deformation_to_edit_idx: index of a deformation on the deformations list to edit
        """
        deformations[deformation_to_edit_idx] = Deformation(
            self.deformation_parts.text(),
            self.deformation_first_atom.text(),
            self.deformation_second_atom.text(),
            self.deformation_type.currentText(),
            self.deformation_name.text(),
            self.deformation_range_left.text(),
            self.deformation_range_right.text(),
        )

        deformation_listbox.item(deformation_to_edit_idx).setText(
            self.deformation_name.text()
        )

    def append_deformation(
        self, deformations: list[Deformation], deformation_listbox: QListWidget
    ):
        """Method to add a defined deformation to the list in the main app
        Arguments:
        deformations: a list of deformations in the main app
        deformation_listbox: QListBox object in the main app to display the deformation
        """
        deformations.append(
            Deformation(
                self.deformation_parts.text(),
                self.deformation_first_atom.text(),
                self.deformation_second_atom.text(),
                self.deformation_type.currentText(),
                self.deformation_name.text(),
                self.deformation_range_left.text(),
                self.deformation_range_right.text(),
            )
        )
        deformation_listbox.addItem(self.deformation_name.text())

    def deformation_warning_message(self, warning: str):
        """Method displaying a new window with a warning message
        Arguments:
        Warning: a warning message to display
        """
        error_dialog = QMessageBox(self)
        # pylint: disable=no-member
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setText(warning)
        error_dialog.setWindowTitle("Deformation input warning!")
        error_dialog.exec_()
