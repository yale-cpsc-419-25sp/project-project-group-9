from flask import Blueprint, render_template, request, redirect, url_for

community_bp = Blueprint("community", __name__)
posts_db = []

@community_bp.route("/community")
def community_board():
    """Show all posts."""
    return render_template("community.html", posts=posts_db)

@community_bp.route("/post", methods=["GET", "POST"])
def create_post():
    """Create a new post."""
    if request.method == "POST":
        author_name = request.form.get("author_name")
        role = request.form.get("role")
        title = request.form.get("title")
        content = request.form.get("content")

        if author_name and role and title and content:
            post = {
                "author_name": author_name,
                "role": role,
                "title": title,
                "content": content
            }
            posts_db.append(post)
            return redirect(url_for("community.community_board"))

    return render_template("create_post.html")
