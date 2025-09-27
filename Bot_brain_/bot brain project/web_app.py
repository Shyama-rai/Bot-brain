import os
from flask import Flask, send_from_directory, request, jsonify
from pathfinding import CampusPathfinder
from gemini_integration import GeminiAssistant
import json

app = Flask(__name__, static_folder='.')

# Initialize instances immediately
pathfinder = CampusPathfinder("attached_assets/map_1758707724808.osm")
# Check for GEMINI_API_KEY from Replit secrets
if "GEMINI_API_KEY" in os.environ:
    gemini = GeminiAssistant()
else:
    gemini = None

# Serve the main HTML file
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# API endpoint for pathfinding
@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.json
    start_location = data.get('start')
    end_location = data.get('end')
    algorithm = data.get('algorithm')
    
    if not start_location or not end_location or not algorithm:
        return jsonify({"error": "Missing parameters"}), 400
    
    try:
        result = pathfinder.find_path(start_location, end_location, algorithm)
        
        # Convert map to JSON for sending to frontend
        # Folium maps are difficult to serialize. Send back the path data instead.
        path_nodes = [
            (pathfinder.graph.nodes[n]['y'], pathfinder.graph.nodes[n]['x'])
            for n in result['path']
        ] if 'path' in result else []
        
        return jsonify({
            "metrics": result['metrics'],
            "path": path_nodes
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint for Gemini chat
@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    if not gemini:
        return jsonify({"error": "AI Assistant unavailable. GEMINI_API_KEY not configured."}), 503
        
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Missing query"}), 400
        
    try:
        response = gemini.get_response(query)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint to get list of POIs
@app.route('/locations', methods=['GET'])
def get_locations():
    try:
        locations = list(pathfinder.POIS.keys())
        return jsonify(locations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)