from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    try:
        conn = sqlite3.connect("lux.sqlite")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            profile_data = {
                'name': user['name'],
                'pronoun': user['pronoun'],
                'res_college': user['residential_college'],
                'college_year': user['college_year'],
                # If you store lists differently (using join tables), you may need to adapt this.
                'majors': [],
                'affinity_groups': [],
                'extracurriculars': user['extracurriculars'],
                'interests': [],
                'work_exp': user['work_experience'],
                'mentorship_seeking': [],
                'mentorship_offering': [],
                'bio': user['bio'],
                'roles': [],
                'headshot': user['headshot_path'] if user['headshot_path'] else 'default.jpg'
            }
            return render_template('profile.html', profile=profile_data)
        else:
            return "User not found", 404
    except sqlite3.Error as e:
        return f"Database error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
