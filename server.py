from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import random
import math
import requests
import json
import secrets
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Session config
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Ollama AI configuration
OLLAMA_URL = "http://localhost:11434/api/generate"

# ============ GAME DATABASE ============

SHAPE_GAMES = {
    # Pattern Recognition Games (1-10)
    1: {"name": "Circle Match", "type": "pattern", "difficulty": "easy"},
    2: {"name": "Square Sequence", "type": "pattern", "difficulty": "easy"},
    3: {"name": "Triangle Rotation", "type": "pattern", "difficulty": "medium"},
    4: {"name": "Shape Morph", "type": "pattern", "difficulty": "medium"},
    5: {"name": "Polygon Fill", "type": "pattern", "difficulty": "hard"},
    6: {"name": "Symmetry Master", "type": "pattern", "difficulty": "easy"},
    7: {"name": "Shape Grid Solver", "type": "pattern", "difficulty": "hard"},
    8: {"name": "Tessellation Builder", "type": "pattern", "difficulty": "hard"},
    9: {"name": "Fractal Explorer", "type": "pattern", "difficulty": "expert"},
    10: {"name": "Shape Evolution", "type": "pattern", "difficulty": "expert"},
    
    # Color & Shape Combinations (11-20)
    11: {"name": "Color Shape Sort", "type": "color", "difficulty": "easy"},
    12: {"name": "Gradient Blend", "type": "color", "difficulty": "medium"},
    13: {"name": "Hue Spectrum Match", "type": "color", "difficulty": "medium"},
    14: {"name": "Color Wheel Puzzle", "type": "color", "difficulty": "medium"},
    15: {"name": "Chromatic Depth", "type": "color", "difficulty": "hard"},
    16: {"name": "Rainbow Constructor", "type": "color", "difficulty": "hard"},
    17: {"name": "Color Harmony", "type": "color", "difficulty": "easy"},
    18: {"name": "Shade Distinction", "type": "color", "difficulty": "medium"},
    19: {"name": "Palette Picker", "type": "color", "difficulty": "hard"},
    20: {"name": "Color Blindness Test", "type": "color", "difficulty": "expert"},
    
    # Speed & Precision (21-30)
    21: {"name": "Rapid Click", "type": "speed", "difficulty": "easy"},
    22: {"name": "Shape Sprint", "type": "speed", "difficulty": "medium"},
    23: {"name": "Precision Aim", "type": "speed", "difficulty": "medium"},
    24: {"name": "Fast Reflect", "type": "speed", "difficulty": "hard"},
    25: {"name": "Dodge Shapes", "type": "speed", "difficulty": "hard"},
    26: {"name": "Bounce Challenge", "type": "speed", "difficulty": "medium"},
    27: {"name": "Target Practice", "type": "speed", "difficulty": "easy"},
    28: {"name": "Shape Catch", "type": "speed", "difficulty": "medium"},
    29: {"name": "Extreme Reaction", "type": "speed", "difficulty": "hard"},
    30: {"name": "Hyperspeed", "type": "speed", "difficulty": "expert"},
    
    # Geometry & Math (31-40)
    31: {"name": "Angle Calculator", "type": "geometry", "difficulty": "medium"},
    32: {"name": "Area Master", "type": "geometry", "difficulty": "medium"},
    33: {"name": "Perimeter Challenge", "type": "geometry", "difficulty": "easy"},
    34: {"name": "Volume Builder", "type": "geometry", "difficulty": "hard"},
    35: {"name": "Coordinate Mapper", "type": "geometry", "difficulty": "medium"},
    36: {"name": "Pythagorean Puzzle", "type": "geometry", "difficulty": "hard"},
    37: {"name": "Tangent Tracer", "type": "geometry", "difficulty": "hard"},
    38: {"name": "Circle Theorem", "type": "geometry", "difficulty": "hard"},
    39: {"name": "3D Rotation", "type": "geometry", "difficulty": "expert"},
    40: {"name": "Tessellation Math", "type": "geometry", "difficulty": "expert"},
    
    # Shape Identification (41-50)
    41: {"name": "Shape Namer", "type": "identification", "difficulty": "easy"},
    42: {"name": "Polygon Classifier", "type": "identification", "difficulty": "easy"},
    43: {"name": "3D Shape ID", "type": "identification", "difficulty": "medium"},
    44: {"name": "Shadow Matcher", "type": "identification", "difficulty": "medium"},
    45: {"name": "Silhouette Solver", "type": "identification", "difficulty": "medium"},
    46: {"name": "Outline Challenge", "type": "identification", "difficulty": "hard"},
    47: {"name": "Distorted Shape ID", "type": "identification", "difficulty": "hard"},
    48: {"name": "Perspective Puzzle", "type": "identification", "difficulty": "hard"},
    49: {"name": "Impossible Shape", "type": "identification", "difficulty": "expert"},
    50: {"name": "Optical Illusion", "type": "identification", "difficulty": "expert"},
    
    # Rotation & Transformation (51-60)
    51: {"name": "Rotate & Match", "type": "rotation", "difficulty": "easy"},
    52: {"name": "Mirror Image", "type": "rotation", "difficulty": "easy"},
    53: {"name": "Flip Challenge", "type": "rotation", "difficulty": "medium"},
    54: {"name": "3D Rotation Viewer", "type": "rotation", "difficulty": "medium"},
    55: {"name": "Rotation Sequence", "type": "rotation", "difficulty": "medium"},
    56: {"name": "Complex Transforms", "type": "rotation", "difficulty": "hard"},
    57: {"name": "Spin Master", "type": "rotation", "difficulty": "hard"},
    58: {"name": "Quaternion Solver", "type": "rotation", "difficulty": "expert"},
    59: {"name": "4D Rotation", "type": "rotation", "difficulty": "expert"},
    60: {"name": "Transformation Matrix", "type": "rotation", "difficulty": "expert"},
    
    # Puzzle & Logic (61-70)
    61: {"name": "Shape Sudoku", "type": "logic", "difficulty": "medium"},
    62: {"name": "Tangram Puzzle", "type": "logic", "difficulty": "medium"},
    63: {"name": "Pentomino Solver", "type": "logic", "difficulty": "hard"},
    64: {"name": "Shape Slider", "type": "logic", "difficulty": "medium"},
    65: {"name": "Block Rotation", "type": "logic", "difficulty": "hard"},
    66: {"name": "Hexagon Fit", "type": "logic", "difficulty": "hard"},
    67: {"name": "Impossible Fit", "type": "logic", "difficulty": "expert"},
    68: {"name": "Portal Puzzle", "type": "logic", "difficulty": "hard"},
    69: {"name": "Shape Teleport", "type": "logic", "difficulty": "expert"},
    70: {"name": "Dimensional Shift", "type": "logic", "difficulty": "expert"},
    
    # Drawing & Creation (71-80)
    71: {"name": "Shape Draw", "type": "creative", "difficulty": "easy"},
    72: {"name": "Perfect Circle", "type": "creative", "difficulty": "easy"},
    73: {"name": "Symmetry Draw", "type": "creative", "difficulty": "medium"},
    74: {"name": "Freeform Shape", "type": "creative", "difficulty": "medium"},
    75: {"name": "Mandala Creator", "type": "creative", "difficulty": "hard"},
    76: {"name": "Fractal Generator", "type": "creative", "difficulty": "hard"},
    77: {"name": "Bezier Curves", "type": "creative", "difficulty": "hard"},
    78: {"name": "Geometric Art", "type": "creative", "difficulty": "expert"},
    79: {"name": "Vector Sculptor", "type": "creative", "difficulty": "expert"},
    80: {"name": "Topology Canvas", "type": "creative", "difficulty": "expert"},
    
    # Memory & Observation (81-90)
    81: {"name": "Shape Memory", "type": "memory", "difficulty": "easy"},
    82: {"name": "Pattern Recall", "type": "memory", "difficulty": "medium"},
    83: {"name": "Sequence Memory", "type": "memory", "difficulty": "medium"},
    84: {"name": "Change Detection", "type": "memory", "difficulty": "hard"},
    85: {"name": "Hidden Shapes", "type": "memory", "difficulty": "medium"},
    86: {"name": "Spot Difference", "type": "memory", "difficulty": "medium"},
    87: {"name": "Master Observer", "type": "memory", "difficulty": "hard"},
    88: {"name": "Brief Flash", "type": "memory", "difficulty": "hard"},
    89: {"name": "Shape Ghost", "type": "memory", "difficulty": "expert"},
    90: {"name": "Perfect Recall", "type": "memory", "difficulty": "expert"},
    
    # Multiplayer & Advanced (91-100)
    91: {"name": "Shape Battle", "type": "multiplayer", "difficulty": "medium"},
    92: {"name": "Polygon Duel", "type": "multiplayer", "difficulty": "hard"},
    93: {"name": "Tetris Shapes", "type": "multiplayer", "difficulty": "medium"},
    94: {"name": "Cooperative Build", "type": "multiplayer", "difficulty": "hard"},
    95: {"name": "Competitive Puzzle", "type": "multiplayer", "difficulty": "hard"},
    96: {"name": "Shape Auction", "type": "multiplayer", "difficulty": "expert"},
    97: {"name": "Geometric Chess", "type": "multiplayer", "difficulty": "expert"},
    98: {"name": "Kaleidoscope Race", "type": "multiplayer", "difficulty": "expert"},
    99: {"name": "Shape Royale", "type": "multiplayer", "difficulty": "expert"},
    100: {"name": "Ultimate Geometric", "type": "multiplayer", "difficulty": "expert"},
}

