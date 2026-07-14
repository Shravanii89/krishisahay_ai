from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Scheme
from app.services.eligibility import get_recommendations, calculate_eligibility
from app.services.ai_service import AIService

schemes_bp = Blueprint('schemes', __name__)

@schemes_bp.route('/')
def list_schemes():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    state = request.args.get('state', '').strip()
    
    # Base query
    scheme_query = Scheme.query
    
    if query:
        scheme_query = scheme_query.filter(
            (Scheme.name.like(f"%{query}%")) | 
            (Scheme.description.like(f"%{query}%")) |
            (Scheme.required_crops.like(f"%{query}%"))
        )
    if category:
        scheme_query = scheme_query.filter(Scheme.category == category)
    if state:
        scheme_query = scheme_query.filter(
            (Scheme.state_specific == state) | (Scheme.state_specific == 'All')
        )
        
    schemes = scheme_query.all()
    
    # Get distinct categories & states for filter dropdowns
    categories = db_categories = [r[0] for r in Scheme.query.with_entities(Scheme.category).distinct().all()]
    states = [r[0] for r in Scheme.query.with_entities(Scheme.state_specific).distinct().all() if r[0] and r[0] != 'All']
    
    # If user logged in, check their eligibility status on the list too
    eligibility_map = {}
    if current_user.is_authenticated:
        for s in schemes:
            eligibility_map[s.id] = calculate_eligibility(current_user, s)
            
    return render_template(
        'schemes.html', 
        schemes=schemes, 
        categories=categories, 
        states=states,
        selected_category=category,
        selected_state=state,
        query=query,
        eligibility_map=eligibility_map
    )


@schemes_bp.route('/<int:scheme_id>')
def detail(scheme_id):
    scheme = Scheme.query.get_or_404(scheme_id)
    
    eligibility = None
    if current_user.is_authenticated:
        eligibility = calculate_eligibility(current_user, scheme)
        
    return render_template(
        'scheme_detail.html', 
        scheme=scheme, 
        eligibility=eligibility
    )


@schemes_bp.route('/eligibility')
@login_required
def check_user_eligibility():
    schemes = Scheme.query.all()
    recs = get_recommendations(current_user, schemes)
    
    # Call Gemini Smart advisor AI Service for personalized instructions
    ai_service = AIService()
    ai_summary = ai_service.get_smart_recommendations(current_user, recs['eligible'])
    
    return render_template(
        'eligibility.html',
        eligible=recs['eligible'],
        partially_eligible=recs['partially_eligible'],
        ai_summary=ai_summary
    )
