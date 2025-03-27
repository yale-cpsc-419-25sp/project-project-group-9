import sqlite3
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QHBoxLayout, QTextEdit, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Route for displaying the form
@app.route('/')
def quiz_form():
    return render_template('quiz.html')

# Route for handling form submission
@app.route('/submit', methods=['POST'])
def submit_quiz():
    name = request.form.get("name")
    pronoun = request.form.get("pronoun")
    residential_college = request.form.get("residential_college")
    college_year = request.form.get("college_year")
    majors = request.form.get("majors")
    affinity_group = request.form.get("affinity_group")
    extracurriculars = request.form.get("extracurriculars")
    interests = request.form.get("interests")
    work_experience = request.form.get("work_experience")
    seeking_mentorship = request.form.get("seeking_mentorship")
    offering_mentorship = request.form.get("offering_mentorship")
    bio = request.form.get("bio")
    roles = ', '.join(request.form.getlist("roles"))

    conn = sqlite3.connect("mentorship_quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, pronoun, residential_college, college_year, majors, 
                           affinity_group, extracurriculars, interests, work_experience, 
                           seeking_mentorship, offering_mentorship, bio, roles)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, pronoun, residential_college, college_year, majors, affinity_group,
          extracurriculars, interests, work_experience, seeking_mentorship,
          offering_mentorship, bio, roles))

    conn.commit()
    conn.close()

    return redirect(url_for('quiz_form'))

if __name__ == '__main__':
    app.run(debug=True)


class QuizPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mentorship Quiz")
        self.resize(800, 600)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.pronoun_input = QLineEdit()
        self.res_college_input = QLineEdit()
        self.college_year_input = QLineEdit()
        self.majors_input = QLineEdit()

        font = QFont("Arial", 12)
        for widget in [self.name_input, self.pronoun_input, self.res_college_input, self.college_year_input, self.majors_input]:
            widget.setFont(font)
            widget.setStyleSheet("padding: 5px; border-radius: 5px; border: 1px solid #ccc;")

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Pronoun:"), self.pronoun_input)
        form_layout.addRow(QLabel("Residential College:"), self.res_college_input)
        form_layout.addRow(QLabel("College Year:"), self.college_year_input)
        form_layout.addRow(QLabel("Major(s):"), self.majors_input)

        layout.addWidget(QLabel("Select Affinity Groups:"))
        self.affinity_groups = QComboBox()
        self.affinity_groups.addItems(["International", "FGLI", "BIPOC", "LGBTQ+", "WGI in STEM", "PWD"])
        self.affinity_groups.setEditable(True)
        self.affinity_groups.setFont(font)
        self.affinity_groups.setStyleSheet("padding: 5px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.affinity_groups)

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

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_quiz)
        submit_button.setFont(QFont("Arial", 14, QFont.Bold))
        submit_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")

        layout.addLayout(form_layout)
        layout.addLayout(checkboxes)
        layout.addWidget(submit_button)

        scroll_area = QScrollArea()
        container_widget = QWidget()
        container_widget.setLayout(layout)
        scroll_area.setWidget(container_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

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

    def submit_quiz(self):
        user_data = {
            "name": self.name_input.text(),
            "pronoun": self.pronoun_input.text(),
            "residential_college": self.res_college_input.text(),
            "college_year": self.college_year_input.text(),
            "majors": self.majors_input.text(),
            "affinity_group": self.affinity_groups.currentText(),
            "extracurriculars": self.extracurriculars_input.toPlainText(),
            "interests": self.interests_input.toPlainText(),
            "work_experience": self.work_exp_input.toPlainText(),
            "seeking_mentorship": self.mentorship_seeking_input.toPlainText(),
            "offering_mentorship": self.mentorship_offering_input.toPlainText(),
            "bio": self.bio_input.toPlainText(),
            "roles": self.get_selected_roles()
        }
        
        self.save_to_database(user_data)

    def save_to_database(self, data):
        conn = sqlite3.connect("mentorship_quiz.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                pronoun TEXT,
                residential_college TEXT,
                college_year TEXT,
                majors TEXT,
                affinity_group TEXT,
                extracurriculars TEXT,
                interests TEXT,
                work_experience TEXT,
                seeking_mentorship TEXT,
                offering_mentorship TEXT,
                bio TEXT,
                roles TEXT
            )
        """)

        cursor.execute("""
            INSERT INTO users (name, pronoun, residential_college, college_year, majors, 
                               affinity_group, extracurriculars, interests, work_experience, 
                               seeking_mentorship, offering_mentorship, bio, roles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data["name"], data["pronoun"], data["residential_college"], data["college_year"],
              data["majors"], data["affinity_group"], data["extracurriculars"], data["interests"],
              data["work_experience"], data["seeking_mentorship"], data["offering_mentorship"],
              data["bio"], data["roles"]))

        conn.commit()
        conn.close()

        print("User data saved successfully.")

    def insert_user_with_image_path(name, email, yale_netid, password_hash, image_path):
        conn = sqlite3.connect("your_database.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Users (name, email, yale_netid, password_hash, headshot_path)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, yale_netid, password_hash, image_path))

        conn.commit()
        conn.close()
