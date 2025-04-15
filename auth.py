from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlparse
from app import db
from models import User, FarmerProfile, CompanyProfile
from forms import LoginForm, RegistrationForm, FarmerProfileForm, CompanyProfileForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        if current_user.is_farmer():
            return redirect(url_for('farmer.dashboard'))
        else:
            return redirect(url_for('company.dashboard'))
    return render_template('landing.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_farmer():
            return redirect(url_for('farmer.dashboard'))
        else:
            return redirect(url_for('company.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_farmer():
                next_page = url_for('farmer.dashboard')
            else:
                next_page = url_for('company.dashboard')
        return redirect(next_page)
    
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.is_farmer():
            return redirect(url_for('farmer.dashboard'))
        else:
            return redirect(url_for('company.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create the appropriate profile based on user role
        if user.is_farmer():
            profile = FarmerProfile(user_id=user.id, farm_name=f"{user.username}'s Farm")
            db.session.add(profile)
        else:
            profile = CompanyProfile(user_id=user.id, company_name=f"{user.username}'s Company")
            db.session.add(profile)
        
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.is_farmer():
        form = FarmerProfileForm()
        profile = current_user.farmer_profile
        
        if request.method == 'GET':
            form.farm_name.data = profile.farm_name
            form.address.data = profile.address
            form.phone.data = profile.phone
            form.bio.data = profile.bio
        
        if form.validate_on_submit():
            profile.farm_name = form.farm_name.data
            profile.address = form.address.data
            profile.phone = form.phone.data
            profile.bio = form.bio.data
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('farmer.dashboard'))
        
        return render_template('farmer/profile.html', form=form)
    
    else:  # Company
        form = CompanyProfileForm()
        profile = current_user.company_profile
        
        if request.method == 'GET':
            form.company_name.data = profile.company_name
            form.industry_type.data = profile.industry_type
            form.address.data = profile.address
            form.phone.data = profile.phone
            form.description.data = profile.description
        
        if form.validate_on_submit():
            profile.company_name = form.company_name.data
            profile.industry_type = form.industry_type.data
            profile.address = form.address.data
            profile.phone = form.phone.data
            profile.description = form.description.data
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('company.dashboard'))
        
        return render_template('company/profile.html', form=form)
