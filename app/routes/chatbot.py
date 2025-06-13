
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from app.models import QuestionAnswer, User, Projects
from app.routes.auth import login_required
import os
from dotenv import load_dotenv
import google.generativeai as genai
from flask_cors import cross_origin

bp = Blueprint('chatbot', __name__)

# Load environment variables
load_dotenv()

# Configure Gemini with API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
chatbot_api_url = os.getenv('CHATBOT_API_URL')


try:
    print("Attempting to configure Gemini...")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set in environment variables")

    genai.configure(api_key=api_key)
    print("Gemini configured successfully")

    print("Attempting to create model...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Model created successfully")

    print("Attempting to start chat...")
    chat = model.start_chat(history=[])
    print("Chat started successfully")

except Exception as e:
    print(f"Error initializing AI model: {e}")
    chat = None



@bp.route('/chatbot/add_qa', methods=['GET', 'POST'])
@login_required
def add_qa():
    user_id = session['user_id']
    project_list = Projects.get_all_approved_projects(user_id)

    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        project_id = request.form.get('project_id')

        if not project_id:
            flash('Please select a project.', 'danger')
            return redirect(url_for('chatbot.add_qa'))

        qa = QuestionAnswer(question, answer, user_id, project_id=project_id)
        qa.save()
        flash('Q&A added successfully!', 'success')
        return redirect(url_for('chatbot.view_qa'))

    return render_template('add_qa.html', project_list=project_list)



@bp.route('/chatbot/projects', methods=['GET', 'POST'])
@login_required
def projects():
    user_id = session['user_id']
    projects = Projects.get_all_projects(user_id)
    return render_template('projects.html', projects=projects, chatbot_api_url=chatbot_api_url)

@bp.route("/chatbot/embed")
def embed_chatbot():
    project_id = request.args.get("project_id")
    user_id = request.args.get("user_id")

    if not project_id or not user_id:
        return "Missing project_id or user_id", 400
    project = Projects.get_project(user_id, project_id)
    return render_template('embed-chatbot.html', project=project, chatbot_api_url=chatbot_api_url)



@bp.route('/chatbot/delete_project<int:project_id>', methods=['GET', 'POST'])
@login_required
def delete_project(project_id):
    user_id = session['user_id']
    projects = Projects.delete(project_id)
    flash('Project deleted successfully')
    return redirect(url_for('chatbot.projects'))

@bp.route('/chatbot/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    project_name = request.form.get('project')
    if not project_name:
        flash('Project name is required.', 'danger')
        return redirect(url_for('chatbot.projects'))
    project = Projects(user_id=session['user_id'], project=project_name)
    try:
        project.save()
        flash('Project added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding project: {str(e)}', 'danger')

    return redirect(url_for('chatbot.projects'))
    
@bp.route('/chatbot/view_qa')
@login_required
def view_qa():
    user_id = session['user_id']
    project_id = request.args.get('project_id')
    if project_id:
        qa_list = QuestionAnswer.get_by_user_id_and_project_id(user_id, project_id)
    else:
        qa_list = QuestionAnswer.get_by_user_id(user_id)
    project_list = Projects.get_all_projects(user_id)
    return render_template('view_qa.html', qa_list=qa_list, project_list=project_list)


@bp.route('/chatbot/edit_qa/<int:qa_id>', methods=['GET', 'POST'])
@login_required
def edit_qa(qa_id):
    qa = QuestionAnswer.get_by_id(qa_id)
    if not qa or qa['user_id'] != session['user_id']:
        flash('Q&A not found or unauthorized access')
        return redirect(url_for('chatbot.view_qa'))

    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        QuestionAnswer.update(qa_id, question, answer)
        flash('Q&A updated successfully!')
        return redirect(url_for('chatbot.view_qa'))

    return render_template('edit_qa.html', qa=qa)


@bp.route('/chatbot/delete_qa/<int:qa_id>', methods=['POST'])
@login_required
def delete_qa(qa_id):
    qa = QuestionAnswer.get_by_id(qa_id)
    if not qa or qa['user_id'] != session['user_id']:
        flash('Q&A not found or unauthorized access')
        return redirect(url_for('chatbot.view_qa'))

    QuestionAnswer.delete(qa_id)
    flash('Q&A deleted successfully!')
    return redirect(url_for('chatbot.view_qa'))


@bp.route('/chatbot/endpoint', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['*'], methods=['POST', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])
def chatbot_endpoint():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json
        user_input = data.get('query')
        user_id = data.get('user_id')
        project_id = data.get('project_id')

        if not user_input or not user_id:
            return jsonify({'response': 'Please provide both query and user_id.'}), 400

        qa_list = QuestionAnswer.get_by_project_id(project_id)
        if not qa_list:
            return jsonify({'response': 'No Q&A data found for this user.'}), 404

        user = User.get_by_id(user_id)
        context = '\n'.join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_list])
        context += f'Q: Contact information\nA: <a href="https://wa.me/{ user.whatsapp_number }" target="_blank">Whatsapp</a> and <a href="mailto:{ user.email }?subject=Hello&body=Message%20content" target="_blank">Email</a>'

        prompt = f"""Your name is Alvi, you are a chatbot assistant. Keep your tone friendly and professional. Answer questions based on the following data and make sure to limit your response to the data provided and in 50 words.If you are not sure about the answer, pass the contact information and say "I'm sorry, I don't have information about that. Please contact us directly for more information":

Q&A Data:
{context}

Query: {user_input}

Answer:"""

        if not chat:
            print("Chat is not initialized")
            return jsonify({'response': 'Sorry, the chat service is currently unavailable. Please try again later.'}), 503

        print("Sending message to Gemini...")
        response = chat.send_message(prompt)
        print("Received response from Gemini")
        return jsonify({'response': response.text})

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': 'Sorry, an error occurred. Please try again later.'}), 500




@bp.route('/edit-whatsapp-message', methods=['POST'])
@login_required
def edit_whatsapp_message():
    message = request.form['whatsapp_message']
    User.update_whatsapp_message(session['user_id'], message)
    flash("WhatsApp message updated successfully", "success")
    return redirect(url_for('dashboard.profile'))

@bp.route('/edit-offers', methods=['POST'])
@login_required
def edit_offers():
    offers = request.form['offers']
    User.update_offers(session['user_id'], offers)
    flash("Offers updated successfully", "success")
    return redirect(url_for('dashboard.profile'))

@bp.route('/edit-popup-text', methods=['POST'])
@login_required
def edit_popup_text():
    popup_text = request.form['popup_text']
    User.update_popup_text(session['user_id'], popup_text)
    flash("Popup text updated successfully", "success")
    return redirect(url_for('dashboard.profile'))


@bp.route('/chatbot/get-live-info', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['*'], methods=['POST', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])
def get_info():
    if request.method == 'OPTIONS':
        return '', 200  # ✅ Handle preflight

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id not provided'}), 400

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'offers': user.offers,
        'whatsapp_message': user.whatsapp_message,
        'popup_text': user.popup_text
    })
