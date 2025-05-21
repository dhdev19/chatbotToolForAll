
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    # return render_template('home.html')
    return redirect("https://dhgenixmedia.ae/", code=302)
