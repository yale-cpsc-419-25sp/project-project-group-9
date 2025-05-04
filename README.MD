Overview

BigSib.com is a mentorship platform specifically designed for Yale students to help them navigate the academic, extracurricular, and professional landscape of campus life. Especially for first-years, finding mentors and understanding opportunities at Yale can be overwhelming. BigSib.com addresses this challenge by fostering meaningful connections through a personalized, data-driven matching system and interactive community spaces.

When students join the platform, they create a detailed profile by completing an onboarding quiz that collects key information such as their major, interests, residential college, and affinity groups. This information powers a matching algorithm that recommends potential mentors with shared backgrounds and goals, helping users build robust networks tailored to their Yale experience. Beyond one-on-one mentorship, BigSib.com also features community discussion boards organized by interests and professions, where students can share resources, ask questions, and discover opportunities posted by peers.

Key Features

1. User Profiles
- Detailed profiles with academic, extracurricular, and professional information.
- Editable by the user and viewable by others for networking purposes.

2. Profile Quiz (Onboarding)
- Users complete a quiz when signing up to populate their profile.
- The quiz data feeds directly into the matching algorithm.

3. Matching Algorithm
- Calculates weighted similarity scores based on shared attributes.
- Curated mentor recommendations appear based on scores.

4. Community Pages
- Students can join profession-based or interest-based communities.
- Users may post opportunities, events, and questions.
- Posts can be filtered by user, type, and tags.

NOTE: Our proposal never included a chat feature. Mentors and mentees can connect through the emails included in the profiles

How to Run BigSib

1. Ensure you have Python 3.x installed. In your terminal, run: pip install flask flask-cas bcrypt
SQLite3 is also required, which is often pre-installed. If not:
- macOS: Already included.
- Linux: sudo apt-get install sqlite3
- Windows: Use SQLite installer.
Important: Use the lux.sqlite provided in the GitHub repository. Do not create your own. This database comes pre-loaded with mentors and seed data.

2. RIn your terminal, run: python homeserver.py 5001
You may use any valid port if preferred (see homeserver.py for details).

3. In your browser, go to: http://127.0.0.1:5001/
You will now be able to use BigSib locally!


Documentation/Repository Structure

project-project-group-9/
├── scripts/
│   └── import_yalies.py                 # Helper script for importing user data
├── static/                              # Static files (CSS, uploaded images)
│   ├── uploads/
│   ├── community_list.css
│   ├── community_view.css
│   ├── home.css
│   ├── profile.css
│   ├── quiz.css
│   ├── styles.css
│   └── view_post.css
├── templates/                           # HTML templates for frontend pages
│   ├── community_list.html
│   ├── community_view.html
│   ├── home.html
│   ├── loginsignup.html
│   ├── mentors.html
│   ├── new_post.html
│   ├── profile.html
│   ├── quiz.html
│   └── view_post.html
├── .env                                 # Local environment configuration (optional)
├── .gitignore                           # Git ignore rules
├── clear_nonint_userids.py              # Utility for cleaning up user data
├── community.py                         # Community page routes and logic
├── homeserver.py                        # Main Flask app entry point
├── lux.sqlite                           # SQLite database (preloaded with data)
├── lux.sqlite.bak                       # Backup database
├── match.py                             # Matching logic for quiz + mentor matches
├── migration and seed SQL files (.sql)  # Database schema + migrations + seed data
├── profile.py                           # User profile routes and logic
├── quiz.py                              # Quiz routes and processing logic
├── run_migration.py                     # Utility for running SQL migrations
└── user_profile.py                      # Helper functions for loading user profiles
