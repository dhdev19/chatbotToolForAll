import mysql.connector
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# MySQL connection configuration
db_config = {
    'host': os.getenv('HOST'),
    #'port': os.getenv('DB_PORT'),
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD'),
    'database': os.getenv('DATABASE')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

class User:
    def __init__(self, full_name, email, password_hash, whatsapp_number, business_name, WelcomeMessage, secret_key=None, is_admin=False, id=None):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.whatsapp_number = whatsapp_number
        self.business_name = business_name
        self.secret_key = secret_key or str(uuid.uuid4())
        self.is_admin = is_admin
        self.WelcomeMessage = WelcomeMessage
        self.created_at = datetime.utcnow()

    @staticmethod
    def create_table():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100),
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128),
                whatsapp_number VARCHAR(20),
                business_name VARCHAR(100),
                secret_key VARCHAR(64) UNIQUE,
                WelcomeMessage TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at DATETIME
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (full_name, email, password_hash, whatsapp_number, business_name, WelcomeMessage, secret_key, is_admin, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (self.full_name, self.email, self.password_hash, self.whatsapp_number, self.business_name, self.WelcomeMessage, self.secret_key, self.is_admin, self.created_at))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    @staticmethod
    def get_all_users():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users

    def delete(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (self.id,))
        conn.commit()
        cursor.close()
        conn.close()
        
    def update_visitor_count(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET visitor_count = COALESCE(visitor_count, 0) + 1
            WHERE id = %s
        ''', (self.id,))
        conn.commit()
        cursor.close()
        conn.close()
        
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return User(
                id=row['id'],
                full_name=row['full_name'],
                email=row['email'],
                password_hash=row['password_hash'],
                whatsapp_number=row['whatsapp_number'],
                business_name=row['business_name'],
                WelcomeMessage=row['WelcomeMessage'],
                secret_key=row['secret_key'],
                is_admin=row['is_admin'],
                #created_at=row['created_at']
            )
        return None
    # @staticmethod
    # def get_by_id(user_id):
    #     conn = get_db_connection()
    #     cursor = conn.cursor(dictionary=True)
    #     cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    #     user = cursor.fetchone()
    #     cursor.close()
    #     conn.close()
    #     return user


class QuestionAnswer:
    def __init__(self, question, answer, user_id):
        self.question = question
        self.answer = answer
        self.user_id = user_id

    @staticmethod
    def create_table():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_answers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO question_answers (question, answer, user_id)
            VALUES (%s, %s, %s)
        ''', (self.question, self.answer, self.user_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM question_answers WHERE user_id = %s', (user_id,))
        qa_list = cursor.fetchall()
        cursor.close()
        conn.close()
        return qa_list

    @staticmethod
    def get_by_id(qa_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM question_answers WHERE id = %s', (qa_id,))
        qa = cursor.fetchone()
        cursor.close()
        conn.close()
        return qa

    @staticmethod
    def update(qa_id, question, answer):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE question_answers 
            SET question = %s, answer = %s 
            WHERE id = %s
        ''', (question, answer, qa_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def delete(qa_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM question_answers WHERE id = %s', (qa_id,))
        conn.commit()
        cursor.close()
        conn.close() 
