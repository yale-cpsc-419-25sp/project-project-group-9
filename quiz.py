#quiz.py
import sqlite3
import os
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from match import calculate_match_scores

# Configure uploads to go into static/uploads so Flask can serve them
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_id(conn, table, name_field, value):
    id_columns = {
        "Majors": "major_id",
        "Affinity_Groups": "group_id",
        "Interests": "interest_id",
        "Mentorship_Topics": "topic_id",
        "Roles": "role_id"
    }
    id_col = id_columns.get(table, f"{table[:-1].lower()}_id")
    cur = conn.cursor()
    cur.execute(f"SELECT {id_col} FROM {table} WHERE {name_field} = ?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table} ({name_field}) VALUES (?)", (value,))
    conn.commit()
    return cur.lastrowid

def quiz_form():
    # Hard‑coded Yale data lists
    majors_list = [
        "African American Studies (B.A.)","African Studies (B.A.)","American Studies (B.A.)",
        "Anthropology (B.A.)","Applied Mathematics (B.A. or B.S.)","Applied Physics (B.S.)",
        "Archaeological Studies (B.A.)","Architecture (B.A.)","Art (B.A.)",
        "Astronomy (B.A.)","Astrophysics (B.S.)","Biomedical Engineering (B.S.)",
        "Chemical Engineering (B.S.)","Chemistry (B.A. or B.S.)","Classical Civilization (B.A.)",
        "Classics (B.A.)","Cognitive Science (B.A. or B.S.)","Comparative Literature (B.A.)",
        "Computer Science (B.A. or B.S.)","Computer Science and Economics (B.S.)",
        "Computer Science and Mathematics (B.S.)","Computer Science and Psychology (B.A.)",
        "Computing and Linguistics (B.A. or B.S.)","Computing and the Arts (B.A.)",
        "Earth and Planetary Sciences (B.A. or B.S.)","East Asian Languages and Literatures (B.A.)",
        "East Asian Studies (B.A.)","Ecology and Evolutionary Biology (B.A. or B.S.)",
        "Economics (B.A.)","Economics and Mathematics (B.A.)","Electrical Engineering (B.S.)",
        "Electrical Engineering and Computer Science (B.S.)","Engineering Sciences (Chemical) (B.S.)",
        "Engineering Sciences (Electrical) (B.A. or B.S.)","Engineering Sciences (Environmental) (B.A.)",
        "Engineering Sciences (Mechanical) (B.A. or B.S.)","English (B.A.)",
        "Environmental Engineering (B.S.)","Environmental Studies (B.A. or B.S.)",
        "Ethics, Politics, and Economics (B.A.)","Ethnicity, Race, and Migration (B.A.)",
        "Film and Media Studies (B.A.)","French (B.A.)","German Studies (B.A.)",
        "Global Affairs (B.A.)","Greek, Ancient and Modern (B.A.)","History (B.A.)",
        "History of Art (B.A.)","History of Science, Medicine, and Public Health (B.A.)",
        "Humanities (B.A.)","Italian Studies (B.A.)","Jewish Studies (B.A.)",
        "Latin American Studies (B.A.)","Linguistics (B.A.)","Mathematics (B.A. or B.S.)",
        "Mathematics and Philosophy (B.A.)","Mathematics and Physics (B.S.)",
        "Mechanical Engineering (B.S.)","Modern Middle East Studies (B.A.)",
        "Molecular Biophysics and Biochemistry (B.A. or B.S.)",
        "Molecular, Cellular, and Developmental Biology (B.A. or B.S.)",
        "Music (B.A.)","Near Eastern Languages and Civilizations (B.A.)",
        "Neuroscience (B.A. or B.S.)","Philosophy (B.A.)","Physics (B.S.)",
        "Physics and Geosciences (B.S.)","Physics and Philosophy (B.A. or B.S.)",
        "Political Science (B.A.)","Portuguese (B.A.)","Psychology (B.A. or B.S.)",
        "Religious Studies (B.A.)","Russian (B.A.)",
        "Russian, East European, and Eurasian Studies (B.A.)","Sociology (B.A.)",
        "South Asian Studies (B.A.)","Spanish (B.A.)",
        "Special Divisional Major (B.A. or B.S.)","Statistics and Data Science (B.A. or B.S.)",
        "Theater, Dance, and Performance Studies (B.A.)","Urban Studies (B.A.)",
        "Women’s, Gender, and Sexuality Studies (B.A.)"
    ]

    affinity_groups_list = [
        "International","FGLI","BIPOC","LGBTQ+","WGI in STEM","PWD"
    ]

    interests_list = [
        "Nonprofit & Community Organizing/Engagement","Finance","Consulting",
        "Public Health & Healthcare","Computer Science","Entrepreneurship",
        "Education & Academic","Law & Public Policy","Creative Arts & Design",
        "Entertainment","Media & Communications","Sports","Journalism",
        "Research","Sales & Marketing"
    ]

    seeking_list = [
        "Finding a Job","Finding Community","Extracurriculars","Networking",
        "Research","Graduate School","Coursework","Surviving at Yale"
    ]

    offering_list = seeking_list.copy()

    roles_list = ["Mentor","Mentee","Public","Private"]

    return render_template(
        'quiz.html',
        majors_list=majors_list,
        affinity_groups_list=affinity_groups_list,
        interests_list=interests_list,
        seeking_list=seeking_list,
        offering_list=offering_list,
        roles_list=roles_list
    )

