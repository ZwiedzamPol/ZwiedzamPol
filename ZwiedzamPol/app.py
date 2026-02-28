from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- DB INIT ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            points INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS trails(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/profile')
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            return "Użytkownik już istnieje!"
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect('/profile')
        return "Niepoprawne dane!"
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, points FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    c.execute("SELECT * FROM trails WHERE user_id=?", (user_id,))
    trails = c.fetchall()
    conn.close()
    return render_template('profile.html', user=user, trails=trails)

@app.route('/add_trail', methods=['POST'])
def add_trail():
    if 'user_id' not in session:
        return redirect('/login')
    name = request.form['name']
    description = request.form['description']
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])
    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO trails (user_id, name, description, latitude, longitude) VALUES (?,?,?,?,?)",
              (user_id, name, description, latitude, longitude))
    c.execute("UPDATE users SET points = points + 10 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/profile')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/regulamin')
def regulamin():
    return render_template('regulamin.html')

if __name__ == '__main__':
    app.run(debug=True)