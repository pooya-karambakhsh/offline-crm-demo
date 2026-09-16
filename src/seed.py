import sqlite3
import random

DB_NAME = "crm.db"

FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Cameron", "Dakota"]
LAST_NAMES = ["Smith", "Jones", "Taylor", "Williams", "Brown", "Davies", "Wilson", "Evans", "Thomas", "Roberts"]
DOMAINS = ["example.com", "org.au", "tech.co", "research.org", "insights.io"]

ORGS = [
    ("Acme Corp", "Technology", "contact@acme.com"),
    ("Global Health Initiative", "Non-Profit", "info@ghi.org"),
    ("Apex Dynamics", "Engineering", "hello@apexdynamics.com"),
    ("Pacific Policy Institute", "Research", "admin@pacificpolicy.org"),
    ("Horizon Analytics", "Data Services", "support@horizon.io"),
]

POSITIONS = ["Research Fellow", "Data Analyst", "Project Manager", "Consultant", "Director", "Policy Advisor"]
DESCRIPTIONS = [
    "Introductory meeting regarding upcoming research partnership.",
    "Followed up on project milestone deliverables.",
    "Discussed budget allocations and funding proposal.",
    "Brief catch-up via email regarding quarterly evaluation.",
    "Attended strategy workshop together."
]

def seed_database():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Seed People
    people_ids = []
    for _ in range(15):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(1,99)}@{random.choice(DOMAINS)}"
        phone = f"04{random.randint(10000000, 99999999)}"
        
        cursor.execute(
            "INSERT INTO people (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
            (fn, ln, email, phone)
        )
        people_ids.append(cursor.lastrowid)

    # Seed Organisations
    org_ids = []
    for name, industry, contact in ORGS:
        cursor.execute(
            "INSERT INTO organisations (name, industry, contact_info) VALUES (?, ?, ?)",
            (name, industry, contact)
        )
        org_ids.append(cursor.lastrowid)

    # Seed Affiliations
    for person_id in people_ids:
        if random.random() > 0.3:  # 70% of people have an affiliation
            org_id = random.choice(org_ids)
            position = random.choice(POSITIONS)
            start_date = f"202{random.randint(0,4)}-0{random.randint(1,9)}-15"
            cursor.execute(
                "INSERT INTO affiliations (person_id, org_id, start_date, end_date, position) VALUES (?, ?, ?, ?, ?)",
                (person_id, org_id, start_date, "", position)
            )

    # Seed Interactions
    for _ in range(25):
        person_id = random.choice(people_ids)
        date_str = f"2026-0{random.randint(1,8)}-{random.randint(10,28)}"
        desc = random.choice(DESCRIPTIONS)
        cursor.execute(
            "INSERT INTO interactions (person_id, date, description) VALUES (?, ?, ?)",
            (person_id, date_str, desc)
        )

    conn.commit()
    conn.close()
    print("Database successfully seeded with dummy data.")

if __name__ == "__main__":
    seed_database()