# ============ OLLAMA CHATBOT ============

def query_ollama(user_message, conversation_history):
    """Query Ollama AI for responses"""
    try:
        # Build context from conversation history
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-10:]])
        
        prompt = f"""You are a friendly AI gaming assistant for a shape-based games server. Help users with:
- Game recommendations based on skill level
- Tips and strategies for games
- Gaming challenges and achievements
- General gaming questions and encouragement

Context of conversation:
{context}

User: {user_message}
Assistant:"""
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",  # Or use "neural-chat", "orca-mini", etc.
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "I couldn't generate a response. Try again!").strip()
        else:
            return "Connection error with AI. Make sure Ollama is running!"
    
    except requests.exceptions.ConnectionError:
        return "⚠️ Ollama AI is not running. Start it with: `ollama serve` then run `ollama pull mistral`"
    except Exception as e:
        return f"Error: {str(e)}"

# ============ ROUTES ============

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/api/games')
def get_games():
    """Get all 100 games"""
    return jsonify(SHAPE_GAMES)

@app.route('/api/games/<int:game_id>')
def get_game(game_id):
    """Get specific game details"""
    if game_id in SHAPE_GAMES:
        game = SHAPE_GAMES[game_id].copy()
        game['id'] = game_id
        return jsonify(game)
    return jsonify({"error": "Game not found"}), 404

