from flask import Blueprint, render_template
from produsys.auth import login_required

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('')
@login_required
def index():
    return render_template('dashboard/index.html')
