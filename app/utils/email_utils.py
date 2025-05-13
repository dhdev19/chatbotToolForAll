from flask_mail import Mail, Message
from app import app

mail = Mail(app)

def send_otp_email(email, otp):
    msg = Message('Your OTP for Password Reset', sender='your-email@example.com', recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    mail.send(msg) 