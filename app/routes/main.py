
from flask import Blueprint, render_template, redirect

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    # return render_template('home.html')
    return redirect("https://digitalhomeez.in/", code=302)
