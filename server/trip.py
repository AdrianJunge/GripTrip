from flask import Blueprint, render_template, redirect, url_for, flash, request
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
    trip = model.Proposal.query.get_or_404(trip_id)

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
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        if not set_details_from_request(trip):
            return redirect(url_for("trip.edit_trip", trip_id=trip.id))

        db.session.commit()
        return redirect(url_for("trip.view_trip", trip_id=trip.id))

    return render_template("trip/edit_trip.html", trip=trip)


@bp.route("/trip/<int:trip_id>")
@login_required
def view_trip(trip_id):
    trip = model.Proposal.query.get_or_404(trip_id)

    if not trip.has_permission(current_user, model.ProposalParticipantRole.VIEWER):
        flash("You do not have permission to view this trip.", "error")
        return redirect(url_for("main.index"))

    return render_template("trip/view_trip.html", trip=trip)
