from flask import Flask, session, redirect, url_for
from flask_cas import CAS

app = Flask(__name__)

# Flask session secret key (change this in production)
app.secret_key = "your_secret_key"

# Initialize CAS authentication
cas = CAS(app, "/cas")

# Configure Yale's CAS
app.config["CAS_SERVER"] = "https://secure.its.yale.edu/cas"
app.config["CAS_AFTER_LOGIN"] = "home"

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

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
