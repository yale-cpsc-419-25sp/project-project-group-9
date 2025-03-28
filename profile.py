from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Route to display user profile
@app.route('/profile/<int:user_id>')
def profile(user_id):
    # Connect to the database and fetch user data based on user_id
    try:
        conn = sqlite3.connect("bigsib-db.db")  # Replace with your actual DB file
        cursor = conn.cursor()

        # Query the user data from the database
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Map user data to a dictionary for easy access in the template
            profile_data = {
                'name': user[1],  # Assuming column order in your users table
                'pronoun': user[2],
                'res_college': user[3],
                'college_year': user[4],
                'majors': user[5],
                'affinity_groups': user[6].split(', ') if user[6] else [],  # Safely split if not None
                'extracurriculars': user[7],
                'interests': user[8],
                'work_exp': user[9],
                'mentorship_seeking': user[10],
                'mentorship_offering': user[11],
                'bio': user[12],
                'roles': user[13].split(', ') if user[13] else [],  # Safely split if not None
                'headshot': user[14] if user[14] else 'default.jpg'  # If no headshot, use a default image
            }

            # Pass profile data to the template
            return render_template('profile.html', profile=profile_data)
        
        else:
            return "User not found", 404

    except sqlite3.Error as e:
        return f"Database error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
