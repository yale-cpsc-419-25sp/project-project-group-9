import os
import sys
import argparse
from flask import Flask, render_template, session, redirect, url_for
from quiz import quiz_form, submit_quiz, profile as profile_route


# Create the Flask app
app = Flask(__name__)

app.add_url_rule('/quiz', view_func=quiz_form)
app.add_url_rule('/submit', view_func=submit_quiz, methods=['POST'])
app.add_url_rule('/profile/<int:user_id>', view_func=profile_route)

# Flask session secret key (change this in production)
app.secret_key = "your_secret_key"

def check_database_exists(db_path='lux.sqlite'):
    """Check if the database file exists."""
    if not os.path.exists(db_path):
        print(f"Error: The database file '{db_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

# Define routes for different pages
@app.route('/')
def home():
    """Home page."""
    return render_template('home.html')

@app.route('/quiz')
def quiz():
    """Quiz page."""
    return render_template('quiz.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/mentors')
def mentors():
    return render_template('mentors.html')

@app.route("/login")
def login():
    """Mock login route for local testing."""
    session['CAS_USERNAME'] = 'testuser'
    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('home'))

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
