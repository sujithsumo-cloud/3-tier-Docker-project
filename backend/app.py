import os
import time
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppass")


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def wait_for_database(max_attempts=10):
    for attempt in range(1, max_attempts + 1):
        try:
            conn = get_connection()
            conn.close()
            return True
        except Exception as error:
            print(f"Database connection attempt {attempt} failed: {error}")
            time.sleep(3)
    return False


@app.route("/")
def home():
    if not wait_for_database():
        return "<h1>Database connection failed</h1>", 500

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO visits (message) VALUES (%s)", ("New visit",))
        cursor.execute("SELECT COUNT(*) AS total_visits FROM visits")
        result = cursor.fetchone()

    conn.close()

    total_visits = result["total_visits"]

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Docker 3-Tier DevOps Project</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                text-align: center;
                padding-top: 80px;
            }}
            .card {{
                background: white;
                width: 600px;
                margin: auto;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #1f2937;
            }}
            .count {{
                font-size: 36px;
                color: #2563eb;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Dockerized 3-Tier Web Application</h1>
            <p><b>Web Tier:</b> Nginx Reverse Proxy</p>
            <p><b>App Tier:</b> Flask Backend</p>
            <p><b>Database Tier:</b> MySQL</p>
            <p>Total Visits Stored in MySQL:</p>
            <div class="count">{total_visits}</div>
        </div>
    </body>
    </html>
    """


@app.route("/visits")
def visits():
    if not wait_for_database():
        return jsonify({"error": "Database connection failed"}), 500

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total_visits FROM visits")
        result = cursor.fetchone()

    conn.close()

    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "flask_backend"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
