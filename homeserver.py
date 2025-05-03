import os
import sqlite3
from functools import wraps

from flask import (
    Flask, flash, render_template,
    session, redirect, url_for,
    request, abort, Response
)
from quiz import quiz_form, submit_quiz, update_quiz
from match import calculate_match_scores
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
    errors = session.pop('form_errors', [])
    return render_template('quiz.html', errors=errors)

@app.route('/new_profile')
def new_profile():
    return quiz_form()

@app.route('/submit', methods=['POST'])
def submit_quiz_route():
    result = submit_quiz()

    # If result is a Response (like redirect due to form errors), just return it
    if isinstance(result, Response):
        return result

    # Otherwise, it should be a user_id (int)
    session['user_id'] = result
    return redirect(url_for('profile_view', user_id=result))

@app.route('/profile/<int:user_id>/edit', methods=['GET','POST'])
@login_required
def profile_edit(user_id):
    if session['user_id'] != user_id:
        abort(403)
    if request.method == 'POST':
        return update_quiz(user_id)
    return quiz_form(user_id)

@app.route('/loginsignup', methods=['GET','POST'])
def loginsignup():
    if request.method == 'POST':
        profile_id = request.form['profile_id']
        password   = request.form['password']
        conn = sqlite3.connect('lux.sqlite'); conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            pid = int(profile_id)
            cur.execute("SELECT user_id, hashed_password FROM Users WHERE user_id=?", (pid,))
        except ValueError:
            cur.execute("SELECT user_id, hashed_password FROM Users WHERE user_id=?", (profile_id,))
        row = cur.fetchone(); conn.close()
        if row and bcrypt.checkpw(password.encode('utf-8'), row['hashed_password']):
            session['user_id'] = row['user_id']
            return redirect(url_for('profile_view', user_id=row['user_id']))
        return render_template('loginsignup.html', error="Invalid User ID or Password.")
    return render_template('loginsignup.html')

@app.route('/switch_profile')
@login_required
def switch_profile():
    cas_username = session.get('cas_username')
    if not cas_username:
        return redirect(url_for('home'))
    conn = sqlite3.connect('lux.sqlite'); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT user_id,name FROM Users WHERE cas_username=?", (cas_username,))
    profiles = cur.fetchall(); conn.close()
    return render_template('switch_profile.html', profiles=profiles)

@app.route('/select_profile/<int:user_id>')
def select_profile(user_id):
    conn = sqlite3.connect('lux.sqlite'); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT user_id,cas_username FROM Users WHERE user_id=?", (user_id,))
    user = cur.fetchone(); conn.close()
    if user:
        session['user_id'] = user['user_id']
        if user['cas_username']:
            session['cas_username'] = user['cas_username']
        return redirect(url_for('profile_view', user_id=user_id))
    flash("Profile not found","danger")
    return redirect(url_for('home'))

@app.route('/mentors')
@login_required
def mentors():
    uid = session['user_id']
    conn = sqlite3.connect('lux.sqlite')
    raw = calculate_match_scores(conn, uid)
    conn.close()
    user_id = session['user_id']

    conn = sqlite3.connect('lux.sqlite')

    raw_scores = calculate_match_scores(conn, user_id)

    conn.close()

    mentors = []
    for m in raw:
        pct = round((m.get('score') or 0) * 100)
        mentors.append({
            'user_id': m['user_id'],
            'name': m['name'],
            'score': pct,
            'shared_attributes': m.get('shared_attributes', [])
        })
    return render_template('mentors.html', mentors=mentors, user_id=uid)
        
    mentors = sorted(mentors, key=lambda m: m['score'], reverse=True)[:3]

    return render_template('mentors.html', mentors=mentors, user_id=user_id)


@app.route('/profile/<int:user_id>')
@login_required
def profile_view(user_id):
    return profile_route(user_id)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    print(f"* Serving on http://127.0.0.1:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)
