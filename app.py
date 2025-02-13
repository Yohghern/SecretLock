import base64
import hashlib
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from cryptography.fernet import Fernet
import os
import time

app = Flask(__name__)
app.secret_key = "supersecretkey"


progress = {"status": 0}


def generate_key(password):
    password_bytes = password.encode()  
    key = hashlib.sha256(password_bytes).digest()[:32]  
    return base64.urlsafe_b64encode(key)


def encrypt_file(file_path, password):
    key = generate_key(password)  
    fernet = Fernet(key)

    with open(file_path, "rb") as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    with open(file_path, "wb") as file:
        file.write(encrypted_data)


def decrypt_file(file_path, password):
    key = generate_key(password)  
    fernet = Fernet(key)

    print(f"🔑 Decryption Key: {key}")  

    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"❌ Decryption failed: {e}")  
        raise

    with open(file_path, "wb") as file:
        file.write(decrypted_data)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    password = request.form["password"]
    action = request.form["action"]

    if not file or not password:
        flash("File and password are required!", "danger")
        return redirect(url_for("index"))

    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    progress["status"] = 0
    for i in range(1, 101):
        time.sleep(0.01)
        progress["status"] = i

    try:
        if action == "encrypt":
            encrypt_file(file_path, password)
            flash("File encrypted successfully!", "success")
        elif action == "decrypt":
            try:
                decrypt_file(file_path, password)
                flash("File decrypted successfully!", "success")
            except Exception as e:
                flash(f"Decryption failed: {str(e)}", "danger")
                return redirect(url_for("index"))

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("index"))

@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
