from flask import Blueprint, render_template, redirect, url_for, session
from app.models import User, QuestionAnswer
from app.routes.auth import login_required

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    user = User.get_by_id(session['user_id'])
    return render_template('dashboard.html', user=user)

@bp.route('/profile')
@login_required
def profile():
    user = User.get_by_id(session['user_id'])
    return render_template('profile.html', user=user)

@bp.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@bp.route('/chatbot/qa')
@login_required
def view_qa():
    return render_template('view_qa.html')

