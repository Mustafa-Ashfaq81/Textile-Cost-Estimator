# database.py
import sqlite3

DB_NAME = "cost_estimator.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cost_estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            category TEXT,
            subcategory TEXT,
            quantity INTEGER,

            artwork_cost REAL,
            artwork_cost_type TEXT,

            width REAL,
            length REAL,
            material TEXT,
            gsm REAL,
            card_calc_cost_per_piece REAL,
            card_calc_details TEXT,

            front_colors INTEGER,
            back_colors INTEGER,
            printing_color_cost REAL,
            printing_color_cost_type TEXT,

            foil_cost REAL,
            foil_cost_type TEXT,
            screen_cost REAL,
            screen_cost_type TEXT,
            heat_cost REAL,
            heat_cost_type TEXT,
            emboss_cost REAL,
            emboss_cost_type TEXT,

            coating TEXT,
            coating_cost REAL,
            coating_cost_type TEXT,

            cutting_cost REAL,
            cutting_cost_type TEXT,

            total_cost_per_piece REAL,
            total_cost_order REAL
        )
    ''')

    conn.commit()
    conn.close()

def save_cost_estimate(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cost_estimates (
            client_name, category, subcategory, quantity,
            artwork_cost, artwork_cost_type,
            width, length, material, gsm,
            card_calc_cost_per_piece, card_calc_details,
            front_colors, back_colors, printing_color_cost, printing_color_cost_type,
            foil_cost, foil_cost_type,
            screen_cost, screen_cost_type,
            heat_cost, heat_cost_type,
            emboss_cost, emboss_cost_type,
            coating, coating_cost, coating_cost_type,
            cutting_cost, cutting_cost_type,
            total_cost_per_piece, total_cost_order
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["client_name"],
        data["category"],
        data["subcategory"],
        data["quantity"],

        data["artwork_cost"],
        data["artwork_cost_type"],
        data["width"],
        data["length"],
        data["material"],
        data["gsm"],

        data["card_calc_cost_per_piece"],
        data.get("card_calc_details", ""),

        data["front_colors"],
        data["back_colors"],
        data["printing_color_cost"],
        data["printing_color_cost_type"],

        data["foil_cost"],
        data["foil_cost_type"],
        data["screen_cost"],
        data["screen_cost_type"],
        data["heat_cost"],
        data["heat_cost_type"],
        data["emboss_cost"],
        data["emboss_cost_type"],

        data["coating"],
        data["coating_cost"],
        data["coating_cost_type"],
        data["cutting_cost"],
        data["cutting_cost_type"],

        data["total_cost_per_piece"],
        data["total_cost_order"]
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id
