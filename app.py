from flask import Flask, request, jsonify, render_template, redirect, session
import sqlite3
from datetime import datetime
from urllib.parse import urlparse

# ML imports
from utils.url_analyzer import extract_features
from models.phishing_model import predict_url

app = Flask(__name__, template_folder='frontend', static_folder='frontend')
app.secret_key = "secret123"

# ---------------- DATABASE ---------------- #

def get_db():
    return sqlite3.connect("database.db")


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input TEXT,
        type TEXT,
        risk_score INTEGER,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template("login.html")


@app.route('/user')
def user_dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template("user_dashboard.html")


@app.route('/admin')
def admin_dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template("admin_dashboard.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()

    if username == "admin" and password == "admin123":
        session['user'] = username
        session['role'] = "admin"
        conn.close()
        return jsonify({"redirect": "/admin"})

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "user")
        )
        conn.commit()

    session['user'] = username
    session['role'] = "user"

    conn.close()
    return jsonify({"redirect": "/user"})


# ---------------- SCAN API ---------------- #

@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"risk_score": 0})

        input_text = data.get('input', "").lower()

        # add this
        if not input_text.startswith("http"):

          input_text = "http://" + input_text


        trusted_domains = [
            "google.com", 
            "facebook.com", 
            "twitter.com", 
            "linkedin.com",
            "github.com",
            "amazon.com",
            "microsoft.com",
            "apple.com",
            "yahoo.com",
            "wikipedia.org",
            "instagram.com",
            "netflix.com",
            "paypal.com",
            "dropbox.com",
            "stackoverflow.com",
            "quora.com",
            "reddit.com",
            "tumblr.com",
            "spotify.com",
            "adobe.com",
            "salesforce.com",
            "slack.com",
            "zoom.us",
            "wordpress.com",
            "bing.com",
            "yandex.com",
            "duckduckgo.com",
            "ebay.com",
            "etsy.com",
            "airbnb.com",
            "uber.com",
            "lyft.com",
            "stripe.com",
            "squareup.com",
            "cloudflare.com",
            "akamai.com",
            "cloudfront.net",
            "youtube.com"
        ]

        # -------- FIXED DOMAIN CHECK -------- #
        parsed = urlparse(input_text)
        domain = parsed.netloc.replace("www.", "")

        if domain in trusted_domains:
            return jsonify({"risk_score": 0})

        # -------- FEATURE EXTRACTION -------- #
        features = extract_features(input_text)

        # -------- ML PREDICTION -------- #
        prediction = predict_url(features)

        # convert to percentage
        score = int(prediction * 100)

        print("Features:", features)
        print("Prediction:", prediction)
        print("Score:", score)

        # -------- SAVE TO DB -------- #
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO scans (input, type, risk_score, timestamp) VALUES (?, ?, ?, ?)",
            (input_text, "url", score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()
        conn.close()

        return jsonify({"risk_score": score})

    except Exception as e:
        print("SCAN ERROR:", e)
        return jsonify({"risk_score": 0})


# ---------------- ADMIN APIs ---------------- #

@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username, role FROM users")
    users = cursor.fetchall()

    conn.close()

    return jsonify([
        {"username": u[0], "role": u[1]} for u in users
    ])


@app.route('/api/scans')
def get_scans():
    try:
        if 'user' not in session:
            return jsonify({"error": "Unauthorized"}), 403

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT input, type, risk_score, timestamp 
        FROM scans ORDER BY timestamp DESC
        """)

        scans = cursor.fetchall()
        conn.close()

        return jsonify([
            {
                "input": s[0],
                "type": s[1],
                "risk_score": s[2],
                "time": s[3]
            }
            for s in scans
        ])

    except Exception as e:
        print("SCANS ERROR:", e)
        return jsonify([])


# ---------------- STATS API ---------------- #

@app.route('/api/stats')
def get_stats():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT risk_score FROM scans")
        data = cursor.fetchall()

        legit = 0
        suspicious = 0
        phishing = 0

        for d in data:
            score = d[0]

            if score <= 30:
                legit += 1
            elif score <= 70:
                suspicious += 1
            else:
                phishing += 1

        conn.close()

        return jsonify({
            "legit": legit,
            "suspicious": suspicious,
            "phishing": phishing
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- RUN ---------------- #

if __name__ == '__main__':
    app.run(debug=True)