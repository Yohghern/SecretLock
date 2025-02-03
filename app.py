from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from cryptography.fernet import Fernet
import os
import time

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Progress tracking
progress = {"status": 0}


# Generate a key based on a password
def generate_key(password):
    return Fernet(Fernet.generate_key())


# Encrypt a file
def encrypt_file(file_path, password):
    fernet = generate_key(password)
    with open(file_path, "rb") as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)
    with open(file_path, "wb") as file:
        file.write(encrypted_data)


# Decrypt a file
def decrypt_file(file_path, password):
    fernet = generate_key(password)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data)
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

    if action == "encrypt":
        encrypt_file(file_path, password)
        flash("File encrypted successfully!", "success")
    elif action == "decrypt":
        decrypt_file(file_path, password)
        flash("File decrypted successfully!", "success")

    return send_file(file_path, as_attachment=True)


@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
