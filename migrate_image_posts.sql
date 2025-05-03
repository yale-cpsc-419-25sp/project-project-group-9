--migrate_image_posts
ALTER TABLE Community_Posts
ADD COLUMN image_path TEXT;
