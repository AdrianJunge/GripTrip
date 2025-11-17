from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from . import db
from . import model

bp = Blueprint("profile", __name__)


@bp.route("/profile", defaults={"user_id": None})
@bp.route("/profile/<int:user_id>")
@login_required
def view_profile(user_id):
    if user_id is None:
        user_id = current_user.id
    query = (
        db.select(model.User)
        .where(model.User.id == user_id)
    )
    user = db.session.execute(query).scalar_one_or_none()
    if user is None:
        flash(f"User with id {user_id} not found.", "error")
        return redirect(url_for("main.index"))

    query = (
        db.select(model.Proposal)
        .join(model.Proposal.participants)
        .filter(model.ProposalParticipant.user_id == user.id)
        .filter(model.Proposal.user_id != user.id)
        .order_by(model.Proposal.timestamp_raw.desc())
    )
    trips_joined = db.session.execute(query).scalars().all()
    return render_template("profile/view_profile.html", user=user, trips_joined=trips_joined)


@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_bio = request.form.get("bio")

        query = (
            db.select(model.User)
            .where(model.User.username == new_username)
        )
        existing_user = db.session.execute(query).scalar_one_or_none()
        if len(new_username) <= 0:
            flash("Invalid username.", "error")
            return render_template("profile/edit_profile.html", user=current_user)
        if existing_user is not None and existing_user.id != current_user.id:
            flash("Username already taken.", "error")
            return render_template("profile/edit_profile.html", user=current_user)

        current_user.username = new_username
        current_user.bio = new_bio
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.view_profile", user_id=current_user.id))
    return render_template("profile/edit_profile.html", user=current_user)


@bp.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow(user_id):
    query = (
        db.select(model.User)
        .where(model.User.id == user_id)
    )
    user_to_follow = db.session.execute(query).scalar_one_or_none()
    if user_to_follow is None:
        flash(f"User with id {user_id} not found.", "error")
        return redirect(url_for("main.index"))

    if user_to_follow.id == current_user.id:
        flash("You cannot follow yourself.", "error")
        return {"message": "Cannot follow yourself"}, 400
    if user_to_follow in current_user.following:
        flash("You are already following this user.", "error")
        return {"message": "Already following"}, 400
    user_to_follow.followers.append(current_user)
    db.session.commit()
    flash("You are now following this user.", "success")
    return redirect(url_for("profile.view_profile", user_id=user_to_follow.id))


@bp.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow(user_id):
    query = (
        db.select(model.User)
        .where(model.User.id == user_id)
    )
    user_to_unfollow = db.session.execute(query).scalar_one_or_none()
    if user_to_unfollow is None:
        flash(f"User with id {user_id} not found.", "error")
        return redirect(url_for("main.index"))

    if user_to_unfollow.id == current_user.id:
        flash("You cannot unfollow yourself.", "error")
        return {"message": "Cannot unfollow yourself"}, 400
    if user_to_unfollow not in current_user.following:
        flash("You are not following this user.", "error")
        return {"message": "Not following"}, 400
    user_to_unfollow.followers.remove(current_user)
    db.session.commit()
    flash("You have unfollowed this user.", "success")
    return redirect(url_for("profile.view_profile", user_id=user_to_unfollow.id))
