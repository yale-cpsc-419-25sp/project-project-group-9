import sqlite3

def get_user_attributes(conn, user_id):
    cursor = conn.cursor()
    def fetch_names(query, uid):
        cursor.execute(query, (uid,))
        return set(row[0] for row in cursor.fetchall())
    interests = fetch_names("""
        SELECT name FROM Interests
        JOIN User_Interests USING (interest_id)
        WHERE user_id = ?
    """, user_id)
    majors = fetch_names("""
        SELECT name FROM Majors
        JOIN User_Majors USING (major_id)
        WHERE user_id = ?
    """, user_id)
    affinity_groups = fetch_names("""
        SELECT name FROM Affinity_Groups
        JOIN User_Affinity_Groups USING (group_id)
        WHERE user_id = ?
    """, user_id)
    seeking = fetch_names("""
        SELECT name FROM Mentorship_Topics
        JOIN User_Seeking_Mentorship USING (topic_id)
        WHERE user_id = ?
    """, user_id)
    offering = fetch_names("""
        SELECT name FROM Mentorship_Topics
        JOIN User_Offering_Mentorship USING (topic_id)
        WHERE user_id = ?
    """, user_id)
    return interests | majors | affinity_groups | seeking | offering

def get_all_user_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users")
    return [row[0] for row in cursor.fetchall()]

def get_user_name(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown"

def calculate_match_scores(conn, target_user_id):
    target_attributes = get_user_attributes(conn, target_user_id)
    all_users = get_all_user_ids(conn)
    scores = []
    for other_user_id in all_users:
        if other_user_id == target_user_id:
            continue
        other_attributes = get_user_attributes(conn, other_user_id)
        shared_attributes = target_attributes.intersection(other_attributes)
        total_attributes = target_attributes.union(other_attributes)
        similarity_score = len(shared_attributes) / len(total_attributes) if total_attributes else 0.0
        scores.append({
            "user_id": other_user_id,
            "name": get_user_name(conn, other_user_id),
            "shared_attributes": list(shared_attributes),
            "score": round(similarity_score, 2)
        })
    return sorted(scores, key=lambda x: x["score"], reverse=True)

def main():
    conn = sqlite3.connect("lux.sqlite")   
    target_user_id = int(input("Enter the user ID to find matches for: "))
    match_scores = calculate_match_scores(conn, target_user_id)
    print(f"\nTop Matches for User {target_user_id}:\n")
    for match in match_scores:
        print(f"Name: {match['name']} (ID: {match['user_id']})")
        print(f" - Match Score: {match['score'] * 100:.1f}%")
        print(f" - Shared Attributes: {', '.join(match['shared_attributes'])}")
        print("-" * 40)
    conn.close()

if __name__ == "__main__":
    main()
