import os
from flask import Flask, render_template, request, redirect, url_for, session
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY'].encode()
fernet = Fernet(ENCRYPTION_KEY)

USERS = {}
NOTES = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS:
            return 'User already exists!', 400
        USERS[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid login', 401
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    user_ip = request.remote_addr
    if request.method == 'POST':
        note = request.form['note']
        enc_note = fernet.encrypt(note.encode()).decode()
        NOTES.setdefault(username, []).append(enc_note)
    enc_notes = NOTES.get(username, [])
    notes = [fernet.decrypt(n.encode()).decode() for n in enc_notes]
    return render_template('dashboard.html', username=username, user_ip=user_ip, notes=notes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
