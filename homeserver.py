import os
import sys
import argparse
from flask import Flask, render_template, session, redirect, url_for
from flask_cas import CAS

# Create the Flask app
app = Flask(__name__)

# Flask session secret key (change this in production)
app.secret_key = "your_secret_key"

# Initialize CAS authentication
cas = CAS(app, "/cas")

# Configure Yale's CAS
app.config["CAS_SERVER"] = "https://secure.its.yale.edu/cas"
app.config["CAS_AFTER_LOGIN"] = "home"

def check_database_exists(db_path='bigsib-db'):
    """Check if the database file exists."""
    if not os.path.exists(db_path):
        print(f"Error: The database file '{db_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

# Define routes for different pages
@app.route('/')
def home():
    """Home page, only accessible if user is authenticated."""
    if "CAS_USERNAME" in session:
        return render_template('home.html', user=session['CAS_USERNAME'])
    return redirect(url_for('login'))

@app.route('/quiz')
def quiz():
    """Quiz page, only accessible if user is authenticated."""
    if "CAS_USERNAME" in session:
        return render_template('quiz.html')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    """Profile page, only accessible if user is authenticated."""
    if "CAS_USERNAME" in session:
        return render_template('profile.html')
    return redirect(url_for('login'))

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route("/login")
def login():
    """Redirect to Yale CAS login."""
    return redirect(url_for("cas.login"))

@app.route("/logout")
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for("cas.logout"))

@app.route("/user")
def user():
    """Check and return authenticated user."""
    if "CAS_USERNAME" in session:
        return f"Logged in as {session['CAS_USERNAME']}"
    return "Not logged in"



def main():
    """Main function to start the Flask server."""
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
