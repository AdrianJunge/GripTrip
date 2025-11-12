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
        .filter(model.Proposal.status == model.ProposalStatus.OPEN)
        .order_by(model.Proposal.timestamp.desc())
        .all()
    )

    user_country = current_user.country
    try:
        country = CountryInfo(user_country)
        lat, lon = country.info()["latlng"]
        user_home = (lat, lon)
    except Exception as e:
        user_home = None

    return render_template(
        "main/index.html",
        trips=trips,
        user_home=user_home,
        user_country=user_country,
    )
