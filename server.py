from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import random
import requests
import secrets
from datetime import timedelta, datetime
import hashlib
import json
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app)

# Session config
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Ollama AI configuration
OLLAMA_URL = "http://localhost:11434/api/generate"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "ADMIN2025"  # Change this!

# ============ USER ACCOUNTS & AUTHENTICATION ============

USERS_FILE = 'users.json'

DEFAULT_USERS = {
    "player1": {"name": "Player 1", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player2": {"name": "Player 2", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player3": {"name": "Player 3", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player4": {"name": "Player 4", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player5": {"name": "Player 5", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player6": {"name": "Player 6", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player7": {"name": "Player 7", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player8": {"name": "Player 8", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player9": {"name": "Player 9", "gems": 1000, "high_score": 0, "purchased_games": []},
    "player10": {"name": "Player 10", "gems": 1000, "high_score": 0, "purchased_games": []},
}

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_USERS.copy()
    return DEFAULT_USERS.copy()

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ============ 100 ARCADE GAMES DATABASE ============

ARCADE_GAMES = {
    # Paddle Games (1-10)
    1: {"name": "Pong Classic", "type": "paddle", "difficulty": "easy", "description": "2-player classic - hit the ball back and forth", "cost": 0},
    2: {"name": "Air Hockey", "type": "paddle", "difficulty": "easy", "description": "Fast-paced paddle game", "cost": 50},
    3: {"name": "Pong Extreme", "type": "paddle", "difficulty": "hard", "description": "Pong with speed multipliers", "cost": 200},
    4: {"name": "Breakout", "type": "paddle", "difficulty": "medium", "description": "Break all the bricks", "cost": 0},
    5: {"name": "Brick Breaker", "type": "paddle", "difficulty": "medium", "description": "Bounce ball to break bricks", "cost": 75},
    6: {"name": "Arkanoid", "type": "paddle", "difficulty": "hard", "description": "Advanced brick breaker", "cost": 150},
    7: {"name": "Paddle Defense", "type": "paddle", "difficulty": "hard", "description": "Defend against falling blocks", "cost": 200},
    8: {"name": "Ball Bounce", "type": "paddle", "difficulty": "easy", "description": "Keep the ball in play", "cost": 0},
    9: {"name": "Power Paddle", "type": "paddle", "difficulty": "medium", "description": "Paddle with power-ups", "cost": 100},
    10: {"name": "Ultra Pong", "type": "paddle", "difficulty": "expert", "description": "4-player Pong madness", "cost": 300},
    
    # Snake/Movement Games (11-20)
    11: {"name": "Snake Classic", "type": "movement", "difficulty": "easy", "description": "Eat food, grow longer, don't hit walls", "cost": 0},
    12: {"name": "Super Snake", "type": "movement", "difficulty": "medium", "description": "Snake with power-ups", "cost": 75},
    13: {"name": "Snake Maze", "type": "movement", "difficulty": "hard", "description": "Snake in a maze", "cost": 150},
    14: {"name": "Worm Wars", "type": "movement", "difficulty": "medium", "description": "Multiplayer worm battle", "cost": 100},
    15: {"name": "Caterpillar", "type": "movement", "difficulty": "easy", "description": "Grow your caterpillar", "cost": 0},
    16: {"name": "Slither Master", "type": "movement", "difficulty": "hard", "description": "Advanced snake gameplay", "cost": 200},
    17: {"name": "Portal Snake", "type": "movement", "difficulty": "medium", "description": "Snake with portals", "cost": 125},
    18: {"name": "Rainbow Snake", "type": "movement", "difficulty": "medium", "description": "Colorful snake adventure", "cost": 100},
    19: {"name": "Speed Snake", "type": "movement", "difficulty": "hard", "description": "Ultra-fast snake challenge", "cost": 175},
    20: {"name": "Neon Snake", "type": "movement", "difficulty": "expert", "description": "Neon-styled snake game", "cost": 300},
    
    # Shooting Games (21-40)
    21: {"name": "Space Invaders", "type": "shooter", "difficulty": "medium", "description": "Shoot down alien invaders", "cost": 0},
    22: {"name": "Asteroids", "type": "shooter", "difficulty": "medium", "description": "Destroy asteroids, avoid collision", "cost": 75},
    23: {"name": "Galaga", "type": "shooter", "difficulty": "hard", "description": "Classic space shooter", "cost": 150},
    24: {"name": "Bullet Hell", "type": "shooter", "difficulty": "expert", "description": "Dodge intense bullet patterns", "cost": 300},
    25: {"name": "Chicken Invaders", "type": "shooter", "difficulty": "easy", "description": "Shoot chickens from space", "cost": 50},
    26: {"name": "Tower Defense", "type": "shooter", "difficulty": "hard", "description": "Defend your tower", "cost": 200},
    27: {"name": "Boss Battle", "type": "shooter", "difficulty": "hard", "description": "Epic boss fights", "cost": 250},
    28: {"name": "Missile Command", "type": "shooter", "difficulty": "medium", "description": "Defend cities from missiles", "cost": 100},
    29: {"name": "Space Shooter", "type": "shooter", "difficulty": "medium", "description": "Classic arcade shooter", "cost": 0},
    30: {"name": "Laser Battle", "type": "shooter", "difficulty": "hard", "description": "Intense laser combat", "cost": 200},
    31: {"name": "Vertical Scroller", "type": "shooter", "difficulty": "medium", "description": "Fly and shoot", "cost": 75},
    32: {"name": "Enemy Waves", "type": "shooter", "difficulty": "hard", "description": "Endless enemy waves", "cost": 225},
    33: {"name": "Star Wars", "type": "shooter", "difficulty": "hard", "description": "Space dogfight", "cost": 200},
    34: {"name": "Weapon Master", "type": "shooter", "difficulty": "expert", "description": "Master all weapons", "cost": 350},
    35: {"name": "Neon Shooter", "type": "shooter", "difficulty": "medium", "description": "Neon arcade shooter", "cost": 125},
    36: {"name": "Rapid Fire", "type": "shooter", "difficulty": "hard", "description": "Speed shooting challenge", "cost": 175},
    37: {"name": "Alien Invasion", "type": "shooter", "difficulty": "hard", "description": "Aliens are coming!", "cost": 200},
    38: {"name": "Robot Wars", "type": "shooter", "difficulty": "hard", "description": "Battle killer robots", "cost": 225},
    39: {"name": "Laser Grid", "type": "shooter", "difficulty": "expert", "description": "Dodge laser grids", "cost": 300},
    40: {"name": "Ultimate Defense", "type": "shooter", "difficulty": "expert", "description": "Survive the onslaught", "cost": 400},
    
    # Flappy Bird Style (41-50)
    41: {"name": "Flappy Bird", "type": "arcade", "difficulty": "medium", "description": "Tap to fly through pipes", "cost": 0},
    42: {"name": "Flappy Plane", "type": "arcade", "difficulty": "easy", "description": "Pilot a plane", "cost": 50},
    43: {"name": "Flappy Fish", "type": "arcade", "difficulty": "medium", "description": "Swim through obstacles", "cost": 100},
    44: {"name": "Flappy Rocket", "type": "arcade", "difficulty": "hard", "description": "Launch rocket through rings", "cost": 175},
    45: {"name": "Gravity Well", "type": "arcade", "difficulty": "hard", "description": "Navigate gravity", "cost": 200},
    46: {"name": "Endless Runner", "type": "arcade", "difficulty": "medium", "description": "Run forever, avoid obstacles", "cost": 75},
    47: {"name": "Dino Run", "type": "arcade", "difficulty": "easy", "description": "Classic dinosaur runner", "cost": 0},
    48: {"name": "Pipe Runner", "type": "arcade", "difficulty": "medium", "description": "Navigate through pipes", "cost": 100},
    49: {"name": "Speed Runner", "type": "arcade", "difficulty": "hard", "description": "Ultra-fast platformer", "cost": 225},
    50: {"name": "Neon Runner", "type": "arcade", "difficulty": "hard", "description": "Neon obstacle course", "cost": 250},
    
    # Puzzle Action (51-60)
    51: {"name": "Tetris", "type": "puzzle", "difficulty": "medium", "description": "Stack falling blocks", "cost": 0},
    52: {"name": "Puyo Puyo", "type": "puzzle", "difficulty": "medium", "description": "Match colored blobs", "cost": 100},
    53: {"name": "Columns", "type": "puzzle", "difficulty": "hard", "description": "Match 3 falling gems", "cost": 150},
    54: {"name": "Block Drop", "type": "puzzle", "difficulty": "medium", "description": "Drop blocks strategically", "cost": 75},
    55: {"name": "Tile Match", "type": "puzzle", "difficulty": "easy", "description": "Match tiles", "cost": 50},
    56: {"name": "Bubble Pop", "type": "puzzle", "difficulty": "easy", "description": "Pop bubbles", "cost": 0},
    57: {"name": "Gem Crusher", "type": "puzzle", "difficulty": "medium", "description": "Crush gems", "cost": 100},
    58: {"name": "Line Clear", "type": "puzzle", "difficulty": "hard", "description": "Clear lines perfectly", "cost": 200},
    59: {"name": "Cascade", "type": "puzzle", "difficulty": "hard", "description": "Watch cascading matches", "cost": 225},
    60: {"name": "Puzzle Master", "type": "puzzle", "difficulty": "expert", "description": "Master all puzzles", "cost": 350},
    
    # Racing Games (61-70)
    61: {"name": "Top-Down Racer", "type": "racing", "difficulty": "medium", "description": "Avoid traffic, race fast", "cost": 100},
    62: {"name": "Road Runner", "type": "racing", "difficulty": "easy", "description": "Dodge obstacles on road", "cost": 50},
    63: {"name": "Canyon Cruise", "type": "racing", "difficulty": "medium", "description": "Race through canyon", "cost": 125},
    64: {"name": "Speed Racer", "type": "racing", "difficulty": "hard", "description": "High-speed racing", "cost": 200},
    65: {"name": "Time Trial", "type": "racing", "difficulty": "hard", "description": "Beat the clock", "cost": 175},
    66: {"name": "Car Dodge", "type": "racing", "difficulty": "medium", "description": "Dodge incoming cars", "cost": 100},
    67: {"name": "Neon Racer", "type": "racing", "difficulty": "hard", "description": "Neon racing action", "cost": 225},
    68: {"name": "Cross Road", "type": "racing", "difficulty": "easy", "description": "Cross the road safely", "cost": 0},
    69: {"name": "Traffic Master", "type": "racing", "difficulty": "hard", "description": "Master traffic patterns", "cost": 250},
    70: {"name": "Velocity", "type": "racing", "difficulty": "expert", "description": "Maximum speed challenge", "cost": 400},
    
    # Platform Games (71-85)
    71: {"name": "Platformer Classic", "type": "platform", "difficulty": "easy", "description": "Jump and collect coins", "cost": 0},
    72: {"name": "Super Mario Style", "type": "platform", "difficulty": "medium", "description": "Adventure platformer", "cost": 100},
    73: {"name": "Cave Explorer", "type": "platform", "difficulty": "medium", "description": "Explore caves, find treasure", "cost": 125},
    74: {"name": "Jungle Jump", "type": "platform", "difficulty": "medium", "description": "Swing through jungle", "cost": 150},
    75: {"name": "Mountain Climber", "type": "platform", "difficulty": "hard", "description": "Climb to peak", "cost": 200},
    76: {"name": "Ice Climb", "type": "platform", "difficulty": "hard", "description": "Climb icy peaks", "cost": 225},
    77: {"name": "Tower Climb", "type": "platform", "difficulty": "hard", "description": "Climb endless tower", "cost": 250},
    78: {"name": "Gravity Flip", "type": "platform", "difficulty": "hard", "description": "Control gravity", "cost": 275},
    79: {"name": "Portal Platformer", "type": "platform", "difficulty": "hard", "description": "Platformer with portals", "cost": 300},
    80: {"name": "Ninja Parkour", "type": "platform", "difficulty": "expert", "description": "Ninja-style parkour", "cost": 350},
    81: {"name": "Wall Jump Master", "type": "platform", "difficulty": "expert", "description": "Master wall jumps", "cost": 375},
    82: {"name": "Pixel Runner", "type": "platform", "difficulty": "medium", "description": "Retro pixel runner", "cost": 100},
    83: {"name": "Quest", "type": "platform", "difficulty": "hard", "description": "Epic quest platformer", "cost": 275},
    84: {"name": "Legacy", "type": "platform", "difficulty": "hard", "description": "Classic platformer homage", "cost": 250},
    85: {"name": "Ultimate Platformer", "type": "platform", "difficulty": "expert", "description": "Master of platformers", "cost": 400},
    
    # Multiplayer Games (86-95)
    86: {"name": "2-Player Battle", "type": "multiplayer", "difficulty": "medium", "description": "Local multiplayer fight", "cost": 0},
    87: {"name": "Co-op Adventure", "type": "multiplayer", "difficulty": "medium", "description": "Play together", "cost": 150},
    88: {"name": "Competitive Racing", "type": "multiplayer", "difficulty": "hard", "description": "Race friends", "cost": 200},
    89: {"name": "Battle Royale Mini", "type": "multiplayer", "difficulty": "hard", "description": "Last one standing", "cost": 250},
    90: {"name": "Tag Game", "type": "multiplayer", "difficulty": "easy", "description": "Digital tag", "cost": 0},
    91: {"name": "Team Challenge", "type": "multiplayer", "difficulty": "medium", "description": "Work as team", "cost": 125},
    92: {"name": "Deathmatch", "type": "multiplayer", "difficulty": "hard", "description": "All-out battle", "cost": 225},
    93: {"name": "King of Arena", "type": "multiplayer", "difficulty": "hard", "description": "Control the center", "cost": 200},
    94: {"name": "Co-op Survival", "type": "multiplayer", "difficulty": "hard", "description": "Survive together", "cost": 275},
    95: {"name": "Ultimate Multiplayer", "type": "multiplayer", "difficulty": "expert", "description": "Max chaos mode", "cost": 400},
    
    # Special/Unique Games (96-100)
    96: {"name": "Pac-Man", "type": "special", "difficulty": "medium", "description": "Eat pellets, avoid ghosts", "cost": 0},
    97: {"name": "Breakdance Battle", "type": "special", "difficulty": "hard", "description": "Rhythm-based action", "cost": 200},
    98: {"name": "Memory Blocks", "type": "special", "difficulty": "easy", "description": "Remember and click", "cost": 50},
    99: {"name": "Whack-a-Mole", "type": "special", "difficulty": "easy", "description": "Click fast moles", "cost": 0},
    100: {"name": "Arcade Mayhem", "type": "special", "difficulty": "expert", "description": "All games mixed together", "cost": 500},
}

# ============ OLLAMA CHATBOT ============

def query_ollama(user_message, conversation_history):
    """Query Ollama AI for responses"""
    try:
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-10:]])
        
        prompt = f"""You are a friendly arcade gaming expert AI. Help users with:
- Game recommendations based on skill level and preference
- Tips and strategies for arcade games (Pong, Snake, Space Invaders, etc.)
- Gaming challenges and high score tips
- Arcade gaming history and fun facts
- General gaming questions and encouragement

Context of conversation:
{context}

User: {user_message}
Assistant:"""
        
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
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

# ============ ADMIN ROUTES ============

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid admin credentials"}), 401
    
    if 'admin' in session:
        return render_template('admin.html')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/api/admin/users')
def admin_get_users():
    """Get all users (admin only)"""
    if 'admin' not in session:
        return jsonify({"error": "Not authorized"}), 401
    
    users = load_users()
    return jsonify(users)

@app.route('/api/admin/update-gems', methods=['POST'])
def admin_update_gems():
    """Update gems for a player (admin only)"""
    if 'admin' not in session:
        return jsonify({"error": "Not authorized"}), 401
    
    data = request.json
    username = data.get('username', '').lower()
    action = data.get('action', 'set')  # 'set', 'add', 'subtract'
    amount = data.get('amount', 0)
    
    users = load_users()
    
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    
    current_gems = users[username].get('gems', 0)
    
    if action == 'set':
        users[username]['gems'] = amount
    elif action == 'add':
        users[username]['gems'] = current_gems + amount
    elif action == 'subtract':
        users[username]['gems'] = max(0, current_gems - amount)
    
    save_users(users)
    return jsonify({
        "success": True,
        "username": username,
        "gems": users[username]['gems']
    })

@app.route('/api/admin/reset-account', methods=['POST'])
def admin_reset_account():
    """Reset account to default (admin only)"""
    if 'admin' not in session:
        return jsonify({"error": "Not authorized"}), 401
    
    data = request.json
    username = data.get('username', '').lower()
    
    users = load_users()
    
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Reset to default
    users[username] = {
        "name": f"Player {username.replace('player', '')}",
        "gems": 1000,
        "high_score": 0,
        "purchased_games": []
    }
    
    save_users(users)
    return jsonify({"success": True, "message": f"Account {username} reset!"})

@app.route('/api/admin/clear-all', methods=['POST'])
def admin_clear_all():
    """Reset all accounts (admin only)"""
    if 'admin' not in session:
        return jsonify({"error": "Not authorized"}), 401
    
    save_users(DEFAULT_USERS.copy())
    return jsonify({"success": True, "message": "All accounts reset to defaults!"})

@app.route('/api/games')
def get_games():
    """Get all 100 games"""
    return jsonify(ARCADE_GAMES)

@app.route('/api/games/<int:game_id>')
def get_game(game_id):
    """Get specific game details"""
    if game_id in ARCADE_GAMES:
        game = ARCADE_GAMES[game_id].copy()
        game['id'] = game_id
        return jsonify(game)
    return jsonify({"error": "Game not found"}), 404

@app.route('/api/games/random')
def random_game():
    """Get a random game"""
    game_id = random.choice(list(ARCADE_GAMES.keys()))
    game = ARCADE_GAMES[game_id].copy()
    game['id'] = game_id
    return jsonify(game)

@app.route('/api/games/filter')
def filter_games():
    """Filter games by type or difficulty"""
    game_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    
    filtered = {}
    for gid, game in ARCADE_GAMES.items():
        if (not game_type or game['type'] == game_type) and \
           (not difficulty or game['difficulty'] == difficulty):
            filtered[gid] = game
    
    return jsonify(filtered)

@app.route('/api/stats')
def get_stats():
    """Get game statistics"""
    types = {}
    difficulties = {}
    
    for game in ARCADE_GAMES.values():
        types[game['type']] = types.get(game['type'], 0) + 1
        difficulties[game['difficulty']] = difficulties.get(game['difficulty'], 0) + 1
    
    return jsonify({
        "total_games": len(ARCADE_GAMES),
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
    
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    conversation_history = session['chat_history']
    conversation_history.append({"role": "user", "content": user_message})
    
    ai_response = query_ollama(user_message, conversation_history)
    conversation_history.append({"role": "assistant", "content": ai_response})
    
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

# ============ HEALTH CHECK ============

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "games": len(ARCADE_GAMES),
        "version": "3.0-arcade-admin-no-login"
    })

if __name__ == '__main__':
    if not os.path.exists(USERS_FILE):
        save_users(DEFAULT_USERS)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