@app.route('/api/games/random')
def random_game():
    """Get a random game"""
    game_id = random.choice(list(SHAPE_GAMES.keys()))
    game = SHAPE_GAMES[game_id].copy()
    game['id'] = game_id
    return jsonify(game)

@app.route('/api/games/filter')
def filter_games():
    """Filter games by type or difficulty"""
    game_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    
    filtered = {}
    for gid, game in SHAPE_GAMES.items():
        if (not game_type or game['type'] == game_type) and \
           (not difficulty or game['difficulty'] == difficulty):
            filtered[gid] = game
    
    return jsonify(filtered)

@app.route('/api/stats')
def get_stats():
    """Get game statistics"""
    types = {}
    difficulties = {}
    
    for game in SHAPE_GAMES.values():
        types[game['type']] = types.get(game['type'], 0) + 1
        difficulties[game['difficulty']] = difficulties.get(game['difficulty'], 0) + 1
    
    return jsonify({
        "total_games": len(SHAPE_GAMES),
        "types": types,
        "difficulties": difficulties
    })

# ============ CHATBOT ROUTES ============

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for Ollama AI"""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get or initialize conversation history in session
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    conversation_history = session['chat_history']
    conversation_history.append({"role": "user", "content": user_message})
    
    # Get AI response
    ai_response = query_ollama(user_message, conversation_history)
    conversation_history.append({"role": "assistant", "content": ai_response})
    
    # Keep only last 20 messages to save memory
    session['chat_history'] = conversation_history[-20:]
    session.modified = True
    
    return jsonify({
        "response": ai_response,
        "history_length": len(conversation_history)
    })

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session['chat_history'] = []
    session.modified = True
    return jsonify({"status": "Chat cleared"})

@app.route('/api/chat/history')
def chat_history():
    """Get chat history"""
    if 'chat_history' not in session:
        session['chat_history'] = []
    return jsonify({"history": session['chat_history']})

# ============ HEALTH CHECK ============

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "games": len(SHAPE_GAMES),
        "version": "1.0"
    })

if __name__ == '__main__':
    # Run on 0.0.0.0 to accept external connections
    app.run(host='0.0.0.0', port=5000, debug=True)
