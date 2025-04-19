# user_profile.py
import sqlite3
from flask import render_template, url_for

def profile(user_id):
    conn = sqlite3.connect("lux.sqlite")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return "User not found", 404

    def fetch(query):
        cur.execute(query, (user_id,))
        return [r["name"] for r in cur.fetchall()]

    majors         = fetch("SELECT name FROM Majors JOIN User_Majors USING (major_id) WHERE user_id = ?")
    affinity_groups= fetch("SELECT name FROM Affinity_Groups JOIN User_Affinity_Groups USING (group_id) WHERE user_id = ?")
    interests      = fetch("SELECT name FROM Interests JOIN User_Interests USING (interest_id) WHERE user_id = ?")
    seeking        = fetch("SELECT name FROM Mentorship_Topics JOIN User_Seeking_Mentorship USING (topic_id) WHERE user_id = ?")
    offering       = fetch("SELECT name FROM Mentorship_Topics JOIN User_Offering_Mentorship USING (topic_id) WHERE user_id = ?")
    roles          = fetch("SELECT name FROM Roles JOIN User_Roles USING (role_id) WHERE user_id = ?")

    headshot = user["headshot_path"] or "default.jpg"

    data = {
        "name": user["name"],
        "pronoun": user["pronoun"],
        "res_college": user["residential_college"],
        "college_year": user["college_year"],
        "extracurriculars": user["extracurriculars"],
        "work_exp": user["work_experience"],
        "bio": user["bio"],
        "headshot": headshot
    }

    conn.close()
    return render_template(
        "profile.html",
        profile=data,
        majors=majors,
        affinity_groups=affinity_groups,
        interests=interests,
        seeking=seeking,
        offering=offering,
        roles=roles
    )
