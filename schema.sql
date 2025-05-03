--schema.sql
-- USERS TABLE
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cas_username TEXT,
    hashed_password TEXT NOT NULL,
    name TEXT NOT NULL,
    pronoun TEXT,
    residential_college TEXT,
    college_year TEXT,
    headshot_path TEXT,
    extracurriculars TEXT,
    work_experience TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Majors (
    major_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE Affinity_Groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE Interests (
    interest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE Mentorship_Topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE Roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- JOIN TABLES FOR MANY-TO-MANY RELATIONSHIPS

CREATE TABLE User_Majors (
    user_id INTEGER NOT NULL,
    major_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, major_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (major_id) REFERENCES Majors(major_id) ON DELETE CASCADE
);

CREATE TABLE User_Affinity_Groups (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES Affinity_Groups(group_id) ON DELETE CASCADE
);

CREATE TABLE User_Interests (
    user_id INTEGER NOT NULL,
    interest_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, interest_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES Interests(interest_id) ON DELETE CASCADE
);

CREATE TABLE User_Seeking_Mentorship (
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES Mentorship_Topics(topic_id) ON DELETE CASCADE
);

CREATE TABLE User_Offering_Mentorship (
    user_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, topic_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES Mentorship_Topics(topic_id) ON DELETE CASCADE
);

CREATE TABLE User_Roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id) ON DELETE CASCADE
);

-- Tables for community discussions

CREATE TABLE IF NOT EXISTS Communities (
    community_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    description    TEXT
);

CREATE TABLE IF NOT EXISTS Community_Posts (
    post_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    community_id   INTEGER NOT NULL,
    user_id        INTEGER NOT NULL,
    title          TEXT NOT NULL,
    content        TEXT NOT NULL,
    post_type      TEXT NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES Communities(community_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Communities (name, description) VALUES
    ('Software Engineering',    'Discuss software development, internships, hackathons, and system design'),
    ('Finance',                 'Banking, investing, corporate finance, and markets'),
    ('Consulting',              'Case prep, firm insights, and networking tips'),
    ('Extracurriculars',        'Clubs, sports, volunteering, and Yale campus life'),
    ('Data Science',            'Analytics, machine learning, data visualization, and big data'),
    ('Public Policy',           'Government, non‑profit policy analysis and advocacy'),
    ('Entrepreneurship',        'Startups, innovation, funding, and pitch practice'),
    ('Pre‑Med & Healthcare',    'Medical school prep, healthcare careers, and clinical volunteering'),
    ('Arts & Design',           'Visual and performing arts, graphic design, and creativity'),
    ('Law & Public Interest',   'Law school prep, public interest law, and social justice'),
    ('Others',                  'Miscellaneous topics and general discussions');
