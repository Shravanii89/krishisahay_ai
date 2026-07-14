from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        farmer_id = request.form.get('farmer_id', '').strip() or None
        age_str = request.form.get('age', '').strip()
        mobile_number = request.form.get('mobile_number', '').strip()
        email = request.form.get('email', '').strip() or None
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()
        village = request.form.get('village', '').strip()
        land_size_str = request.form.get('land_size', '').strip()
        crop_type = request.form.get('crop_type', '').strip()
        annual_income_str = request.form.get('annual_income', '').strip()
        category = request.form.get('category', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validation checks
        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        if not mobile_number or not re.match(r'^\+?[0-9]{10,15}$', mobile_number):
            errors.append("Please enter a valid mobile number.")
        if not age_str or not age_str.isdigit() or int(age_str) <= 0:
            errors.append("Please enter a valid age.")
        if not state or not district or not village:
            errors.append("State, District, and Village fields are required.")
        if not category:
            errors.append("Category is required.")
        if not land_size_str:
            errors.append("Land size is required.")
        else:
            try:
                land_size = float(land_size_str)
                if land_size < 0:
                    errors.append("Land size cannot be negative.")
            except ValueError:
                errors.append("Land size must be a number.")
                
        if not annual_income_str:
            errors.append("Annual income is required.")
        else:
            try:
                annual_income = float(annual_income_str)
                if annual_income < 0:
                    errors.append("Annual income cannot be negative.")
            except ValueError:
                errors.append("Annual income must be a number.")
                
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
            
        # Check if mobile already exists
        existing_mobile = User.query.filter_by(mobile_number=mobile_number).first()
        if existing_mobile:
            errors.append("A farmer with this mobile number is already registered.")
            
        if farmer_id:
            existing_fid = User.query.filter_by(farmer_id=farmer_id).first()
            if existing_fid:
                errors.append("This Farmer ID is already registered.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html')
            
        # Create User
        # Username will be the mobile number (farmer-friendly)
        new_user = User(
            username=mobile_number,
            full_name=full_name,
            farmer_id=farmer_id,
            age=int(age_str),
            mobile_number=mobile_number,
            email=email,
            state=state,
            district=district,
            village=village,
            land_size=float(land_size_str),
            crop_type=crop_type,
            annual_income=float(annual_income_str),
            category=category
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! You can now log in using your Mobile Number.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        mobile_number = request.form.get('mobile_number', '').strip()
        password = request.form.get('password', '').strip()
        
        if not mobile_number or not password:
            flash("Please fill in all fields.", "danger")
            return render_template('login.html')
            
        # Usernames are stored as mobile numbers
        user = User.query.filter_by(username=mobile_number).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            # Redirect to next parameter if present
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash("Invalid mobile number or password.", "danger")
            
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.", "info")
    return redirect(url_for('dashboard.landing'))
