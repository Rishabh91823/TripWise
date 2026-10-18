# TripWise - Smart Travel Planner

TripWise is a full-stack travel planning web application that allows users to discover global destinations, explore landmarks via an interactive map, inspect real-time weather forecasts, curate custom itineraries, and generate AI-powered travel itineraries tailored to their budget.

---

## Chosen Track
**Track 3: Full-Stack Development**

---

## Features
- **User Authentication:** Secure signup, login, and session-based access using password hashing.
- **Destination Discovery:** Search global destinations powered by the Open-Meteo Geocoding API.
- **Interactive Map Exploration:** Leaflet.js interactive map integration utilizing Wikipedia's Geosearch API to discover landmarks by clicking anywhere on the map.
- **Search, Filter & Sort:** Alphabetical sorting (A-Z, Z-A) and category filtering.
- **Live Weather Data:** Real-time weather forecasting on destination cards via Open-Meteo.
- **Itinerary Management:** Persistent CRUD operations saved per user in a SQLite database.
- **AI Itinerary Planner:** Integrated Google Gemini 1.5 Flash model generating day-by-day travel schedules based on saved itinerary items and budget preferences.
- **Direct Booking Integration:** Automated flight and hotel booking routes via Google Travel.

---

## Tech Stack
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript, Leaflet.js, Marked.js, FontAwesome
- **Backend:** Python, Flask, Werkzeug Security, Requests
- **Database:** SQLite
- **AI Engine:** Google Gemini API (`gemini-1.5-flash`)
- **External APIs:** Open-Meteo Geocoding API, Open-Meteo Weather Forecast API, Wikipedia Geosearch API

---

## External APIs Used

| API Name | Purpose | Authentication |
| :--- | :--- | :--- |
| **Open-Meteo Geocoding API** | Search cities and convert query strings to geographic coordinates | Free (No Key Required) |
| **Open-Meteo Weather API** | Fetch live temperatures for selected coordinates | Free (No Key Required) |
| **Wikipedia Geosearch API** | Retrieve nearby landmarks and tourist spots based on map click coordinates | Free (No Key Required) |
| **Google Gemini API** | Generate custom markdown travel itineraries based on saved places | API Key Required (Server Environment Variable) |

---

## Database Configuration
The application uses SQLite (`tripwise.db`). Tables are initialized automatically upon application startup.

---

## API Endpoints Documentation

### Authentication
- `POST /api/register`
  - **Body:** `{"username": "example", "password": "password123"}`
  - **Response:** `201 Created`
- `POST /api/login`
  - **Body:** `{"username": "example", "password": "password123"}`
  - **Response:** `200 OK`
- `GET /api/logout`
  - **Response:** `200 OK`
- `GET /api/me`
  - **Response:** `200 OK` `{"username": "example"}`

### Destinations & Weather
- `GET /api/explore?query={city}`
  - **Response:** Array of destination objects containing coordinates, description, and location metadata.
- `GET /api/explore_nearby?lat={latitude}&lon={longitude}`
  - **Response:** Array of nearby landmark objects retrieved from Wikipedia.
- `GET /api/weather?lat={latitude}&lon={longitude}`
  - **Response:** `{"temperature": 24.5}`

### Itinerary Management
- `GET /api/itinerary`
  - **Response:** Array of saved itinerary items for the active session user.
- `POST /api/itinerary`
  - **Body:** `{"name": "Eiffel Tower", "location": "Paris", "description": "...", "category": "Landmark", "travel_date": "2026-11-01"}`
  - **Response:** `201 Created`
- `DELETE /api/itinerary/<id>`
  - **Response:** `200 OK`

### AI Travel Planner
- `GET /api/generate_plan?budget={budget_type}`
  - **Response:** `{"plan": "# Markdown Travel Plan..."}`

---

## Local Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/tripwise.git](https://github.com/YOUR_USERNAME/tripwise.git)
   cd tripwise
   Install Dependencies

2. Bash
pip install -r requirements.txt
Set the Gemini API Key

3. Windows (Command Prompt):

-DOS
set GEMINI_API_KEY=your_gemini_api_key_here
Windows (PowerShell):

-PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
Linux / macOS:

-Bash
export GEMINI_API_KEY="your_gemini_api_key_here"
Run the Application

-Bash
python app.py
Access in Browser
Open http://127.0.0.1:5000


---
