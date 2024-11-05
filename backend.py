from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import requests
import random

app = Flask(__name__)
CORS(app)  # Дозволити CORS для всіх доменів

# Функція для підключення до бази даних
def connect_to_db():
    return mysql.connector.connect(
        user='admin',
        password='bebusamebus',
        host='databaseht.clsme2w0ce1q.eu-north-1.rds.amazonaws.com',
        database='databaseht' 
    )

# Create the table for football matches
@app.route('/create_table', methods=['POST'])
def create_table():
    conn = None
    cursor = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS football_match (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_home VARCHAR(100) NOT NULL,
                team_away VARCHAR(100) NOT NULL,
                match_date DATE NOT NULL,
                score_home INT,
                score_away INT
            )
        """)
        return jsonify({"message": "Table 'football_match' created successfully!"}), 201
    except Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Add a new football match
@app.route('/matches', methods=['POST'])
def add_match():
    data = request.json
    team_home = data.get('team_home')
    team_away = data.get('team_away')
    match_date = data.get('match_date')
    score_home = data.get('score_home')
    score_away = data.get('score_away')
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO football_match (team_home, team_away, match_date, score_home, score_away)
        VALUES (%s, %s, %s, %s, %s)
    """, (team_home, team_away, match_date, score_home, score_away))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Match record added successfully!"}), 201

# Get all football matches
@app.route('/matches', methods=['GET'])
def get_all_matches():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM football_match")
    matches = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Format data for response
    matches_list = [
        {
            "id": match[0],
            "team_home": match[1],
            "team_away": match[2],
            "match_date": match[3],
            "score_home": match[4],
            "score_away": match[5]
        } for match in matches
    ]
    
    return jsonify(matches_list), 200

# Function to add a random match for testing purposes
@app.route('/test_add_random_match', methods=['POST'])
def add_random_match():
    teams = ["Team A", "Team B", "Team C", "Team D"]
    random_home = random.choice(teams)
    random_away = random.choice([team for team in teams if team != random_home])
    random_date = "2024-11-01"
    random_score_home = random.randint(0, 5)
    random_score_away = random.randint(0, 5)
    payload = {
        "team_home": random_home,
        "team_away": random_away,
        "match_date": random_date,
        "score_home": random_score_home,
        "score_away": random_score_away
    }
    
    # Insert the random match directly into the database
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO `football_match` (team_home, team_away, match_date, score_home, score_away) VALUES (%s, %s, %s, %s, %s)", (payload["team_home"], payload["team_away"], payload["match_date"], payload["score_home"], payload["score_away"]))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Random match added successfully!"}), 201


# Запуск сервера
if __name__ == '__main__':
    with app.app_context():
        create_table()
        add_random_match() 
    app.run(host='0.0.0.0', port=5000)  # Змінюйте порт, якщо потрібно