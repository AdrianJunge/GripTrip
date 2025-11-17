import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required

from . import db
from . import model
import json

bp = Blueprint("trip", __name__)

def set_details_from_request(trip_proposal):
    destinations = json.loads(request.form.get("destination")) if request.form.get("destination") else []
    activities = json.loads(request.form.get("activity")) if request.form.get("activity") else []
    departure_locations = json.loads(request.form.get("departure_location")) if request.form.get("departure_location") else []

    start_dates = request.form.getlist("start_date") or []
    end_dates = request.form.getlist("end_date") or []
    dates = list(zip(start_dates, end_dates))

    budget = request.form.get("budget") or None
    accommodation = request.form.get("accommodation") or None
    transportation = request.form.get("transportation") or None

    try:
        trip_proposal.destinations = destinations
        trip_proposal.budget = budget
        trip_proposal.accommodation = accommodation
        trip_proposal.transportation = transportation
        trip_proposal.activities = activities
        trip_proposal.departure_locations = departure_locations
        trip_proposal.dates = dates
    except Exception as e:
        flash (str(e), "error")
        return False
    return True

@bp.route("/trip/create", methods=["GET", "POST"])
@login_required
def create_trip():
    if request.method == "POST":
        trip_name = request.form.get("trip_name")
        max_participants = request.form.get("max_participants")

        if not trip_name or not max_participants:
            flash("Mandatory fields are missing", "error")
            return redirect(url_for("trip.create_trip"))

        try:
            new_trip = model.Proposal(
                user_id=current_user.id,
                title=trip_name,
                max_participants=max_participants or 1,
            )
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("trip.create_trip"))

        if not set_details_from_request(new_trip):
            return redirect(url_for("trip.create_trip"))

        participant = model.ProposalParticipant(
            user_id=current_user.id,
            proposal_id=new_trip.id,
            permission=model.ProposalParticipantRole.ADMIN,
        )

        new_trip.participants.append(participant)

        db.session.add(new_trip)
        db.session.commit()
        return redirect(url_for("trip.view_trip", trip_id=new_trip.id))

    return render_template("trip/create_trip.html")


