from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, User, Scheme, DocumentUpload

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def dashboard():
    # Simple check: let's assume first registered farmer is admin, or keep it open for demonstration
    # In production, check an admin flag or role.
    farmers_count = User.query.count()
    schemes_count = Scheme.query.count()
    uploads_count = DocumentUpload.query.count()
    
    recent_farmers = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_uploads = DocumentUpload.query.order_by(DocumentUpload.uploaded_at.desc()).limit(5).all()
    
    return render_template(
        'admin.html',
        farmers_count=farmers_count,
        schemes_count=schemes_count,
        uploads_count=uploads_count,
        recent_farmers=recent_farmers,
        recent_uploads=recent_uploads
    )


@admin_bp.route('/schemes/add', methods=['GET', 'POST'])
@login_required
def add_scheme():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        target_category = request.form.get('target_category', '').strip() or 'All'
        state_specific = request.form.get('state_specific', '').strip() or 'All'
        min_age = request.form.get('min_age', '0').strip()
        max_land_size = request.form.get('max_land_size', '').strip()
        max_income = request.form.get('max_income', '').strip()
        required_crops = request.form.get('required_crops', '').strip()
        benefits = request.form.get('benefits', '').strip()
        required_documents = request.form.get('required_documents', '').strip()
        application_steps = request.form.get('application_steps', '').strip()
        official_link = request.form.get('official_link', '').strip()
        
        errors = []
        if not name:
            errors.append("Scheme name is required.")
        if not description:
            errors.append("Scheme description is required.")
        if not category:
            errors.append("Category is required.")
            
        existing = Scheme.query.filter_by(name=name).first()
        if existing:
            errors.append("A scheme with this name already exists.")
            
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('admin_add_scheme.html')
            
        # Parse numeric inputs safely
        min_age_int = int(min_age) if min_age.isdigit() else 0
        max_land = float(max_land_size) if max_land_size else None
        max_inc = float(max_income) if max_income else None
        
        new_scheme = Scheme(
            name=name,
            description=description,
            category=category,
            target_category=target_category,
            state_specific=state_specific,
            min_age=min_age_int,
            max_land_size=max_land,
            max_income=max_inc,
            required_crops=required_crops,
            benefits=benefits,
            required_documents=required_documents,
            application_steps=application_steps,
            official_link=official_link
        )
        
        try:
            db.session.add(new_scheme)
            db.session.commit()
            flash("Scheme added successfully!", "success")
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding scheme: {str(e)}", "danger")
            
    return render_template('admin_add_scheme.html')
