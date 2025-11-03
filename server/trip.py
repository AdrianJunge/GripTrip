from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required

from . import db
from . import model
import json

bp = Blueprint("trip", __name__)

@bp.route("/trip/create", methods=["GET", "POST"])
@login_required
def create_trip():
    if request.method == "POST":
        trip_name = request.form.get("trip_name")
        destination = request.form.get("destination")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        max_participants = request.form.get("max_participants")

        budget = request.form.get("budget")
        accommodation = request.form.get("accommodation")
        transportation = request.form.get("transportation")
        activities = request.form.get("activities")
        departure_location = request.form.get("departure_location")

        if not trip_name or not destination or not start_date or not end_date:
            flash("All fields are required.", "error")
            return redirect(url_for("trip.create_trip"))

        new_trip = model.Proposal(
            user_id=current_user.id,
            title=trip_name,
            dates=[(start_date, end_date)],
            destinations=[destination],
            max_participants=int(max_participants) if max_participants else 1,
            budget=budget,
            accommodation=accommodation,
            transportation=transportation,
            activities=activities,
            departure_locations=[departure_location] if departure_location is not None else [],
        )
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
        trip.title = request.form.get("trip_name")
        trip.destinations = request.form.getlist("destination")
        trip.dates = [(request.form.get("start_date"), request.form.get("end_date"))]
        trip.max_participants = int(request.form.get("max_participants"))

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
