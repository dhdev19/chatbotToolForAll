from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app.models import User
import hashlib
from app.routes.auth import admin_required
from dotenv import load_dotenv
import os
bp = Blueprint('admin', __name__)

@bp.route('/admin/dashboard')
@admin_required
def dashboard():
    user = User.get_by_id(session['user_id'])
    return render_template('admin_dashboard.html', user=user)

@bp.route('/admin/users')
@admin_required
def show_users():
    users = User.get_all_users()
    return render_template('show_users.html', users=users, chatbot_api_url=os.getenv('CHATBOT_API_URL'))

@bp.route('/admin/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        whatsapp_number = request.form.get('whatsapp_number')
        business_name = request.form.get('business_name')
        WelcomeMessage = request.form.get('WelcomeMessage')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(full_name, email, password_hash, whatsapp_number, business_name, WelcomeMessage)
        new_user.save()
        flash('User added successfully')
        return redirect(url_for('admin.dashboard'))
    return render_template('add_user.html') 


@bp.route('/admin/deleteuser', methods=['POST'])
@admin_required
def delete_user():
    user_id = request.form.get('user_id')
    if user_id:
        user = User.get_by_id(user_id)
        if user:
            user.delete()  # Assuming your User model has a .delete() method
            flash('User deleted successfully')
        else:
            flash('User not found')
    else:
        flash('No user ID provided')
    return redirect(url_for('admin.show_users'))


@bp.route('/admin/sales')
@admin_required
def show_users():
    users = User.get_all_users()
    return render_template('show_sales.html', users=users)

