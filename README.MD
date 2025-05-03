For our final full stack project, we would like to create a website called BigSib.com, a mentorship platform specifically catered to the Yale experience. Since it can often be difficult to understand the opportunities on campus, get into professional industries, and find professional support systems, BigSib.com addresses a critical gap in Yale's student support ecosystem by creating a targeted mentorship platform that transforms how students connect and grow professionally. The platform features a comprehensive profile creation process through an interactive quiz that collects critical student information– including name, hometown, residential college, ethnicity, major, interests, hobbies, and affinity group memberships. Through this quiz, the web application will enable Yale students, especially incoming first-years, to find personalized mentors who share similar backgrounds, interests, and career aspirations. At the conclusion of the profile quiz, users will be presented with a curated list of potential mentors with high-interest matches they should consider reaching out to for mentorship. Unlike existing platforms like CrossCampus, BigSib.com focuses on meaningful, data-driven connections that empower students to navigate their academic and professional journeys more effectively, with a particular emphasis on supporting incoming freshmen in building robust networks and accessing career resources tailored to their unique Yale experience. To build our database, we hope to draw from existing databases, such as the Yalies.io, specific organizations’ Big Sib, Lil Sib tables, and our own data collection through the quiz. 

Features: 
1. User Profile: Each user has a detailed profile displaying their information, such as grade, their extracurriculars, classes, jobs, interests, and what they are willing to talk to people about. We hope to use LinkedIn as an inspiration for the look of this page. After signing up on the home page, users will be directed to their profile page. We will have two versions of this: a page people can edit and a preview version that others see. We store the data we gain through this profile set up in a database, helping us pair people up. Since this will be a Yale-centered system and people are logging in through CAS, they can reach out to each other through their Yale emails, shown on their profiles. 
2. Profile Quiz: As part of the onboarding process on joining our mentorship network, when a user signs up they must go through a sign up quiz that both creates their login in credentials but collects key information to build their profile. This information is then fed into the matching algorithm to populate mentors or mentees that have high similarity scores as them based on their profile.
3. Matching algorithm: Our matching algorithm will assign tags to each user profile based on their quiz responses, including factors like major, hometown, residential college, affinity groups, career interests, and hobbies. Each pairing will have a weighted score that is calculated through common tags that contribute to a similarity score. The final recommendations will be sorted by highest to lowest score and listed on the home page.
4. Mentor listing (quiz results): A list of mentors the user should consider matching with from the matching quiz
Additional deliverable (stretch goal): maybe we include some on-campus opportunities (such as upcoming career fairs, networking events, and mentorship workshops) that the user should check out on the home page
5. Community discussion boards: Users can join community pages for specific professions or interests (such as software engineering, pre-med, and public service). In these discussion forums, they can make posts, raising awareness about resources and opportunities. Users can also filter posts based on users, interests, and post type (motivational, interpersonal, job posting, resource, and/or event). 

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
