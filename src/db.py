import sqlite3
import csv

DB_NAME = "crm.db"

def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organisations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                industry TEXT,
                contact_info TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affiliations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                org_id INTEGER NOT NULL,
                start_date TEXT,
                end_date TEXT,
                position TEXT,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organisations(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

# --- People Queries ---
def insert_person(first_name, last_name, email, phone):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO people (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, phone)
        )
        conn.commit()

def update_person(person_id, first_name, last_name, email, phone):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE people SET first_name = ?, last_name = ?, email = ?, phone = ? WHERE id = ?",
            (first_name, last_name, email, phone, person_id)
        )
        conn.commit()

def delete_person(person_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM people WHERE id = ?", (person_id,))
        conn.commit()

def get_all_people():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, email, phone FROM people ORDER BY last_name, first_name")
        return cursor.fetchall()

def search_people(query):
    with connect() as conn:
        cursor = conn.cursor()
        term = f"%{query.strip()}%"
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone 
            FROM people 
            WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
            ORDER BY id DESC
        """, (term, term, term))
        return cursor.fetchall()

def check_person_exists(email):
    if not email:
        return False
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM people WHERE LOWER(email) = LOWER(?)", (email.strip(),))
        return cursor.fetchone() is not None

# --- Organisations Queries ---
def insert_organisation(name, industry, contact_info):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO organisations (name, industry, contact_info) VALUES (?, ?, ?)",
            (name, industry, contact_info)
        )
        conn.commit()

def update_organisation(org_id, name, industry, contact_info):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE organisations SET name = ?, industry = ?, contact_info = ? WHERE id = ?",
            (name, industry, contact_info, org_id)
        )
        conn.commit()

def delete_organisation(org_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM organisations WHERE id = ?", (org_id,))
        conn.commit()

def get_all_organisations():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, industry, contact_info FROM organisations ORDER BY name")
        return cursor.fetchall()

def search_organisations(query):
    with connect() as conn:
        cursor = conn.cursor()
        term = f"%{query.strip()}%"
        cursor.execute("""
            SELECT id, name, industry, contact_info 
            FROM organisations 
            WHERE name LIKE ? OR industry LIKE ?
            ORDER BY id DESC
        """, (term, term))
        return cursor.fetchall()

def check_organisation_exists(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM organisations WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        return cursor.fetchone() is not None

# --- Affiliations Queries ---
def insert_affiliation(person_id, org_id, start_date, end_date, position):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO affiliations (person_id, org_id, start_date, end_date, position) VALUES (?, ?, ?, ?, ?)",
            (person_id, org_id, start_date, end_date, position)
        )
        conn.commit()

def update_affiliation(affiliation_id, person_id, org_id, start_date, end_date, position):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE affiliations 
            SET person_id = ?, org_id = ?, start_date = ?, end_date = ?, position = ?
            WHERE id = ?
        """, (person_id, org_id, start_date, end_date, position, affiliation_id))
        conn.commit()

def delete_affiliation(affiliation_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM affiliations WHERE id = ?", (affiliation_id,))
        conn.commit()

def get_all_affiliations():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.id,
                p.first_name || ' ' || p.last_name AS person_name,
                o.name AS org_name,
                a.position,
                a.start_date,
                a.end_date
            FROM affiliations a
            JOIN people p ON a.person_id = p.id
            JOIN organisations o ON a.org_id = o.id
            ORDER BY a.id DESC
        """)
        return cursor.fetchall()

def search_affiliations(query):
    with connect() as conn:
        cursor = conn.cursor()
        term = f"%{query.strip()}%"
        cursor.execute("""
            SELECT 
                a.id,
                p.first_name || ' ' || p.last_name AS person_name,
                o.name AS org_name,
                a.position,
                a.start_date,
                a.end_date
            FROM affiliations a
            JOIN people p ON a.person_id = p.id
            JOIN organisations o ON a.org_id = o.id
            WHERE person_name LIKE ? OR org_name LIKE ? OR a.position LIKE ?
            ORDER BY a.id DESC
        """, (term, term, term))
        return cursor.fetchall()

# --- Interactions Queries ---
def insert_interaction(person_id, date, description):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interactions (person_id, date, description) VALUES (?, ?, ?)",
            (person_id, date, description)
        )
        conn.commit()

def update_interaction(interaction_id, person_id, date, description):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE interactions 
            SET person_id = ?, date = ?, description = ?
            WHERE id = ?
        """, (person_id, date, description, interaction_id))
        conn.commit()

def delete_interaction(interaction_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM interactions WHERE id = ?", (interaction_id,))
        conn.commit()

def get_all_interactions():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.id,
                p.first_name || ' ' || p.last_name AS person_name,
                i.date,
                i.description
            FROM interactions i
            JOIN people p ON i.person_id = p.id
            ORDER BY i.date DESC
        """)
        return cursor.fetchall()

def search_interactions(query):
    with connect() as conn:
        cursor = conn.cursor()
        term = f"%{query.strip()}%"
        cursor.execute("""
            SELECT 
                i.id,
                p.first_name || ' ' || p.last_name AS person_name,
                i.date,
                i.description
            FROM interactions i
            JOIN people p ON i.person_id = p.id
            WHERE person_name LIKE ? OR i.description LIKE ? OR i.date LIKE ?
            ORDER BY i.date DESC
        """, (term, term, term))
        return cursor.fetchall()

# --- Export Utility ---
def export_table_to_csv(filepath, headers, rows):
    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)