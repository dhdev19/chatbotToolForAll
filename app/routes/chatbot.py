
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from app.models import QuestionAnswer, User
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
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        user_id = session['user_id']
        qa = QuestionAnswer(question, answer, user_id)
        qa.save()
        flash('Q&A added successfully!')
        return redirect(url_for('chatbot.view_qa'))
    return render_template('add_qa.html')


@bp.route('/chatbot/view_qa')
@login_required
def view_qa():
    user_id = session['user_id']
    qa_list = QuestionAnswer.get_by_user_id(user_id)
    return render_template('view_qa.html', qa_list=qa_list)


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

        if not user_input or not user_id:
            return jsonify({'response': 'Please provide both query and user_id.'}), 400

        qa_list = QuestionAnswer.get_by_user_id(user_id)
        if not qa_list:
            return jsonify({'response': 'No Q&A data found for this user.'}), 404

        user = User.get_by_id(user_id)
        context = '\n'.join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_list])
        context + = f'Q: Contact information\nA: <a href="https://wa.me/{ user.whatsapp_number }" target="_blank">Whatsapp</a> and <a href="mailto:{ user.email }?subject=Hello&body=Message%20content" target="_blank">Email</a>'

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
