from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from . import db, model
from datetime import timezone
from countryinfo import CountryInfo

bp = Blueprint("main", __name__)

@bp.route("/")
@login_required
def index():
    trips = (
        model.Proposal.query
        .filter(model.Proposal.max_participants > model.Proposal.participant_count)
        .order_by(model.Proposal.timestamp.desc())
        .all()
    )

    user_country_name = current_user.country.name
    user_home = None
    if user_country_name:
        try:
            country = CountryInfo(user_country_name)
            lat, lon = country.info()["latlng"]
            user_home = (lat, lon)
        except:
            user_home = None

    return render_template(
        "main/index.html",
        trips=trips,
        user_home=user_home,
        user_country = user_country_name,
    )
