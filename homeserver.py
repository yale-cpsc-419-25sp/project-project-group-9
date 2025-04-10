import os
import sys
import argparse
from flask import Flask, render_template, session, redirect, url_for
from quiz import quiz_form, submit_quiz, profile as profile_route
from community import community_bp
from flask_cas import CAS

# Create the Flask app
app = Flask(__name__)

# Register routes from quiz.py
app.add_url_rule('/quiz', view_func=quiz_form)
app.add_url_rule('/submit', view_func=submit_quiz, methods=['POST'])
app.add_url_rule('/profile/<int:user_id>', view_func=profile_route)

# Set the secret key
app.secret_key = "your_secret_key"

# Configure CAS for authentication
cas = CAS(app, "/cas")
app.config["CAS_SERVER"] = "https://secure.its.yale.edu/cas"
app.config["CAS_AFTER_LOGIN"] = "home"

# Register the community blueprint with a URL prefix 
app.register_blueprint(community_bp, url_prefix="/community")

# Define routes for additional pages
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/mentors')
def mentors():
    return render_template('mentors.html')

@app.route("/login")
def login():
    
    session['CAS_USERNAME'] = 'testuser'
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/user")
def user():
    if "CAS_USERNAME" in session:
        return f"Logged in as {session['CAS_USERNAME']}"
    return "Not logged in"

def check_database_exists(db_path='lux.sqlite'):
    """Check if the database file exists."""
    if not os.path.exists(db_path):
        print(f"Error: The database file '{db_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Mentorship Quiz Application")
    parser.add_argument('port', type=int, help='The port at which the server should listen')
    args = parser.parse_args()
    if args.port < 1 or args.port > 65535:
        print("Error: The port must be between 1 and 65535.", file=sys.stderr)
        sys.exit(1)
    check_database_exists()
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()