def submit_quiz():
    name                = request.form.get("name")
    pronoun             = request.form.get("pronoun")
    residential_college = request.form.get("residential_college")
    college_year        = request.form.get("college_year")
    extracurriculars    = request.form.get("extracurriculars")
    work_experience     = request.form.get("work_experience")
    bio                 = request.form.get("bio")

    majors           = request.form.getlist("majors[]")
    affinity_groups  = request.form.getlist("affinity_groups[]")
    interests        = request.form.getlist("interests[]")
    seeking          = request.form.getlist("mentorship_seeking[]")
    offering         = request.form.getlist("mentorship_offering[]")
    roles            = request.form.getlist("roles[]")

    # Validate at least one of each
    errors = []
    if not majors:          errors.append("Please select at least one major.")
    if not affinity_groups: errors.append("Please select at least one affinity group.")
    if not interests:       errors.append("Please select at least one interest.")
    if not seeking:         errors.append("Please select something you’re seeking mentorship on.")
    if not offering:        errors.append("Please select something you can offer mentorship on.")
    if not roles:           errors.append("Please choose at least one role (Mentor/Mentee).")
    if errors:
        for e in errors:
            flash(e, "warning")
        return redirect(url_for('quiz_form'))

    headshot_path = None
    file = request.files.get("headshot")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dest = os.path.join(UPLOAD_FOLDER, filename)
        file.save(dest)
        # store relative to static/
        headshot_path = f"uploads/{filename}"

    conn = sqlite3.connect("lux.sqlite")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Users (
            name, pronoun, residential_college, college_year,
            headshot_path, extracurriculars, work_experience, bio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, pronoun, residential_college, college_year,
        headshot_path, extracurriculars, work_experience, bio
    ))
    user_id = cur.lastrowid

    # join tables
    for m in majors:
        mid = get_or_create_id(conn, "Majors", "name", m)
        cur.execute("INSERT INTO User_Majors (user_id, major_id) VALUES (?, ?)", (user_id, mid))
    for g in affinity_groups:
        gid = get_or_create_id(conn, "Affinity_Groups", "name", g)
        cur.execute("INSERT INTO User_Affinity_Groups (user_id, group_id) VALUES (?, ?)", (user_id, gid))
    for i in interests:
        iid = get_or_create_id(conn, "Interests", "name", i)
        cur.execute("INSERT INTO User_Interests (user_id, interest_id) VALUES (?, ?)", (user_id, iid))
    for t in seeking:
        tid = get_or_create_id(conn, "Mentorship_Topics", "name", t)
        cur.execute("INSERT INTO User_Seeking_Mentorship (user_id, topic_id) VALUES (?, ?)", (user_id, tid))
    for t in offering:
        tid = get_or_create_id(conn, "Mentorship_Topics", "name", t)
        cur.execute("INSERT INTO User_Offering_Mentorship (user_id, topic_id) VALUES (?, ?)", (user_id, tid))
    for r in roles:
        rid = get_or_create_id(conn, "Roles", "name", r)
        cur.execute("INSERT INTO User_Roles (user_id, role_id) VALUES (?, ?)", (user_id, rid))

    conn.commit()
    # compute and render matches
    matches = calculate_match_scores(conn, user_id)
    conn.close()
    return render_template("mentors.html", mentors=matches)
