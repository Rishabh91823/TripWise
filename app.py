from flask import Flask, request, jsonify, session, send_file
import sqlite3
import requests
import os
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai

app = Flask(__name__, static_folder='.')
app.secret_key = 'tripwise_secure_session_key_2026'

DB_NAME = 'tripwise.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itinerary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            category TEXT,
            travel_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute("PRAGMA table_info(itinerary)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "user_id" not in columns:
        print("Migrating database: Adding user_id column to itinerary...")
        cursor.execute("ALTER TABLE itinerary ADD COLUMN user_id INTEGER")
        
    if "travel_date" not in columns:
        print("Migrating database: Adding travel_date column to itinerary...")
        cursor.execute("ALTER TABLE itinerary ADD COLUMN travel_date TEXT")
        
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return send_file('templates/index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    hashed_password = generate_password_hash(password)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
 
        session['user_id'] = cursor.lastrowid
        session['username'] = username
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        return jsonify({"error": "User not found"}), 404
        
    if check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Incorrect password"}), 401

@app.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@app.route('/api/me', methods=['GET'])
def me():
    if 'user_id' in session:
        return jsonify({"username": session['username']}), 200
    return jsonify({"error": "Not logged in"}), 401

@app.route('/api/explore', methods=['GET'])
def explore():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
        
    try:
        response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=6&language=en&format=json", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "results" in data:
            for item in data["results"]:
                results.append({
                    "name": item.get("name"),
                    "location": f"{item.get('admin1', '')}, {item.get('country', '')}".strip(', '),
                    "description": f"Explore the beautiful sights and culture of {item.get('name')}.",
                    "category": item.get("feature_code", "Destination"),
                    "lat": float(item.get("latitude", 0)),
                    "lon": float(item.get("longitude", 0))
                })
        else:
            raise ValueError("No results found in API")
            
        return jsonify(results)
        
    except Exception as e:
        fallback = [
            {"name": f"The Grand {query.title()} Museum", "location": query.title(), "description": f"Discover the rich history of {query.title()}.", "category": "Museum", "lat": 0, "lon": 0},
            {"name": f"{query.title()} Central Park", "location": query.title(), "description": f"A beautiful green space in the heart of {query.title()}.", "category": "Park", "lat": 0.01, "lon": 0.01}
        ]
        return jsonify(fallback)

@app.route('/api/explore_nearby', methods=['GET'])
def explore_nearby():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    try:
        headers = {'User-Agent': 'TripWisePlanner/1.0 (StudentProject)'}
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gscoord={lat}|{lon}&gsradius=10000&gslimit=5&format=json"
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'query' in data and 'geosearch' in data['query']:
            for place in data['query']['geosearch']:
                results.append({
                    "name": place['title'],
                    "location": f"{(place['dist']/1000):.1f} km away",
                    "description": f"A notable landmark near your selected coordinates.",
                    "category": "Landmark",
                    "lat": float(place['lat']),
                    "lon": float(place['lon'])
                })
                
        if not results:
            raise ValueError("No nearby locations")
            
        return jsonify(results)
    except Exception:
    
        return jsonify([{
            "name": "Hidden Gem Location",
            "location": "Near Selected Point",
            "description": "An unmapped location you discovered by clicking the map.",
            "category": "Landmark",
            "lat": float(lat) if lat else 0.0,
            "lon": float(lon) if lon else 0.0
        }])

@app.route('/api/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=3)
        data = response.json()
        temp = data.get('current_weather', {}).get('temperature')
        return jsonify({"temperature": temp})
    except:
        return jsonify({"temperature": None})


@app.route('/api/itinerary', methods=['GET'])
def get_itinerary():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location, travel_date FROM itinerary WHERE user_id = ?", (session['user_id'],))
    rows = cursor.fetchall()
    conn.close()
    
    itinerary = [{"id": row[0], "name": row[1], "location": row[2], "travel_date": row[3]} for row in rows]
    return jsonify(itinerary)

@app.route('/api/itinerary', methods=['POST'])
def add_itinerary():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO itinerary (user_id, name, location, description, category, travel_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], data.get('name'), data.get('location'), data.get('description'), data.get('category'), data.get('travel_date')))
    conn.commit()
    conn.close()
    return jsonify({"message": "Added to itinerary successfully!"}), 201

@app.route('/api/itinerary/<int:item_id>', methods=['DELETE'])
def remove_itinerary(item_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itinerary WHERE id = ? AND user_id = ?", (item_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Removed successfully!"}), 200

@app.route('/api/generate_plan', methods=['GET'])
def generate_plan():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    budget = request.args.get('budget', 'moderate')
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return jsonify({"error": "Gemini API key is missing on the server. Please set the GEMINI_API_KEY environment variable."}), 500

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, location, travel_date FROM itinerary WHERE user_id = ?", (session['user_id'],))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"error": "Your itinerary is empty! Add places first."}), 400

    places_text = ", ".join([f"{row[0]} in {row[1]} (Date: {row[2]})" for row in rows])
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"I am planning a {budget} budget trip. I want to visit these places: {places_text}. Write a short, engaging day-by-day travel plan using markdown formatting. Include brief transport and food tips."
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"plan": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)