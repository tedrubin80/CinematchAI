# auth.py - Authentication system for Cinematch

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import secrets
import json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

def get_limiter():
    """Get the limiter from the app context"""
    from app import limiter
    return limiter

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username')  # Can be username or email
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Import here to avoid circular imports
        from models import User, db
        
        # Support login with both username and email
        user = User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # Log successful login
            user.last_login = datetime.utcnow()
            from models import db
            db.session.commit()
            
            # Redirect based on user role
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            # If user is admin, go to admin subscription dashboard
            if user.is_admin:
                # Get the secret admin path from config
                from flask import current_app
                admin_path = current_app.config.get('ADMIN_SECRET_PATH', 'admin')
                return redirect(f'/{admin_path}/subscription/')
            else:
                # Regular users go back to homepage
                return redirect(url_for('index'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/google/callback', methods=['POST'])
def google_callback():
    """Handle Google Sign-In callback"""
    try:
        # Get the token from the request
        data = request.get_json()
        token = data.get('token')
        email = data.get('email')
        name = data.get('name')
        picture = data.get('picture')
        
        # Verify the token with Google (use environment variable)
        CLIENT_ID = current_app.config.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_CLIENT_ID')

        if not CLIENT_ID:
            current_app.logger.error("GOOGLE_CLIENT_ID not configured")
            return jsonify({
                'success': False,
                'message': 'Google authentication not configured'
            }), 500

        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                CLIENT_ID
            )
            
            # Token is valid, get user info
            google_email = idinfo.get('email')
            google_name = idinfo.get('name', email.split('@')[0])
            
            # Import here to avoid circular imports
            from models import User, db
            
            # Check if user exists
            user = User.query.filter_by(email=google_email).first()
            
            if not user:
                # Create new user
                username = google_email.split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User(
                    username=username,
                    email=google_email,
                    password_hash=generate_password_hash(secrets.token_urlsafe(32)),  # Random password
                    is_admin=False,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
            
            # Log the user in
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Determine redirect based on user role
            if user.is_admin:
                redirect_url = url_for('admin.dashboard')
            else:
                redirect_url = url_for('index')
            
            return jsonify({
                'success': True,
                'redirect': redirect_url,
                'message': 'Login successful'
            })
            
        except ValueError as e:
            # Invalid token
            return jsonify({
                'success': False,
                'message': 'Invalid Google token'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page (can be disabled in production)"""
    # Check if registration is allowed
    from flask import current_app
    if not current_app.config.get('ALLOW_REGISTRATION', False):
        flash('Registration is currently disabled.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        from models import User, db
        
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        birth_date_str = request.form.get('birthdate')
        parental_email = request.form.get('parental_email')
        parental_consent = request.form.get('parental_consent') == 'on'
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if not password or len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Age validation
        birth_date = None
        if birth_date_str:
            try:
                from datetime import datetime, date
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                
                # Calculate age
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                
                if age < 13:
                    if not parental_consent or not parental_email:
                        errors.append('Users under 13 require parental consent and parental email address.')
                elif age < 18:
                    if not parental_consent:
                        errors.append('Users under 18 require parental consent for payments.')
                
                if age > 120 or age < 5:
                    errors.append('Please enter a valid birth date.')
                    
            except ValueError:
                errors.append('Please enter a valid birth date (YYYY-MM-DD).')
        else:
            errors.append('Birth date is required for age verification.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            # Create new user
            user = User(
                username=username,
                email=email,
                birth_date=birth_date,
                parental_consent=parental_consent,
                parental_email=parental_email if parental_consent else None,
                age_verification_date=datetime.utcnow(),
                is_admin=False  # Regular user by default
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        from models import User
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            
            from models import db
            db.session.commit()
            
            # In production, send email with reset link
            # For demo, just show the token
            flash(f'Password reset link: /reset-password/{token}', 'info')
        else:
            # Don't reveal if email exists
            flash('If the email exists, a reset link has been sent.', 'info')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    from models import User, db
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
        else:
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            
            flash('Password reset successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

# Session security
@auth_bp.before_app_request
def session_security():
    """Add security checks for each request"""
    # Set session timeout (30 minutes)
    session.permanent = True
    from flask import current_app
    current_app.permanent_session_lifetime = timedelta(minutes=30)
    
    # Regenerate session ID periodically
    if 'session_regenerated' not in session:
        session['session_regenerated'] = datetime.utcnow().isoformat()
    else:
        try:
            last_regenerated = datetime.fromisoformat(session['session_regenerated'])
            if datetime.utcnow() - last_regenerated > timedelta(minutes=15):
                # Note: session.regenerate() is not a standard Flask feature
                # We'll just update the timestamp for now
                session['session_regenerated'] = datetime.utcnow().isoformat()
        except (ValueError, TypeError):
            # If there's an issue with the stored datetime, reset it
            session['session_regenerated'] = datetime.utcnow().isoformat()
