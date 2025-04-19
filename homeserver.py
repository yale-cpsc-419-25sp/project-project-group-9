import os
import sqlite3
from functools import wraps

from flask import Flask, render_template, session, redirect, url_for, request
from flask_cas import CAS

from quiz import quiz_form, submit_quiz
from user_profile import profile as profile_route
from community import community_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

# ---- CAS CONFIGURATION ----
app.config['CAS_SERVER']         = 'https://secure.its.yale.edu'
app.config['CAS_LOGIN_ROUTE']    = '/cas/login'
app.config['CAS_VALIDATE_ROUTE'] = '/cas/serviceValidate'
app.config['CAS_LOGOUT_ROUTE']   = '/cas/logout'
app.config['CAS_VERSION']        = '2'
# ← You **must** tell Flask‑CAS where to go after login & after logout:
app.config['CAS_AFTER_LOGIN']    = 'home'
app.config['CAS_AFTER_LOGOUT']   = 'home'

cas = CAS(app, '/cas')


# ---- a decorator to protect pages ----
def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'CAS_USERNAME' not in session:
            return redirect(url_for('cas.login', next=request.path))
        return f(*args, **kwargs)
    return wrapped


# ---- register blueprints & routes ----
app.register_blueprint(community_bp, url_prefix='/community')


@app.route('/login')
def login():
    return redirect(url_for('cas.login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('cas.logout'))


@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/resources')
@login_required
def resources():
    return render_template('resources.html')

@app.route('/quiz')
@login_required
def quiz_page():
    return quiz_form()

@app.route('/submit', methods=['POST'])
@login_required
def submit_quiz_route():
    return submit_quiz()

@app.route('/mentors')
@login_required
def mentors():
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
    return render_template('mentors.html', mentors=mentors)

@app.route('/profile/<int:user_id>')
@login_required
def profile_view(user_id):
    return profile_route(user_id)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
