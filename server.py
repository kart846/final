from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_mail import Mail, Message
import logging
import pymysql
import mysql.connector

app = Flask(__name__)
# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # Use your email provider's SMTP
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False 
app.config["MAIL_USERNAME"] = "karthickmadasamy7@gmail.com"  # Your email
app.config["MAIL_PASSWORD"] = "kqho easx cfrm rlbj"  # Your email app password
# app.config["MAIL_DEFAULT_SENDER"] = "karthickmadasamy7@gmail.com"  # Optional, default sender address

mail = Mail(app)
CORS(app)

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password="Karthick@24",
    database = "user_management"
    
)
cursor = db.cursor(dictionary=True)

#create table if not exists
cursor.execute('''
                CREATE TABLE IF NOT EXISTS users(
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   role VARCHAR(50) NOT NULL,
                   user_id VARCHAR(50) UNIQUE NOT NULL,
                   username VARCHAR(100) UNIQUE NOT NULL,
                   email VARCHAR(100) UNIQUE NOT NULL,
                   password VARCHAR(100) NOT NULL
                   )
                   ''')
db.commit()

@app.route("/users", methods=['GET'])
def get_users():
    cursor.execute("SELECT role, user_id, username, email FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route("/add_user", methods=['POST'])
def add_user():
    data = request.json
    if not all(key in data for key in ['role', 'id', 'username', 'email', 'password']):
      return jsonify({"error": "Missing fields in request"}), 400
    role = data['role']
    user_id = data['id']
    username = data["username"]
    email = data["email"]
    password = data["password"]
    
    cursor.execute("INSERT INTO users (role, user_id, username, email, password) VALUES (%s, %s, %s, %s, %s)",
                   (role, user_id, username, email, password)
                   )
    db.commit()
    
    return jsonify({"message": "User added successfully"}),201

# dummy baba

@app.route('/get_available_ids', methods=['GET'])
def get_available_ids():
    role = request.args.get('role')  # Get role from query parameters
    if not role:
        return jsonify([])  # Return empty list if no role is selected


    cursor.execute("SELECT user_id FROM users WHERE role=%s", (role,))
    used_ids = [row['user_id'] for row in cursor.fetchall()]
    available_ids = [f"{role}{i}" for i in range(1, 4) if f"{role}{i}" not in used_ids]  # Assume IDs are in the form ASM1, RSM1, STORE1, etc.

    return jsonify(available_ids)
# dummy end

# delete a user
@app.route("/delete_user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        db.commit()
        rows_affected = cursor.rowcount  # Number of rows deleted

        if rows_affected == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/update_user/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")  # Get password (if provided)

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    print(f"Received Data: {data}")  # Debugging

    query = "UPDATE users SET username=%s, email=%s WHERE user_id=%s"
    values = [username, email, user_id]

    if password and password.strip() != "":  # If password is provided
        query = "UPDATE users SET username=%s, email=%s, password=%s WHERE user_id=%s"
        values = [username, email, password, user_id]

    print(f"Executing Query: {query}")  # Debugging
    print(f"With Values: {values}")  # Debugging

    cursor.execute(query, values)
    db.commit()

    return jsonify({"message": "User updated successfully"}), 200


# email send password
logging.basicConfig(level=logging.DEBUG)
@app.route("/emailsend/<user_id>", methods=["PUT", "POST", "GET"])
def sendemail(user_id):
    data = request.json
    email = data.get("email")
    new_password = data.get("password", None)  # Password is optional

    try:
        # Fetch existing email if not provided
        if not email:
            cursor.execute("SELECT email FROM users WHERE user_id=%s", (user_id,))
            user = cursor.fetchone()
            if user:
                email = user[0]  # Get existing email from DB

        # Update email
        if email:
            cursor.execute("UPDATE users SET email=%s WHERE user_id=%s", (email, user_id))

        # If password is provided, update and commit
        if new_password:
            cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (new_password, user_id))
            db.commit()
            print(" Password Updated in Database")
            # Send Password Reset Email
            if email:
                print(f"📧 Sending Email To: {email}")  # Debugging
                subject = "Password Reset Successful"
                message_body = f"""
                Hello,

                Your password has been successfully reset.

                **New Password:** {new_password}

                Please change it after logging in for security reasons.

                Regards,
                Admin Team
                """
                print("📜 Email Body:", message_body)  # Debugging
                msg = Message(subject, sender="karthickmadasamy7@gmail.com", recipients=[email])
                msg.body = message_body
                mail.send(msg)
                
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        logging.error(f"Error updating user {user_id}: {e}")
        return jsonify({"error": "Something went wrong. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    
