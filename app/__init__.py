from flask import Flask
from app.models import User, QuestionAnswer, Projects
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CHATBOT_API_URL'] = os.getenv('CHATBOT_API_URL')
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize database tables
with app.app_context():
    User.create_table()
    QuestionAnswer.create_table()
    Projects.create_table()

from app.routes import auth, dashboard, chatbot, main, admin

app.register_blueprint(auth.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(chatbot.bp)
app.register_blueprint(main.bp)
app.register_blueprint(admin.bp)