@bp.route("/trip/edit/<int:trip_id>", methods=["GET", "POST"])
@login_required
def edit_trip(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    if not trip.has_permission(current_user, model.ProposalParticipantRole.EDITOR):
        flash("You do not have permission to edit this trip.", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        if request.form.get('toggle_final'):
            field = request.form.get('toggle_final')
            action = request.form.get('toggle_action')
            if action == 'finalize':
                trip.finalize(field, by_user=current_user.id)
                flash(f"Field '{field}' marked as final.", "success")
            else:
                trip.unfinalize(field)
                flash(f"Field '{field}' marked as open.", "success")
            db.session.commit()
            return redirect(url_for('trip.edit_trip', trip_id=trip.id))

        trip_name = request.form.get("trip_name")
        max_participants = request.form.get("max_participants")

        if not trip_name or not max_participants:
            flash("Mandatory fields are missing", "error")
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        try:
            trip.title = trip_name
            trip.max_participants = int(max_participants)
            status_str = request.form.get("status")
            if status_str:
                try:
                    trip.status = model.ProposalStatus[status_str]
                except Exception:
                    flash("Invalid status selected", "error")
                    return redirect(url_for("trip.edit_trip", trip_id=trip.id))
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        if not set_details_from_request(trip):
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        db.session.commit()
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    return render_template("trip/edit_trip.html", trip=trip, ProposalStatus=model.ProposalStatus)


@bp.route("/trip/<int:trip_id>")
@login_required
def view_trip(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    query = (
        db.select(model.Message)
        .where(model.Message.proposal_id == trip.id)
        .order_by(model.Message.timestamp_raw.asc())
    )
    messages = db.session.execute(query).scalars().all()

    if not trip.has_permission(current_user, model.ProposalParticipantRole.VIEWER):
        flash("You do not have permission to view this trip.", "error")
        return redirect(url_for("main.index"))

    return render_template("trip/view_trip.html", trip=trip, messages=messages, now=datetime.datetime.now(datetime.timezone.utc), ProposalParticipantRole=model.ProposalParticipantRole)


@bp.route("/trip/join/<int:trip_id>", methods=["POST"])
@login_required
def join(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    if trip.participant_count >= trip.max_participants:
        flash("This trip is already full.", "error")
        return redirect(url_for("main.index"))

    query = (
        db.select(model.ProposalParticipant)
        .where(model.ProposalParticipant.proposal_id == trip.id)
        .where(model.ProposalParticipant.user_id == current_user.id)
    )
    existing_participant = db.session.execute(query).scalar_one_or_none()

    if existing_participant:
        flash("You are already a participant in this trip.", "info")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    new_participant = model.ProposalParticipant(
        user_id=current_user.id,
        proposal_id=trip.id,
        permission=model.ProposalParticipantRole.VIEWER,
    )

    trip.participants.append(new_participant)
    db.session.commit()

    return redirect(url_for("trip.view_trip", trip_id=trip.id))


@bp.route("/trip/<int:trip_id>/participant/<int:user_id>/role", methods=["POST"])
@login_required
def change_participant_role(trip_id, user_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    if not trip.has_permission(current_user, model.ProposalParticipantRole.VIEWER):
        return jsonify({"success": False, "error": "No access to this trip."}), 403

    current_p = trip.get_participant(current_user)
    query = (
        db.select(model.User)
        .where(model.User.id == user_id)
    )
    target_user = db.session.execute(query).scalar_one_or_none()
    if target_user is None:
        return jsonify({"success": False, "error": "Target user not found."}), 404
    target_p = trip.get_participant(target_user)
    if target_p is None:
        return jsonify({"success": False, "error": "Target user is not a participant."}), 404

    new_role_str = request.form.get('role') or (request.json and request.json.get('role'))
    if not new_role_str:
        return jsonify({"success": False, "error": "No role specified."}), 400

    try:
        new_role = model.ProposalParticipantRole[new_role_str.upper()]
    except Exception:
        return jsonify({"success": False, "error": "Invalid role specified."}), 400

    # Admins cannot change their own role so there is always at least one admin with inherent editing rights
    if current_p and current_p.permission == model.ProposalParticipantRole.ADMIN:
        if target_p.user_id == current_user.id and new_role != model.ProposalParticipantRole.ADMIN:
            return jsonify({"success": False, "error": "Admins cannot change their own role."}), 403
        allowed = True
    elif current_p and current_p.permission == model.ProposalParticipantRole.EDITOR:
        if target_p.permission == model.ProposalParticipantRole.ADMIN:
            allowed = False
        elif new_role == model.ProposalParticipantRole.ADMIN:
            allowed = False
        elif new_role.value < target_p.permission.value:
            allowed = False
        else:
            allowed = (new_role == model.ProposalParticipantRole.EDITOR)
    else:
        allowed = False

    if not allowed:
        return jsonify({"success": False, "error": "You do not have permission to change this role."}), 403

    old_role = target_p.permission.name if target_p.permission is not None else 'UNKNOWN'
    target_p.permission = new_role
    db.session.commit()

    return jsonify({
        "success": True,
        "new_role": new_role.name,
        "messages": [{
            "category": "success",
            "text": f"Participant role for {target_p.user.username} updated successfully from {old_role} to {new_role.name}."
        }]
    })


@bp.route("/trip/<int:trip_id>/leave", methods=["POST"])
@login_required
def leave_trip(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    participant = trip.get_participant(current_user)
    if participant is None:
        flash("You are not a participant in this trip.", "error")
        return redirect(url_for("main.index"))

    if trip.user_id == current_user.id:
        flash("The creator of a trip cannot leave it.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    if participant.permission == model.ProposalParticipantRole.ADMIN:
        flash("Admins cannot leave the trip.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    db.session.delete(participant)
    db.session.commit()

    flash("You have left the trip.", "success")
    return redirect(url_for("main.index"))


@bp.route("/trip/<int:trip_id>/post_message", methods=["POST"])
@login_required
def post_message(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    content = request.form.get("message_content")
    if not content:
        flash("Message content cannot be empty.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    new_message = model.Message(
        proposal_id=trip.id,
        user_id=current_user.id,
        content=content,
        response_to_id=request.form.get("response_to") or None,
    )

    db.session.add(new_message)
    db.session.commit()

    flash("Message posted successfully.", "success")
    return redirect(url_for("trip.view_trip", trip_id=trip.id) + f"#message-{new_message.id}")
