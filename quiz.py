from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set up file upload configurations
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Define your upload folder
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Define allowed image types

if not os.path.exists(app.config['UPLOAD_FOLDER']): # CHANGED CODDE HERE 
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route for displaying the form
@app.route('/')
def quiz_form():
    return render_template('quiz.html')

# Route for handling form submission
@app.route('/submit', methods=['POST'])
def submit_quiz():                                      # CHANGED CODDE HERE 
    # Get all the form data
    name = request.form.get("name")
    pronoun = request.form.get("pronoun")
    residential_college = request.form.get("residential_college")
    college_year = request.form.get("college_year")
    majors = ', '.join(request.form.getlist("majors"))
    affinity_group = ', '.join(request.form.getlist("affinity_group"))
    extracurriculars = request.form.get("extracurriculars")
    interests = ', '.join(request.form.getlist("interests"))
    work_experience = request.form.get("work_experience")
    seeking_mentorship = ', '.join(request.form.getlist("seeking_mentorship"))
    offering_mentorship = ', '.join(request.form.getlist("offering_mentorship"))
    bio = request.form.get("bio")
    roles = ', '.join(request.form.getlist("roles")) 

    # Handle file upload
    if 'headshot' not in request.files:
        return redirect(request.url)
    file = request.files['headshot']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    else:
        file_path = None  # If no valid image, set to None

    # Insert data into the database
    conn = sqlite3.connect("bigsib-db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, pronoun, residential_college, college_year, majors, 
                           affinity_group, extracurriculars, interests, work_experience, 
                           seeking_mentorship, offering_mentorship, bio, roles, headshot_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, pronoun, residential_college, college_year, majors, affinity_group,
          extracurriculars, interests, work_experience, seeking_mentorship,
          offering_mentorship, bio, roles, file_path))

    conn.commit()
    user_id = cursor.lastrowid  # Get the ID of the newly inserted user
    conn.close()

    print(f"New user ID: {user_id}")  # CHANGED CODDE HERE 

    # Redirect to the profile page with the user's ID
    return redirect(url_for('profile', user_id=user_id))

# Route for displaying the user's profile
@app.route('/profile/<int:user_id>')
def profile(user_id):
    # Fetch user data from the database using the user_id
    conn = sqlite3.connect("bigsib-db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('profile.html', user=user)
    else:
        return "User not found", 404

if __name__ == '__main__':
    app.run(debug=True)
