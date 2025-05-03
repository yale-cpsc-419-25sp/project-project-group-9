#match.py
import sqlite3

def get_user_attributes(conn, user_id):
    cur = conn.cursor()
    def fetch(q):
        cur.execute(q, (user_id,))
        return set(r[0] for r in cur.fetchall())
    interests = fetch("SELECT name FROM Interests JOIN User_Interests USING (interest_id) WHERE user_id = ?")
    majors    = fetch("SELECT name FROM Majors JOIN User_Majors USING (major_id) WHERE user_id = ?")
    groups    = fetch("SELECT name FROM Affinity_Groups JOIN User_Affinity_Groups USING (group_id) WHERE user_id = ?")
    seeking   = fetch("SELECT name FROM Mentorship_Topics JOIN User_Seeking_Mentorship USING (topic_id) WHERE user_id = ?")
    offering  = fetch("SELECT name FROM Mentorship_Topics JOIN User_Offering_Mentorship USING (topic_id) WHERE user_id = ?")
    return interests | majors | groups | seeking | offering

def get_mentor_ids(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT ur.user_id FROM User_Roles ur
        JOIN Roles r ON ur.role_id = r.role_id
        WHERE r.name = 'Mentor'
    """)
    return [r[0] for r in cur.fetchall()]

def get_user_name(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT name FROM Users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else "Unknown"

def calculate_match_scores(conn, target_user_id):
    target_attrs = get_user_attributes(conn, target_user_id)
    mentors = [m for m in get_mentor_ids(conn) if m != target_user_id]
    scores = []
    for mid in mentors:
        attrs = get_user_attributes(conn, mid)
        shared = target_attrs & attrs
        union = target_attrs | attrs
        score = len(shared) / len(union) if union else 0.0
        scores.append({
            "user_id": mid,
            "name": get_user_name(conn, mid),
            "shared_attributes": sorted(shared),
            "score": score
        })
    return sorted(scores, key=lambda x: x["score"], reverse=True)
