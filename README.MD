How to Run BigSib:

Step 1: Ensure you have Python 3.x installed, then open a terminal and run:
pip install flask flask-cas bcrypt

This will ensure that flash, flask-cas, and bcrypt are installed. Most systems come with sqlite3 preinstalled. If not, you can install it through your package manager:
- macOS: Already included
- Linux: Run sudo apt-get install sqlite3
- Windows: Use SQLite Installer (more in-depth instructions in the sql bootcamp from the beginning of the semester)

NOTE: Please don't make your own lux.sqlite. We loaded in many mentors into lux.sqlite in our GitHub. 

Step 2: Then, to start the server, run: python homeserver.py 5001 (You can choose any port within the limits shown in homeserver.py)

Step 3: Take the html url (basically something like this http://127.0.0.1:5001/) within the terminal and paste it on chrome or an equivalent and, then, you should see our website. 
