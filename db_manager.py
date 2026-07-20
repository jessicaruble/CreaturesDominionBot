import sqlite3
import os

DB_PATH = '/storage/emulated/0/Download/CreaturesDominionBot/database/bot_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Economy & Leveling Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            coins INTEGER DEFAULT 100,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            faction TEXT DEFAULT 'None',
            bonded_creature TEXT DEFAULT 'None'
        )
    ''')

    # 2. Moderation Table (Infractions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS infractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guild_id INTEGER,
            moderator_id INTEGER,
            type TEXT,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Territory & Factions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS territories (
            zone_name TEXT PRIMARY KEY,
            controlling_faction TEXT DEFAULT 'Wilderness',
            defense_score INTEGER DEFAULT 100
        )
    ''')

    # 4. Player Inventory Storage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            quantity INTEGER DEFAULT 1
        )
    ''')

    # --- NEW TABLE: Upcoming Scheduled Events Queue ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upcoming_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            event_details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database tables initialized successfully!")

# Inventory controls
def add_item_to_inventory(user_id, item_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ?', (user_id, item_name))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE inventory SET quantity = quantity + 1 WHERE user_id = ? AND item_name = ?', (user_id, item_name))
    else:
        cursor.execute('INSERT INTO inventory (user_id, item_name) VALUES (?, ?)', (user_id, item_name))
    conn.commit()
    conn.close()

def get_user_inventory(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, quantity FROM inventory WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Profile Core Functions
def get_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT coins, xp, level, faction, bonded_creature FROM profiles WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"coins": row, "xp": row, "level": row, "faction": row, "bonded_creature": row}
    return None

def create_profile(user_id, guild_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT OR IGNORE INTO profiles (user_id, guild_id) VALUES (?, ?)', (user_id, guild_id))
        conn.commit()
    except Exception as e:
        print(f"Error creating profile: {e}")
    finally:
        conn.close()

def update_profile(user_id, column, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE profiles SET {column} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()
