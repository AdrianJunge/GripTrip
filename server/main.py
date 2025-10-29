from datetime import datetime
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from . import db, model
from datetime import timezone

bp = Blueprint("main", __name__)

@bp.route("/")
@login_required
def index():
    return render_template(
        "main/base.html"
    )
