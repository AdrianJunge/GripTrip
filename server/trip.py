import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from . import db
from . import model
import json
import requests

bp = Blueprint("trip", __name__)


def set_destination_coordinates(trip_proposal):
    if trip_proposal.destinations:
        primary = trip_proposal.destinations[0]
        coords = fetch_coordinates_for_destination(primary)
        if coords == None: raise ValueError("There's no such destination")
        
        print("coords: ", coords)
        print("Primary: ", primary)

        if coords:
            trip_proposal.primary_coordinates = coords
            trip_proposal.primary_destination = primary
        else:
            flash("No primary destination found.", "error")
            return False

def fetch_coordinates_for_destination(destination):
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": destination, "format": "json", "limit": 1},
            headers={"User-Agent": "UC3M-WebAppProject/1.0"}
        )
        response.raise_for_status()
        data = response.json()

        print(f"DATA FETCHED : {data}", flush=True)

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return (lat, lon)
    except Exception as e:
        print(f"Error fetching coordinates for {destination}: {e}")
    return None

def set_details_from_request(trip_proposal):
    destinations = json.loads(request.form.get("destinations")) if request.form.get("destinations") else []
    activities = json.loads(request.form.get("activity")) if request.form.get("activity") else []

    # set departure thingy
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
        set_destination_coordinates(trip_proposal)
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
        
        # check that mandatory fields are in 
        if not trip_name or not max_participants:
            flash("Mandatory fields are missing", "error")
            return redirect(url_for("trip.create_trip"))
        
        if len(trip_name) > 25:
            flash("Trip name too long (max 25 characters)", "error")
            return redirect(url_for("trip.create_trip"))

        # create new trip
        try:
            new_trip = model.Proposal(
                user_id=current_user.id,
                title=trip_name,
                max_participants=max_participants or 1,
            )
        except Exception as e:
            flash(str(e), "error:")
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
    
    required_fields = [
        'destinations',
        'dates',
        'activities',
        'accommodation',
        'transportation',
        'departure_locations',
        'budget',
    ]
    all_final = all(trip.is_final(f) for f in required_fields)

    if request.method == "POST":
        if trip.status in (model.ProposalStatus.FINALIZED, model.ProposalStatus.CANCELLED):
            flash("This trip is finalized or cancelled and cannot be edited.", "error")
            return redirect(url_for("trip.view_trip", trip_id=trip.id))

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
                    new_status = model.ProposalStatus[status_str]
                except Exception:
                    flash("Invalid status selected", "error")
                    return redirect(url_for("trip.edit_trip", trip_id=trip.id))

                if new_status == model.ProposalStatus.FINALIZED and not all_final:
                    flash("Cannot mark trip as FINALIZED: not all details are finalized.", "error")
                    return redirect(url_for("trip.edit_trip", trip_id=trip.id))

                trip.status = new_status
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        if not set_details_from_request(trip):
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        db.session.commit()
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    return render_template(
        "trip/edit_trip.html",
        trip=trip,
        ProposalStatus=model.ProposalStatus,
        all_final=all_final,
    )


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

    query = (
        db.select(model.Meetup)
        .where(model.Meetup.proposal_id == trip.id)
        .order_by(model.Meetup.date_raw.asc())
    )
    meetups = db.session.execute(query).scalars().all()

    meetup_membership = {}
    for m in meetups:
        member_ids = {mp.user_id for mp in m.participants}
        meetup_membership[m.id] = (current_user.id in member_ids)

    if not trip.has_permission(current_user, model.ProposalParticipantRole.VIEWER):
        flash("You do not have permission to view this trip.", "error")
        return redirect(url_for("main.index"))

    return render_template(
        "trip/view_trip.html",
        trip=trip,
        messages=messages,
        meetups=meetups,
        meetup_membership=meetup_membership,
        now=datetime.datetime.now(datetime.timezone.utc),
        ProposalParticipantRole=model.ProposalParticipantRole,
    )


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

    if trip.status != model.ProposalStatus.OPEN:
        flash("This trip is not open for joining.", "error")
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
        flash("No access to this trip.", "error")
        return redirect(url_for("main.index"))

    current_p = trip.get_participant(current_user)
    query = (
        db.select(model.User)
        .where(model.User.id == user_id)
    )
    target_user = db.session.execute(query).scalar_one_or_none()
    if target_user is None:
        flash("Target user not found.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))
    target_p = trip.get_participant(target_user)
    if target_p is None:
        flash("Target user is not a participant.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))
    new_role_str = request.form.get('role') or (request.json and request.json.get('role'))
    if not new_role_str:
        flash("No role specified.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    try:
        new_role = model.ProposalParticipantRole[new_role_str.upper()]
    except Exception:
        flash("Invalid role specified.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    # Admins cannot change their own role so there is always at least one admin with inherent editing rights
    if current_p and current_p.permission == model.ProposalParticipantRole.ADMIN:
        if target_p.user_id == current_user.id and new_role != model.ProposalParticipantRole.ADMIN:
            flash("Admins cannot change their own role.", "error")
            return redirect(url_for("trip.view_trip", trip_id=trip.id))
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
        flash("You do not have permission to change this role.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    old_role = target_p.permission.name if target_p.permission is not None else 'UNKNOWN'
    target_p.permission = new_role
    db.session.commit()

    flash(f"Participant role for {target_p.user.username} updated successfully from {old_role} to {new_role.name}.", "success")
    return redirect(url_for("trip.view_trip", trip_id=trip.id))


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

    if not trip.has_permission(current_user, model.ProposalParticipantRole.VIEWER):
        flash("You do not have permission to post messages in this trip.", "error")
        return redirect(url_for("main.index"))

    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    if trip.status in (model.ProposalStatus.FINALIZED, model.ProposalStatus.CANCELLED):
        flash("Cannot post messages to a finalized or cancelled trip.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

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


@bp.route("/trip/<int:trip_id>/create_meeting", methods=["POST"])
@login_required
def create_meeting(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    if not trip.has_permission(current_user, model.ProposalParticipantRole.EDITOR):
        flash("You do not have permission to create meetings for this trip.", "error")
        return redirect(url_for("main.index"))

    title = request.form.get("meeting_title")
    scheduled_time_str = request.form.get("scheduled_time")
    location = request.form.get("location") or None
    description = request.form.get("description") or None

    if not title or not scheduled_time_str:
        flash("Mandatory fields are missing", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    try:
        scheduled_time = datetime.datetime.fromisoformat(scheduled_time_str)
    except ValueError:
        flash("Invalid date and time format.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    new_meeting = model.Meetup(
        proposal_id=trip.id,
        title=title,
        date_raw=scheduled_time,
        location=location or "",
        description=description or "",
        created_by_user_id=current_user.id,
    )
    meeting_participant = model.MeetupParticipant(
        user_id=current_user.id,
        meetup=new_meeting,
    )
    new_meeting.participants.append(meeting_participant)

    db.session.add(new_meeting)
    db.session.add(meeting_participant)
    db.session.commit()

    flash(f"Meeting created successfully for the date {scheduled_time.strftime('%Y-%m-%d %H:%M')}.", "success")
    return redirect(url_for("trip.view_trip", trip_id=trip.id) + f"#meeting-{new_meeting.id}")


@bp.route("/trip/<int:trip_id>/meetup/<int:meetup_id>/join", methods=["POST"])
@login_required
def join_meetup(trip_id, meetup_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    query = (
        db.select(model.Meetup)
        .where(model.Meetup.id == meetup_id)
        .where(model.Meetup.proposal_id == trip.id)
    )
    meetup = db.session.execute(query).scalar_one_or_none()
    if meetup is None:
        flash("Meetup not found.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    if not trip.has_permission(current_user, model.ProposalParticipantRole.VIEWER):
        flash("You do not have permission to join this meetup.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    query = (
        db.select(model.MeetupParticipant)
        .where(model.MeetupParticipant.meetup_id == meetup.id)
        .where(model.MeetupParticipant.user_id == current_user.id)
    )
    existing = db.session.execute(query).scalar_one_or_none()
    if existing:
        flash("You are already participating in this meetup.", "info")
        return redirect(url_for("trip.view_trip", trip_id=trip.id) + f"#meeting-{meetup.id}")

    new_participant = model.MeetupParticipant(
        meetup_id=meetup.id,
        user_id=current_user.id,
    )
    meetup.participants.append(new_participant)
    db.session.add(new_participant)
    db.session.commit()

    flash("You joined the meetup.", "success")
    return redirect(url_for("trip.view_trip", trip_id=trip.id) + f"#meeting-{meetup.id}")


@bp.route("/trip/<int:trip_id>/meetup/<int:meetup_id>/leave", methods=["POST"])
@login_required
def leave_meetup(trip_id, meetup_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    query = (
        db.select(model.Meetup)
        .where(model.Meetup.id == meetup_id)
        .where(model.Meetup.proposal_id == trip.id)
    )
    meetup = db.session.execute(query).scalar_one_or_none()
    if meetup is None:
        flash("Meetup not found.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    query = (
        db.select(model.MeetupParticipant)
        .where(model.MeetupParticipant.meetup_id == meetup.id)
        .where(model.MeetupParticipant.user_id == current_user.id)
    )
    participant = db.session.execute(query).scalar_one_or_none()
    if participant is None:
        flash("You are not a participant in this meetup.", "info")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    if meetup.created_by_user_id == current_user.id:
        flash("The creator of a meetup cannot leave it.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    db.session.delete(participant)
    db.session.commit()

    flash("You have left the meetup.", "success")
    return redirect(url_for("trip.view_trip", trip_id=trip.id))


@bp.route("/trip/<int:trip_id>/meetup/create", methods=["GET"])
@login_required
def create_meetup_page(trip_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    if not trip.has_permission(current_user, model.ProposalParticipantRole.EDITOR):
        flash("You do not have permission to create meetups for this trip.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    return render_template("trip/create_meetup.html", trip=trip)


@bp.route("/trip/<int:trip_id>/meetup/<int:meetup_id>/edit", methods=["GET", "POST"])
@login_required
def edit_meetup(trip_id, meetup_id):
    query = (
        db.select(model.Proposal)
        .where(model.Proposal.id == trip_id)
    )
    trip = db.session.execute(query).scalar_one_or_none()
    if trip is None:
        flash(f"Trip with id {trip_id} not found.", "error")
        return redirect(url_for("main.index"))

    query = (
        db.select(model.Meetup)
        .where(model.Meetup.id == meetup_id)
        .where(model.Meetup.proposal_id == trip.id)
    )
    meetup = db.session.execute(query).scalar_one_or_none()
    if meetup is None:
        flash("Meetup not found.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    if not (
        trip.has_permission(current_user, model.ProposalParticipantRole.EDITOR)
        or meetup.created_by_user_id == current_user.id
    ):
        flash("You do not have permission to edit this meetup.", "error")
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    if request.method == "POST":
        title = request.form.get("meeting_title")
        scheduled_time_str = request.form.get("scheduled_time")
        location = request.form.get("location") or None
        description = request.form.get("description") or None

        if not title or not scheduled_time_str:
            flash("Mandatory fields are missing", "error")
            return redirect(url_for("trip.edit_meetup", trip_id=trip.id, meetup_id=meetup.id))

        try:
            scheduled_time = datetime.datetime.fromisoformat(scheduled_time_str)
        except ValueError:
            flash("Invalid date and time format.", "error")
            return redirect(url_for("trip.edit_meetup", trip_id=trip.id, meetup_id=meetup.id))

        meetup.title = title
        meetup.date_raw = scheduled_time
        meetup.location = location or ""
        meetup.description = description or ""

        db.session.commit()
        flash("Meetup updated successfully.", "success")
        return redirect(url_for("trip.view_trip", trip_id=trip.id) + f"#meeting-{meetup.id}")

    return render_template("trip/edit_meetup.html", trip=trip, meetup=meetup)
