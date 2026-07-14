from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Scheme
from app.services.eligibility import get_recommendations

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Retrieve all schemes from database
    schemes = Scheme.query.all()
    
    # Calculate recommendations
    recs = get_recommendations(current_user, schemes)
    
    # Just show count of eligible schemes
    eligible_count = len(recs['eligible'])
    partial_count = len(recs['partially_eligible'])
    
    # Pick top 3 eligible schemes for quick dashboard preview
    top_eligible = recs['eligible'][:3]
    
    # Recent document uploads summary
    recent_uploads = current_user.uploads[-3:] if current_user.uploads else []
    
    return render_template(
        'dashboard.html',
        eligible_count=eligible_count,
        partial_count=partial_count,
        top_eligible=top_eligible,
        recent_uploads=recent_uploads
    )
