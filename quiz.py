import bcrypt
import sqlite3
import os
import random
import string
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

from match import calculate_match_scores  # you already have this

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_id(conn, table, name_field, value):
    id_cols = {
        "Majors": "major_id",
        "Affinity_Groups": "group_id",
        "Interests": "interest_id",
        "Mentorship_Topics": "topic_id",
        "Roles": "role_id"
    }
    col = id_cols[table]
    cur = conn.cursor()
    cur.execute(f"SELECT {col} FROM {table} WHERE {name_field}=?", (value,))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute(f"INSERT INTO {table} ({name_field}) VALUES(?)", (value,))
    conn.commit()
    return cur.lastrowid

def quiz_form(user_id=None):
    pronouns = ["she/her","he/him","they/them","she/they","they/she","he/they","ze/zir"]
    residences = [
        "Benjamin Franklin College","Berkeley College","Branford College",
        "Davenport College","Ezra Stiles College","Grace Hopper College",
        "Jonathan Edwards College","Morse College","Pauli Murray College",
        "Pierson College","Saybrook College","Silliman College",
        "Timothy Dwight College","Trumbull College"
    ]
    years = ["2025","2026","2027","2028"]
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
        "Physics and Geosciences (B.S.)","Political Science (B.A.)","Portuguese (B.A.)",
        "Psychology (B.A. or B.S.)","Religious Studies (B.A.)","Russian (B.A.)",
        "Russian, East European, and Eurasian Studies (B.A.)","Sociology (B.A.)",
        "South Asian Studies (B.A.)","Spanish (B.A.)",
        "Special Divisional Major (B.A. or B.S.)","Statistics and Data Science (B.A. or B.S.)",
        "Theater, Dance, and Performance Studies (B.A.)","Urban Studies (B.A.)",
        "Women’s, Gender, and Sexuality Studies (B.A.)"
    ]
    affinity_list = ["International","FGLI","BIPOC","LGBTQ+","WGI in STEM","PWD"]
    interests_list = [
        "Nonprofit & Community Organizing/Engagement","Finance","Consulting",
        "Public Health & Healthcare","Computer Science","Entrepreneurship",
        "Education & Academic","Law & Public Policy","Creative Arts & Design",
        "Entertainment","Media & Communications","Sports","Journalism",
        "Research","Sales & Marketing"
    ]
    seeking_list = [
        "Finding a Job","Finding Community","Extracurriculars",
        "Networking","Research","Graduate School","Coursework","Surviving at Yale"
    ]
    offering_list = seeking_list.copy()
    roles_list = ["Mentor","Mentee"]

    # defaults
    name = pronoun = res_college = college_year = ""
    headshot = None
    extracurriculars = work_experience = bio = ""
    sel_maj = sel_aff = sel_int = sel_seek = sel_off = sel_roles = set()

    if user_id:
        conn = sqlite3.connect("lux.sqlite"); conn.row_factory = sqlite3.Row
        cur  = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE user_id=?", (user_id,))
        u = cur.fetchone(); conn.close()
        if u:
            name            = u["name"]
            pronoun         = u["pronoun"]
            res_college     = u["residential_college"]
            college_year    = u["college_year"]
            headshot        = u["headshot_path"]
            extracurriculars= u["extracurriculars"]
            work_experience = u["work_experience"]
            bio             = u["bio"]
            def fetch(table, join, fk):
                c = sqlite3.connect("lux.sqlite").cursor()
                c.execute(f"""
                  SELECT {table}.name
                  FROM {table}
                  JOIN {join} ON {table}.{fk}={join}.{fk}
                  WHERE {join}.user_id=?
                """, (user_id,))
                vals = {r[0] for r in c.fetchall()}
                c.connection.close()
                return vals
            sel_maj   = fetch("Majors",            "User_Majors",             "major_id")
            sel_aff   = fetch("Affinity_Groups",   "User_Affinity_Groups",    "group_id")
            sel_int   = fetch("Interests",         "User_Interests",          "interest_id")
            sel_seek  = fetch("Mentorship_Topics", "User_Seeking_Mentorship", "topic_id")
            sel_off   = fetch("Mentorship_Topics", "User_Offering_Mentorship","topic_id")
            sel_roles = fetch("Roles",             "User_Roles",              "role_id")

    return render_template(
      "quiz.html",
      edit_mode=bool(user_id),
      user_id=user_id,
      pronouns=pronouns,
      residences=residences,
      years=years,
      majors_list=majors_list,
      affinity_list=affinity_list,
      interests_list=interests_list,
      seeking_list=seeking_list,
      offering_list=offering_list,
      roles_list=roles_list,
      name=name,
      pronoun=pronoun,
      res_college=res_college,
      college_year=college_year,
      headshot=headshot,
      extracurriculars=extracurriculars,
      work_experience=work_experience,
      bio=bio,
      sel_maj=sel_maj,
      sel_aff=sel_aff,
      sel_int=sel_int,
      sel_seek=sel_seek,
      sel_off=sel_off,
      sel_roles=sel_roles
    )

