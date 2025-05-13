# Flask Chatbot Application

This is a Flask application that provides user authentication, payment processing, and a chatbot feature.

## Features

- User registration and login
- Forgot password with OTP verification
- Payment processing via Razorpay and PayPal
- Dashboard with chatbot and WhatsApp bot options
- View and add Q&A for the chatbot
- Embed code for the chatbot

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd chatbotAll
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Configure the database:
   - Create a MySQL database named `chatbot_db`
   - Update the database configuration in `app/models.py`

4. Configure email settings:
   - Update the email settings in `app/utils/email_utils.py`

5. Configure payment gateways:
   - Update Razorpay and PayPal credentials in `app/routes/payment.py`

6. Run the application:
   ```
   python run.py
   ```

## Usage

- Register a new user
- Login with the registered email and password
- Use the dashboard to manage chatbot Q&A and view embed code
- Process payments via Razorpay or PayPal 