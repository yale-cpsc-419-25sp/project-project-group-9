# community.py
import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from contextlib import closing

community_bp = Blueprint("community_bp", __name__)

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "lux.sqlite")

def get_db_connection():
    """Utility to connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

@community_bp.route("/communities")
def list_communities():
    """Show all existing communities."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT community_id, name, description FROM Communities ORDER BY name ASC;")
        communities = cursor.fetchall()
    return render_template("community_list.html", communities=communities)

@community_bp.route("/communities/<int:community_id>")
def view_community(community_id):
    """
    Show all posts in a single community, optionally filtering by post_type.
    """
    post_type = request.args.get("post_type", None)
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT community_id, name, description FROM Communities WHERE community_id = ?", (community_id,))
        community = cursor.fetchone()
        if not community:
            flash("Community not found.", "danger")
            return redirect(url_for("community_bp.list_communities"))
        query = """
            SELECT p.post_id, p.title, p.content, p.post_type, p.created_at,
                   u.name AS author_name
            FROM Community_Posts p
            JOIN Users u ON p.user_id = u.user_id
            WHERE p.community_id = ?
        """
        params = [community_id]
        if post_type:
            query += " AND p.post_type = ?"
            params.append(post_type)
        query += " ORDER BY p.created_at DESC"
        cursor.execute(query, params)
        posts = cursor.fetchall()
    return render_template("community_view.html", community=community, posts=posts, selected_post_type=post_type)

@community_bp.route("/communities/<int:community_id>/newpost", methods=["GET", "POST"])
def new_post(community_id):
    """Create a new post in the specified community."""
    if "CAS_USERNAME" not in session:
        flash("You must be logged in to create a post.", "warning")
        return redirect(url_for("home"))
    user_id = get_user_id_by_cas_username(session["CAS_USERNAME"])
    if user_id is None:
        flash("Your CAS username is not linked to a user account.", "danger")
        return redirect(url_for("home"))
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT community_id, name FROM Communities WHERE community_id = ?", (community_id,))
        community = cursor.fetchone()
        if not community:
            flash("Community not found.", "danger")
            return redirect(url_for("community_bp.list_communities"))
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            post_type = request.form.get("post_type", "").strip()
            if not title or not content or not post_type:
                flash("All fields are required.", "warning")
                return redirect(url_for("community_bp.new_post", community_id=community_id))
            now = datetime.now()
            cursor.execute("""
                INSERT INTO Community_Posts (community_id, user_id, title, content, post_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (community_id, user_id, title, content, post_type, now, now))
            conn.commit()
            flash("Post created successfully!", "success")
            return redirect(url_for("community_bp.view_community", community_id=community_id))
    return render_template("new_post.html", community=community)

@community_bp.route("/communities/<int:community_id>/post/<int:post_id>")
def view_post(community_id, post_id):
    """Show a single post in detail."""
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT community_id, name FROM Communities WHERE community_id = ?", (community_id,))
        community = cursor.fetchone()
        if not community:
            flash("Community not found.", "danger")
            return redirect(url_for("community_bp.list_communities"))
        cursor.execute("""
            SELECT p.post_id, p.title, p.content, p.post_type, p.created_at,
                   u.name AS author_name
            FROM Community_Posts p
            JOIN Users u ON p.user_id = u.user_id
            WHERE p.community_id = ? AND p.post_id = ?
        """, (community_id, post_id))
        post = cursor.fetchone()
        if not post:
            flash("Post not found.", "danger")
            return redirect(url_for("community_bp.view_community", community_id=community_id))
    return render_template("view_post.html", community=community, post=post)

def get_user_id_by_cas_username(cas_username):
    """
    Helper function to map a CAS username to a user_id in the Users table.
    Adjust this if you store CAS information differently.
    """
    if not cas_username:
        return None
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE name = ?", (cas_username,))
        result = cursor.fetchone()
        if result:
            return result["user_id"]
    return None
