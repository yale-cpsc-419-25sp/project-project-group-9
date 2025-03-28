from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set up file upload configurations
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(app.config['UPLOAD_FOLDER']): # CHANGED CODDE HERE 
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_or_create_id(conn, table, name_field, value):
    id_columns = {
        "Majors": "major_id",
        "Affinity_Groups": "group_id",
        "Interests": "interest_id",
        "Mentorship_Topics": "topic_id",
        "Roles": "role_id"
    }

    id_column = id_columns.get(table, f"{table[:-1].lower()}_id")

    cursor = conn.cursor()
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {name_field} = ?", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f"INSERT INTO {table} ({name_field}) VALUES (?)", (value,))
        conn.commit()
        return cursor.lastrowid

@app.route('/')
def quiz_form():
    return render_template('quiz.html')

@app.route('/submit', methods=['POST'])
def submit_quiz():
    name = request.form.get("name")
    pronoun = request.form.get("pronoun")
    residential_college = request.form.get("residential_college")
    college_year = request.form.get("college_year")
    extracurriculars = request.form.get("extracurriculars")
    work_experience = request.form.get("work_experience")
    bio = request.form.get("bio")

    majors = request.form.getlist("majors[]")
    affinity_groups = request.form.getlist("affinity_groups[]")
    interests = request.form.getlist("interests[]")
    seeking = request.form.getlist("mentorship_seeking[]")
    offering = request.form.getlist("mentorship_offering[]")
    roles = request.form.getlist("roles[]")

    # Handle headshot upload
    file = request.files.get('headshot')
    file_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    # Insert into Users table
    conn = sqlite3.connect("lux.sqlite")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Users (name, pronoun, residential_college, college_year,
                           headshot_path, extracurriculars, work_experience, bio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, pronoun, residential_college, college_year,
          file_path, extracurriculars, work_experience, bio))

    user_id = cursor.lastrowid
    # Insert into join tables
    for major in majors:
        major_id = get_or_create_id(conn, "Majors", "name", major)
        cursor.execute("INSERT INTO User_Majors (user_id, major_id) VALUES (?, ?)", (user_id, major_id))

    for group in affinity_groups:
        group_id = get_or_create_id(conn, "Affinity_Groups", "name", group)
        cursor.execute("INSERT INTO User_Affinity_Groups (user_id, group_id) VALUES (?, ?)", (user_id, group_id))

    for interest in interests:
        interest_id = get_or_create_id(conn, "Interests", "name", interest)
        cursor.execute("INSERT INTO User_Interests (user_id, interest_id) VALUES (?, ?)", (user_id, interest_id))

    for topic in seeking:
        topic_id = get_or_create_id(conn, "Mentorship_Topics", "name", topic)
        cursor.execute("INSERT INTO User_Seeking_Mentorship (user_id, topic_id) VALUES (?, ?)", (user_id, topic_id))

    for topic in offering:
        topic_id = get_or_create_id(conn, "Mentorship_Topics", "name", topic)
        cursor.execute("INSERT INTO User_Offering_Mentorship (user_id, topic_id) VALUES (?, ?)", (user_id, topic_id))

    for role in roles:
        role_id = get_or_create_id(conn, "Roles", "name", role)
        cursor.execute("INSERT INTO User_Roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))

    conn.commit()
    conn.close()

    return redirect(url_for('profile', user_id=user_id))

def fetch_user_data(user_id):
    conn = sqlite3.connect("lux.sqlite")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Basic user info
    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    # Join tables
    def fetch_related(query, user_id):
        cursor.execute(query, (user_id,))
        return [row["name"] for row in cursor.fetchall()]

    majors = fetch_related("""
        SELECT name FROM Majors
        JOIN User_Majors USING (major_id)
        WHERE user_id = ?
    """, user_id)

    affinity_groups = fetch_related("""
        SELECT name FROM Affinity_Groups
        JOIN User_Affinity_Groups USING (group_id)
        WHERE user_id = ?
    """, user_id)

    interests = fetch_related("""
        SELECT name FROM Interests
        JOIN User_Interests USING (interest_id)
        WHERE user_id = ?
    """, user_id)

    seeking = fetch_related("""
        SELECT name FROM Mentorship_Topics
        JOIN User_Seeking_Mentorship USING (topic_id)
        WHERE user_id = ?
    """, user_id)

    offering = fetch_related("""
        SELECT name FROM Mentorship_Topics
        JOIN User_Offering_Mentorship USING (topic_id)
        WHERE user_id = ?
    """, user_id)

    roles = fetch_related("""
        SELECT name FROM Roles
        JOIN User_Roles USING (role_id)
        WHERE user_id = ?
    """, user_id)

    conn.close()

    return {
        "user": user,
        "majors": majors,
        "affinity_groups": affinity_groups,
        "interests": interests,
        "seeking": seeking,
        "offering": offering,
        "roles": roles
    }

@app.route('/profile/<int:user_id>')
def profile(user_id):
    data = fetch_user_data(user_id)
    data["profile"] = data.pop("user")  # Rename key
    return render_template("profile.html", **data)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
