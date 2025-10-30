from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .datatypes import Deformation

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
    ):
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
