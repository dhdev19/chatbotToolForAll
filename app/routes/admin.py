from flask import Blueprint, request, render_template, redirect, url_for, session, flash, jsonify
from app.models import User, Projects
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
    users = User.get_all_users_with_project_count()
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
def show_sales():
    users = User.get_all_users_with_project_count()
    return render_template('show_sales.html', users=users)

@bp.route('/admin/approveProject')
@admin_required
def approve_project():
    project_id = request.args.get('project_id')
    
    if not project_id:
        flash("Project ID is required.", "danger")
        return redirect(url_for('chatbot.show_users'))

    try:
        project_id = int(project_id)
        Project.update_project_status(project_id)
        flash("Project approved successfully!", "success")
    except ValueError:
        flash("Invalid Project ID.", "danger")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
    
    return redirect(url_for('chatbot.show_users'))

@bp.route('/admin/getUserProjects')
@admin_required
def get_user_projects():
    user_id = request.args.get('user_id', type=int)
    projects = Projects.get_all_projects(user_id)
    return jsonify(projects)

@bp.route('/admin/revokeProject')
@admin_required
def revoke_project():
    pid = request.args.get('project_id', type=int)
    Projects.update_project_status(pid, approved=False)
    return ('', 204)



@bp.route('/admin/increase_count', methods=['POST'])
def increase_count():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID missing'}), 400

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.update_visitor_count()

    return jsonify({'message': 'Visitor count increased'}), 200
