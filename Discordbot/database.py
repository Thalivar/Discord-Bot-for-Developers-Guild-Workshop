import sqlite3
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent / "game.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        # Characters table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            xp_to_level INTEGER DEFAULT 100,
            health INTEGER DEFAULT 100,
            max_health INTEGER DEFAULT 100,
            attack INTEGER DEFAULT 10,
            defense INTEGER DEFAULT 5,
            coins INTEGER DEFAULT 0,
            current_area TEXT DEFAULT 'Starter Village'
        )''')

        # Inventory table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES characters (user_id)
        )''')

        # Equipment table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            user_id TEXT,
            slot TEXT,
            item_name TEXT,
            FOREIGN KEY (user_id) REFERENCES characters (user_id),
            PRIMARY KEY (user_id, slot)
        )''')

        # Monsters table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS monsters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            area TEXT,
            health INTEGER,
            attack INTEGER,
            defense INTEGER,
            xp_reward INTEGER,
            type TEXT,
            effect TEXT,
            description TEXT
        )''')

        # Shop items table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_items (
            item_name TEXT PRIMARY KEY,
            buy_price INTEGER,
            sell_price INTEGER,
            type TEXT,
            effect TEXT,
            description TEXT
        )''')

        self.conn.commit()

    def create_character(self, user_id: str, name: str) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO characters (user_id, name) VALUES (?, ?)",
                (user_id, name)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_character(self, user_id: str) -> dict:
        self.cursor.execute("SELECT * FROM characters WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if not result:
            return None
        
        columns = [description[0] for description in self.cursor.description]
        return dict(zip(columns, result))

    def update_character(self, user_id: str, updates: dict) -> bool:
        set_values = ", ".join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE characters SET {set_values} WHERE user_id = ?"
        values = list(updates.values()) + [user_id]
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def delete_character(self, user_id: str) -> bool:
        try:
            self.cursor.execute("DELETE FROM characters WHERE user_id = ?", (user_id,))
            self.cursor.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
            self.cursor.execute("DELETE FROM equipment WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_inventory(self, user_id: str) -> list:
        self.cursor.execute(
            "SELECT item_name, quantity FROM inventory WHERE user_id = ?", 
            (user_id,)
        )
        return self.cursor.fetchall()

    def add_item(self, user_id: str, item_name: str, quantity: int = 1) -> bool:
        try:
            self.cursor.execute(
                """
                INSERT INTO inventory (user_id, item_name, quantity) 
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, item_name) 
                DO UPDATE SET quantity = quantity + ?
                """,
                (user_id, item_name, quantity, quantity)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def remove_item(self, user_id: str, item_name: str, quantity: int = 1) -> bool:
        try:
            self.cursor.execute(
                """
                UPDATE inventory 
                SET quantity = quantity - ? 
                WHERE user_id = ? AND item_name = ? AND quantity >= ?
                """,
                (quantity, user_id, item_name, quantity)
            )
            
            if self.cursor.rowcount > 0:
                self.cursor.execute(
                    "DELETE FROM inventory WHERE quantity <= 0"
                )
                self.conn.commit()
                return True
            return False
        except sqlite3.Error:
            return False

    def __del__(self):
        self.conn.close()