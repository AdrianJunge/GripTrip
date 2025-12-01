from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from . import db, model
from datetime import timezone
from countryinfo import CountryInfo
from sqlalchemy.sql import func

bp = Blueprint("main", __name__)

@bp.route("/")
@login_required
def index():
    query = (
        db.select(model.Proposal)
        # can't use .participant_count directly in filter as it is a @property and only works for already loaded ORM objects
        .outerjoin(model.Proposal.participants)
        .group_by(model.Proposal.id)
        .having(func.count(model.ProposalParticipant.user_id) < model.Proposal.max_participants)
        .filter(model.Proposal.status == model.ProposalStatus.OPEN)
        .order_by(model.Proposal.timestamp_raw.desc())
    )
    overall_trips = db.session.execute(query).scalars().all()

    query = (
        db.select(model.Proposal)
        .filter(model.Proposal.user_id == current_user.id)
        .order_by(model.Proposal.timestamp_raw.desc())
    )
    user_trips = db.session.execute(query).scalars().all()

    #user_country = current_user.country
    #try:
     #   country = CountryInfo(user_country)
      #  lat, lon = country.info()["latlng"]
       # user_home = (lat, lon)
    #except Exception as e:
     #   user_home = None
    
    trip_icons = []
    for trip in user_trips:
        participant_ids = {participant.user_id for participant in trip.participants}
        if current_user.id not in participant_ids:
            continue
        try:
            country = CountryInfo(trip.country)
            lat, lon = country.info()["latlng"]
            trip_icons.append({
                "id": trip.id,
                "title": trip.title,
                "lat": lat,
                "lon": lon,
                "country_code": trip.country_code
            })
        except Exception as e:
            continue

    return render_template(
        "main/index.html",
        overall_trips=overall_trips,
        user_trips=user_trips,
        #user_home=user_home,
        #user_country=user_country, # why was this needed?
        trip_icons=trip_icons
    )