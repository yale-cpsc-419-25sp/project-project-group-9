import os
import sqlite3
from flask import (
    Blueprint, render_template, request, session,
    flash, redirect, url_for
)
from datetime import datetime
from contextlib import closing
from werkzeug.utils import secure_filename

community_bp = Blueprint("community_bp", __name__)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "lux.sqlite")


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_id_by_cas_username(cas_username):
    if not cas_username:
        return None
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM Users WHERE cas_username = ?",
            (cas_username,)
        )
        row = cur.fetchone()
        return row["user_id"] if row else None


@community_bp.route("/communities", methods=["GET", "POST"])
def list_communities():
    profile_id = get_user_id_by_cas_username(session.get("CAS_USERNAME"))
    now = datetime.now()

    # always load all for checkbox form
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT community_id, name, description "
            "FROM Communities ORDER BY name"
        )
        all_list = cur.fetchall()

    if request.method == "POST":
        selected_ids = request.form.getlist("community_ids")
        if selected_ids:
            placeholders = ",".join("?" for _ in selected_ids)
            query = (
                f"SELECT community_id, name, description "
                f"FROM Communities WHERE community_id IN ({placeholders}) "
                f"ORDER BY name"
            )
            with closing(get_db_connection()) as conn:
                cur = conn.cursor()
                cur.execute(query, selected_ids)
                communities = cur.fetchall()
        else:
            communities = []

        return render_template(
            "community_list.html",
            communities=communities,
            selected_ids=selected_ids,
            profile_id=profile_id,
            now=now
        )

    # GET: show checkbox selector
    return render_template(
        "community_list.html",
        communities=all_list,
        profile_id=profile_id,
        now=now
    )


@community_bp.route("/communities/<int:community_id>")
def view_community(community_id):
    post_type = request.args.get("post_type", "")
    sort      = request.args.get("sort", "recent")
    now       = datetime.now()

    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Communities WHERE community_id = ?",
            (community_id,)
        )
        community = cur.fetchone()
        if not community:
            flash("Community not found.", "danger")
            return redirect(url_for("community_bp.list_communities"))

        # build base query
        base = """
            SELECT p.post_id, p.title, p.content, p.post_type,
                   p.created_at, p.deleted_at,
                   u.name AS author_name,
                   u.cas_username AS author_netid,
                   (SELECT COUNT(*) FROM Community_Post_Likes    WHERE post_id=p.post_id)    AS like_count,
                   (SELECT COUNT(*) FROM Community_Post_Dislikes WHERE post_id=p.post_id) AS dislike_count
              FROM Community_Posts p
              JOIN Users u ON p.user_id=u.user_id
        """
        filters = ["p.community_id = ?"]
        params  = [community_id]
        if post_type:
            filters.append("p.post_type = ?")
            params.append(post_type)
        base += " WHERE " + " AND ".join(filters)

        if sort == "most_liked":
            base += " ORDER BY like_count DESC"
        elif sort == "author":
            base += " ORDER BY author_name COLLATE NOCASE ASC"
        else:
            base += " ORDER BY p.created_at DESC"

        cur.execute(base, params)
        raw = cur.fetchall()

    # convert ISO strings to datetimes
    posts = []
    for row in raw:
        d = dict(row)
        try:
            d["created_at"] = datetime.fromisoformat(d["created_at"])
            if d.get("deleted_at"):
                d["deleted_at"] = datetime.fromisoformat(d["deleted_at"])
        except Exception:
            pass
        posts.append(d)

    return render_template(
        "community_view.html",
        community=community,
        posts=posts,
        selected_post_type=post_type,
        selected_sort=sort,
        now=now
    )


