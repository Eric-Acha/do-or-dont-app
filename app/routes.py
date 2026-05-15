from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Post, Vote, Comment

main = Blueprint("main", __name__)

@main.route("/")
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)

@main.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category = request.form.get("category")

        post = Post(
            title=title,
            content=content,
            category=category,
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()

        flash("Post created successfully.")
        return redirect(url_for("main.index"))

    return render_template("create_post.html")

@main.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    do_votes = Vote.query.filter_by(post_id=post.id, vote_type="Do").count()
    dont_votes = Vote.query.filter_by(post_id=post.id, vote_type="Dont").count()
    total_votes = do_votes + dont_votes

    do_percent = round((do_votes / total_votes) * 100, 1) if total_votes else 0
    dont_percent = round((dont_votes / total_votes) * 100, 1) if total_votes else 0

    return render_template(
        "post_detail.html",
        post=post,
        do_votes=do_votes,
        dont_votes=dont_votes,
        do_percent=do_percent,
        dont_percent=dont_percent
    )

@main.route("/post/<int:post_id>/vote/<vote_type>", methods=["POST"])
@login_required
def vote(post_id, vote_type):
    if vote_type not in ["Do", "Dont"]:
        flash("Invalid vote.")
        return redirect(url_for("main.post_detail", post_id=post_id))

    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing_vote:
        existing_vote.vote_type = vote_type
    else:
        new_vote = Vote(
            vote_type=vote_type,
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(new_vote)

    db.session.commit()
    return redirect(url_for("main.post_detail", post_id=post_id))

@main.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def comment(post_id):
    content = request.form["content"]

    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id
    )

    db.session.add(comment)
    db.session.commit()

    return redirect(url_for("main.post_detail", post_id=post_id)) 