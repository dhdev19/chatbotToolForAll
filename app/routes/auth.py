from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, make_response
from app.models import User
import hashlib
import random
import string
from app.utils.email_utils import send_otp_email
from functools import wraps

bp = Blueprint('auth', __name__)

def no_cache(view):
    @wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache_impl

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
@no_cache
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_email(email)
        if user and user['is_admin'] == False and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            session['email'] = user['email']
            session['full_name'] = user['full_name']
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password')
    return render_template('login.html')

@bp.route('/admin/login', methods=['GET', 'POST'])
@no_cache
def admin_login():
    if 'user_id' in session and session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_email(email)
        if user and user['is_admin'] and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
            session['user_id'] = user['id']
            session['is_admin'] = True
            session['email'] = user['email']
            session['full_name'] = user['full_name']
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials')
    return render_template('admin_login.html')

@bp.route('/register', methods=['GET', 'POST'])
@no_cache
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        whatsapp_number = request.form.get('whatsapp_number')
        business_name = request.form.get('business_name')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(full_name, email, password_hash, whatsapp_number, business_name)
        user.save()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@bp.route('/logout')
@no_cache
def logout():
    session.clear()
    response = make_response(redirect(url_for('main.home')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_by_email(email)
        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            session['otp'] = otp
            session['email'] = email
            send_otp_email(email, otp)
            return redirect(url_for('auth.verify_otp'))
        flash('Email not found')
    return render_template('forgot_password.html')

@bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp == session.get('otp'):
            return redirect(url_for('auth.reset_password'))
        flash('Invalid OTP')
    return render_template('verify_otp.html')

@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        password = request.form.get('password')
        email = session.get('email')
        user = User.get_by_email(email)
        if user:
            user['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
            user.save()
            session.pop('otp', None)
            session.pop('email', None)
            flash('Password reset successful. Please login.')
            return redirect(url_for('auth.login'))
    return render_template('reset_password.html') 