@community_bp.route("/communities/<int:community_id>/newpost", methods=["GET", "POST"])
def new_post(community_id):
    if "CAS_USERNAME" not in session:
        return redirect(url_for("cas.login"))
    casid = session["CAS_USERNAME"]
    # look up or create user
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM Users WHERE cas_username = ?",
            (casid,)
        )
        row = cur.fetchone()
        if not row:
            flash("Your CAS username isn’t linked.", "danger")
            return redirect(url_for("community_bp.list_communities"))
        uid = row["user_id"]

    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Communities WHERE community_id = ?",
            (community_id,)
        )
        community = cur.fetchone()
        if not community:
            flash("Community not found.", "danger")
            return redirect(url_for("community_bp.list_communities"))

        if request.method == "POST":
            title   = request.form.get("title","").strip()
            content = request.form.get("content","").strip()
            ptype   = request.form.get("post_type","").strip()
            image   = request.files.get("image")
            image_path = None
            if image and image.filename:
                filename = secure_filename(image.filename)
                upload_dir = os.path.join("static", "uploads")
                os.makedirs(upload_dir, exist_ok=True)
                image.save(os.path.join(upload_dir, filename))
                image_path = f"uploads/{filename}"

            if not (title and content and ptype):
                flash("All fields are required.", "warning")
                return redirect(
                    url_for("community_bp.new_post", community_id=community_id)
                )

            now = datetime.now()
            cur.execute("""
                INSERT INTO Community_Posts
                  (community_id, user_id, title, content, post_type, image_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (community_id, uid, title, content, ptype, image_path, now, now))
            conn.commit()
            flash("Post created successfully!", "success")
            return redirect(
                url_for("community_bp.view_community", community_id=community_id)
            )

    return render_template("new_post.html", community=community)


@community_bp.route("/communities/<int:community_id>/post/<int:post_id>")
def view_post(community_id, post_id):
    now = datetime.now()
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Communities WHERE community_id = ?",
            (community_id,)
        )
        community = cur.fetchone()
        if not community:
            flash("Community not found.", "danger")
            return redirect(url_for("community_bp.list_communities"))

        # fetch post
        cur.execute("""
            SELECT p.post_id, p.title, p.content, p.post_type,
                   p.created_at, p.deleted_at,
                   u.name AS author_name,
                   u.cas_username AS author_netid,
                   (SELECT COUNT(*) FROM Community_Post_Likes    WHERE post_id=p.post_id)    AS like_count,
                   (SELECT COUNT(*) FROM Community_Post_Dislikes WHERE post_id=p.post_id) AS dislike_count
              FROM Community_Posts p
              JOIN Users u ON p.user_id=u.user_id
             WHERE p.community_id=? AND p.post_id=?
        """, (community_id, post_id))
        row = cur.fetchone()
        if not row:
            flash("Post not found.", "danger")
            return redirect(
                url_for("community_bp.view_community", community_id=community_id)
            )

        # fetch comments
        cur.execute("""
            SELECT c.comment_id, c.content, c.created_at, u.name AS author_name
              FROM Community_Post_Comments c
              JOIN Users u ON c.user_id=u.user_id
             WHERE c.post_id=?
             ORDER BY c.created_at ASC
        """, (post_id,))
        comments_raw = cur.fetchall()

    post = dict(row)
    try:
        post["created_at"] = datetime.fromisoformat(post["created_at"])
        if post.get("deleted_at"):
            post["deleted_at"] = datetime.fromisoformat(post["deleted_at"])
    except Exception:
        pass

    comments = []
    for c in comments_raw:
        d = dict(c)
        try:
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        except Exception:
            pass
        comments.append(d)

    return render_template(
        "view_post.html",
        community=community,
        post=post,
        comments=comments,
        now=now
    )


@community_bp.route(
    "/communities/<int:community_id>/post/<int:post_id>/like",
    methods=["POST"]
)
def like_post(community_id, post_id):
    if "CAS_USERNAME" not in session:
        return redirect(url_for("cas.login"))
    casid = session["CAS_USERNAME"]
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM Users WHERE cas_username = ?",
            (casid,)
        )
        row = cur.fetchone()
        if not row:
            return redirect(url_for("community_bp.list_communities"))
        uid = row["user_id"]

        cur.execute(
            "DELETE FROM Community_Post_Dislikes WHERE post_id=? AND user_id=?",
            (post_id, uid)
        )
        cur.execute(
            "SELECT 1 FROM Community_Post_Likes WHERE post_id=? AND user_id=?",
            (post_id, uid)
        )
        if cur.fetchone():
            cur.execute(
                "DELETE FROM Community_Post_Likes WHERE post_id=? AND user_id=?",
                (post_id, uid)
            )
        else:
            cur.execute(
                "INSERT INTO Community_Post_Likes "
                "(post_id,user_id,created_at) VALUES (?,?,?)",
                (post_id, uid, datetime.now())
            )
        conn.commit()

    return redirect(
        url_for("community_bp.view_community", community_id=community_id)
    )


@community_bp.route(
    "/communities/<int:community_id>/post/<int:post_id>/dislike",
    methods=["POST"]
)
def dislike_post(community_id, post_id):
    if "CAS_USERNAME" not in session:
        return redirect(url_for("cas.login"))
    casid = session["CAS_USERNAME"]
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM Users WHERE cas_username = ?",
            (casid,)
        )
        row = cur.fetchone()
        if not row:
            return redirect(url_for("community_bp.list_communities"))
        uid = row["user_id"]

        cur.execute(
            "DELETE FROM Community_Post_Likes WHERE post_id=? AND user_id=?",
            (post_id, uid)
        )
        cur.execute(
            "SELECT 1 FROM Community_Post_Dislikes WHERE post_id=? AND user_id=?",
            (post_id, uid)
        )
        if cur.fetchone():
            cur.execute(
                "DELETE FROM Community_Post_Dislikes WHERE post_id=? AND user_id=?",
                (post_id, uid)
            )
        else:
            cur.execute(
                "INSERT INTO Community_Post_Dislikes "
                "(post_id,user_id,created_at) VALUES (?,?,?)",
                (post_id, uid, datetime.now())
            )
        conn.commit()

    return redirect(
        url_for("community_bp.view_community", community_id=community_id)
    )


@community_bp.route(
    "/communities/<int:community_id>/post/<int:post_id>/comment",
    methods=["POST"]
)
def comment_post(community_id, post_id):
    if "CAS_USERNAME" not in session:
        return redirect(url_for("cas.login"))
    content = request.form.get("comment","").strip()
    if not content:
        flash("Comment cannot be empty.", "warning")
        return redirect(
            url_for("community_bp.view_post",
                    community_id=community_id,
                    post_id=post_id)
        )
    casid = session["CAS_USERNAME"]
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id FROM Users WHERE cas_username = ?",
            (casid,)
        )
        row = cur.fetchone()
        if not row:
            return redirect(url_for("community_bp.list_communities"))
        uid = row["user_id"]

        cur.execute(
            "INSERT INTO Community_Post_Comments "
            "(post_id,user_id,content,created_at) VALUES (?,?,?,?)",
            (post_id, uid, content, datetime.now())
        )
        conn.commit()

    return redirect(
        url_for("community_bp.view_post",
                community_id=community_id,
                post_id=post_id)
    )


@community_bp.route(
    "/communities/<int:community_id>/post/<int:post_id>/delete",
    methods=["POST"]
)
def delete_post(community_id, post_id):
    if "CAS_USERNAME" not in session:
        return redirect(url_for("cas.login"))
    with closing(get_db_connection()) as conn:
        cur = conn.cursor()
        # verify ownership
        cur.execute(
            "SELECT user_id FROM Community_Posts WHERE post_id=?",
            (post_id,)
        )
        row = cur.fetchone()
        if not row or session["CAS_USERNAME"] is None:
            flash("Unauthorized.", "danger")
            return redirect(
                url_for("community_bp.view_community",
                        community_id=community_id)
            )
        # delete
        cur.execute(
            "DELETE FROM Community_Posts WHERE post_id=?",
            (post_id,)
        )
        conn.commit()
        flash("Post deleted.", "info")

    return redirect(
        url_for("community_bp.view_community", community_id=community_id)
    )