def submit_quiz():
    name                = request.form["name"]
    pronoun             = request.form["pronoun"]
    res_college         = request.form["residential_college"]
    college_year        = request.form["college_year"]
    extracurriculars    = request.form["extracurriculars"]
    work_experience     = request.form["work_experience"]
    bio                 = request.form["bio"]
    password            = request.form["password"]

    majors           = request.form.getlist("majors[]")
    affinity_groups  = request.form.getlist("affinity_groups[]")
    interests        = request.form.getlist("interests[]")
    seeking          = request.form.getlist("mentorship_seeking[]")
    offering         = request.form.getlist("mentorship_offering[]")
    roles            = request.form.getlist("roles[]")

    errors = []
    if not majors:   errors.append("Select at least one major.")
    if not interests:errors.append("Select at least one interest.")
    if not seeking:  errors.append("Select something you’re seeking.")
    if not offering: errors.append("Select something you’re offering.")
    if not roles:    errors.append("Select at least one role.")
    if errors:
        session['form_errors'] = errors
        return redirect(url_for('quiz_page'))

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    headshot_path = None
    file = request.files.get("headshot")
    if file and allowed_file(file.filename):
        fn = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, fn))
        headshot_path = f"uploads/{fn}"

    conn = sqlite3.connect("lux.sqlite")
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO Users
        (name, pronoun, residential_college, college_year,
         headshot_path, extracurriculars, work_experience, bio, hashed_password)
      VALUES (?,?,?,?,?,?,?,?,?)
    """, (
      name, pronoun, res_college, college_year,
      headshot_path, extracurriculars, work_experience, bio, hashed_pw
    ))
    uid = cur.lastrowid
    for m in majors:
      mid = get_or_create_id(conn, "Majors", "name", m)
      cur.execute("INSERT INTO User_Majors VALUES(?,?)", (uid, mid))
    for g in affinity_groups:
      gid = get_or_create_id(conn, "Affinity_Groups", "name", g)
      cur.execute("INSERT INTO User_Affinity_Groups VALUES(?,?)", (uid, gid))
    for i in interests:
      iid = get_or_create_id(conn, "Interests", "name", i)
      cur.execute("INSERT INTO User_Interests VALUES(?,?)", (uid, iid))
    for t in seeking:
      tid = get_or_create_id(conn, "Mentorship_Topics", "name", t)
      cur.execute("INSERT INTO User_Seeking_Mentorship VALUES(?,?)", (uid, tid))
    for t in offering:
      tid = get_or_create_id(conn, "Mentorship_Topics", "name", t)
      cur.execute("INSERT INTO User_Offering_Mentorship VALUES(?,?)", (uid, tid))
    for r in roles:
      rid = get_or_create_id(conn, "Roles", "name", r)
      cur.execute("INSERT INTO User_Roles VALUES(?,?)", (uid, rid))
    conn.commit()
    conn.close()

    session['user_id'] = uid
    return uid

def update_quiz(user_id):
    name                = request.form["name"]
    pronoun             = request.form["pronoun"]
    res_college         = request.form["residential_college"]
    college_year        = request.form["college_year"]
    extracurriculars    = request.form["extracurriculars"]
    work_experience     = request.form["work_experience"]
    bio                 = request.form["bio"]

    majors           = request.form.getlist("majors[]")
    affinity_groups  = request.form.getlist("affinity_groups[]")
    interests        = request.form.getlist("interests[]")
    seeking          = request.form.getlist("mentorship_seeking[]")
    offering         = request.form.getlist("mentorship_offering[]")
    roles            = request.form.getlist("roles[]")

    errors = []
    if not majors:   errors.append("Select at least one major.")
    if not interests:errors.append("Select at least one interest.")
    if not seeking:  errors.append("Select something you’re seeking.")
    if not offering: errors.append("Select something you’re offering.")
    if not roles:    errors.append("Select at least one role.")
    if errors:
        for e in errors: flash(e, "warning")
        return redirect(url_for('profile_edit', user_id=user_id))

    headshot_path = None
    file = request.files.get("headshot")
    if file and allowed_file(file.filename):
        fn = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, fn))
        headshot_path = f"uploads/{fn}"

    conn = sqlite3.connect("lux.sqlite")
    cur = conn.cursor()
    if headshot_path:
        cur.execute("""
          UPDATE Users SET
            name=?, pronoun=?, residential_college=?, college_year=?,
            headshot_path=?, extracurriculars=?, work_experience=?, bio=?
          WHERE user_id=?
        """, (
          name, pronoun, res_college, college_year,
          headshot_path, extracurriculars, work_experience, bio, user_id
        ))
    else:
        cur.execute("""
          UPDATE Users SET
            name=?, pronoun=?, residential_college=?, college_year=?,
            extracurriculars=?, work_experience=?, bio=?
          WHERE user_id=?
        """, (
          name, pronoun, res_college, college_year,
          extracurriculars, work_experience, bio, user_id
        ))
    for tbl in [
      "User_Majors","User_Affinity_Groups","User_Interests",
      "User_Seeking_Mentorship","User_Offering_Mentorship","User_Roles"
    ]:
      cur.execute(f"DELETE FROM {tbl} WHERE user_id=?", (user_id,))
    for m in majors:
      mid = get_or_create_id(conn, "Majors", "name", m)
      cur.execute("INSERT INTO User_Majors VALUES(?,?)", (user_id, mid))
    for g in affinity_groups:
      gid = get_or_create_id(conn, "Affinity_Groups", "name", g)
      cur.execute("INSERT INTO User_Affinity_Groups VALUES(?,?)", (user_id, gid))
    for i in interests:
      iid = get_or_create_id(conn, "Interests", "name", i)
      cur.execute("INSERT INTO User_Interests VALUES(?,?)", (user_id, iid))
    for t in seeking:
      tid = get_or_create_id(conn, "Mentorship_Topics", "name", t)
      cur.execute("INSERT INTO User_Seeking_Mentorship VALUES(?,?)", (user_id, tid))
    for t in offering:
      tid = get_or_create_id(conn, "Mentorship_Topics", "name", t)
      cur.execute("INSERT INTO User_Offering_Mentorship VALUES(?,?)", (user_id, tid))
    for r in roles:
      rid = get_or_create_id(conn, "Roles", "name", r)
      cur.execute("INSERT INTO User_Roles VALUES(?,?)", (user_id, rid))

    conn.commit()
    conn.close()

    flash("Your changes have been saved!", "success")
    return redirect(url_for('profile_view', user_id=user_id))
