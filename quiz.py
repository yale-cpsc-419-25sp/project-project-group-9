from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QHBoxLayout, QTextEdit, QFormLayout, QDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

class QuizPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mentorship Quiz")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Basic Information Form Layout
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.pronoun_input = QLineEdit()
        self.res_college_input = QLineEdit()
        self.college_year_input = QLineEdit()
        self.majors_input = QLineEdit()

        # Styling the form fields
        font = QFont("Arial", 12)
        for widget in [self.name_input, self.pronoun_input, self.res_college_input, self.college_year_input, self.majors_input]:
            widget.setFont(font)
            widget.setStyleSheet("padding: 5px; border-radius: 5px; border: 1px solid #ccc;")

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Pronoun:"), self.pronoun_input)
        form_layout.addRow(QLabel("Residential College:"), self.res_college_input)
        form_layout.addRow(QLabel("College Year:"), self.college_year_input)
        form_layout.addRow(QLabel("Major(s):"), self.majors_input)

        # Affinity Groups
        layout.addWidget(QLabel("Select Affinity Groups:"))
        self.affinity_groups = QComboBox()
        self.affinity_groups.addItems([
            "International", "FGLI", "BIPOC", "LGBTQ+", "WGI in STEM", "PWD"
        ])
        self.affinity_groups.setEditable(True)
        self.affinity_groups.setFont(font)
        self.affinity_groups.setStyleSheet("padding: 5px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.affinity_groups)

        # Other Textboxes
        self.extracurriculars_input = QTextEdit()
        self.interests_input = QTextEdit()
        self.work_exp_input = QTextEdit()
        self.mentorship_seeking_input = QTextEdit()
        self.mentorship_offering_input = QTextEdit()
        self.bio_input = QTextEdit()

        for widget in [self.extracurriculars_input, self.interests_input, self.work_exp_input, 
                       self.mentorship_seeking_input, self.mentorship_offering_input, self.bio_input]:
            widget.setFont(font)
            widget.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")

        form_layout.addRow("Extracurriculars:", self.extracurriculars_input)
        form_layout.addRow("Interests:", self.interests_input)
        form_layout.addRow("Work Experience:", self.work_exp_input)
        form_layout.addRow("Seeking Mentorship On:", self.mentorship_seeking_input)
        form_layout.addRow("Open to Offering Mentorship On:", self.mentorship_offering_input)
        form_layout.addRow("2-Sentence Bio:", self.bio_input)

        # Checkboxes Layout
        layout.addWidget(QLabel("Roles:"))
        self.mentor_check = QCheckBox("Mentor")
        self.mentee_check = QCheckBox("Mentee")
        self.public_check = QCheckBox("Public")
        self.private_check = QCheckBox("Private")

        for checkbox in [self.mentor_check, self.mentee_check, self.public_check, self.private_check]:
            checkbox.setFont(font)
            checkbox.setStyleSheet("padding: 5px;")

        checkboxes = QHBoxLayout()
        checkboxes.addWidget(self.mentor_check)
        checkboxes.addWidget(self.mentee_check)
        checkboxes.addWidget(self.public_check)
        checkboxes.addWidget(self.private_check)

        # Submit Button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_quiz)
        submit_button.setFont(QFont("Arial", 14, QFont.Bold))
        submit_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")

        # Add all elements to the layout
        layout.addLayout(form_layout)
        layout.addLayout(checkboxes)
        layout.addWidget(submit_button)

        # Add the main layout into a scrollable area
        scroll_area = QScrollArea()
        container_widget = QWidget()
        container_widget.setLayout(layout)
        scroll_area.setWidget(container_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def submit_quiz(self):
        print("Name:", self.name_input.text())
        print("Pronoun:", self.pronoun_input.text())
        print("Residential College:", self.res_college_input.text())
        print("College Year:", self.college_year_input.text())
        print("Major(s):", self.majors_input.text())
        print("Affinity Group:", self.affinity_groups.currentText())
        print("Extracurriculars:", self.extracurriculars_input.toPlainText())
        print("Interests:", self.interests_input.toPlainText())
        print("Work Experience:", self.work_exp_input.toPlainText())
        print("Seeking Mentorship On:", self.mentorship_seeking_input.toPlainText())
        print("Open to Offering Mentorship On:", self.mentorship_offering_input.toPlainText())
        print("Bio:", self.bio_input.toPlainText())
        print("Roles:", self.get_selected_roles())

    def get_selected_roles(self):
        roles = []
        if self.mentor_check.isChecked():
            roles.append("Mentor")
        if self.mentee_check.isChecked():
            roles.append("Mentee")
        if self.public_check.isChecked():
            roles.append("Public")
        if self.private_check.isChecked():
            roles.append("Private")
        return ", ".join(roles)
