# homeserver.py
import os
import sqlite3
from functools import wraps

from flask import Flask, flash, render_template, session, redirect, url_for, request
from quiz import quiz_form, submit_quiz
from user_profile import profile as profile_route
from community import community_bp
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

app.register_blueprint(community_bp, url_prefix='/community')

@app.context_processor
def inject_profile_id():
    return {'user_id': session.get('user_id')}

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('loginsignup'))
        return f(*args, **kwargs)
    return wrapped

@app.route('/login')
def login():
    return redirect(url_for('loginsignup'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/quiz')
def quiz_page():
    return quiz_form()

@app.route('/new_profile')
def new_profile():
    # Allow users to create a new profile even if already logged in
    return quiz_form()

@app.route('/submit', methods=['POST'])
def submit_quiz_route():
    user_id = submit_quiz()
    # Set the session to this newly created profile
    session['user_id'] = user_id
    return redirect(url_for('profile_view', user_id=user_id))

@app.route('/loginsignup', methods=['GET', 'POST'])
def loginsignup():
    if request.method == 'POST':
        profile_id = request.form['profile_id']
        password = request.form['password']

        conn = sqlite3.connect('lux.sqlite')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Convert profile_id to integer if it's an integer string
        try:
            user_id = int(profile_id)
            cur.execute("SELECT user_id, hashed_password FROM Users WHERE user_id = ?", (user_id,))
        except ValueError:
            # If it's not an integer, search by the string ID
            cur.execute("SELECT user_id, hashed_password FROM Users WHERE user_id = ?", (profile_id,))
            
        row = cur.fetchone()
        conn.close()

        if row and row['hashed_password']:
            if bcrypt.checkpw(password.encode('utf-8'), row['hashed_password']):
                session['user_id'] = row['user_id']
                # Also store cas_username if we know it
                conn = sqlite3.connect('lux.sqlite')
                cur = conn.cursor()
                cur.execute("SELECT cas_username FROM Users WHERE user_id = ?", (row['user_id'],))
                cas_row = cur.fetchone()
                if cas_row and cas_row[0]:
                    session['cas_username'] = cas_row[0]
                conn.close()
                
                return redirect(url_for('profile_view', user_id=row['user_id']))

        return render_template('loginsignup.html', error="Invalid User ID or Password. Please try again.")

    return render_template('loginsignup.html')

@app.route('/switch_profile')
@login_required
def switch_profile():
    # Get current CAS username if available
    cas_username = session.get('cas_username')
    
    if not cas_username:
        flash("Unable to find associated profiles", "warning")
        return redirect(url_for('home'))
    
    # Fetch all profiles for this CAS username
    conn = sqlite3.connect('lux.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT user_id, name 
        FROM Users 
        WHERE cas_username = ?
    """, (cas_username,))
    
    profiles = cur.fetchall()
    conn.close()
    
    return render_template('switch_profile.html', profiles=profiles)

@app.route('/select_profile/<int:user_id>')
def select_profile(user_id):
    # Switch to the selected profile
    conn = sqlite3.connect('lux.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT user_id, cas_username FROM Users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    
    if user:
        session['user_id'] = user['user_id']
        if user['cas_username']:
            session['cas_username'] = user['cas_username']
        
        return redirect(url_for('profile_view', user_id=user_id))
    
    flash("Profile not found", "danger")
    return redirect(url_for('home'))

@app.route('/mentors')
@login_required
def mentors():
    user_id = session.get('user_id')

    conn = sqlite3.connect('lux.sqlite')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT user_id, name FROM Users")
    rows = cur.fetchall()
    conn.close()

    mentors = [{
        'user_id': r['user_id'],
        'name': r['name'],
        'score': 1.0,
        'shared_attributes': []
    } for r in rows]
    return render_template('mentors.html', mentors=mentors, user_id=user_id)

@app.route('/profile/<int:user_id>')
@login_required
def profile_view(user_id):
    return profile_route(user_id)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print(f"* Serving on http://127.0.0.1:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)