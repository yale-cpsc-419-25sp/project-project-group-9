--migrate_add_post_interactions.sql
ALTER TABLE Community_Posts ADD COLUMN deleted_at TIMESTAMP;

CREATE TABLE IF NOT EXISTS Community_Post_Likes (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES Community_Posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)         ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community_Post_Dislikes (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES Community_Posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)         ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community_Post_Comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id    INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    content    TEXT    NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES Community_Posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)         ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community_Post_Shares (
    share_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id      INTEGER NOT NULL,
    sharer_id    INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id)      REFERENCES Community_Posts(post_id)       ON DELETE CASCADE,
    FOREIGN KEY (sharer_id)    REFERENCES Users(user_id)                ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES Users(user_id)                ON DELETE CASCADE
);
