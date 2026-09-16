# Offline-First CRM

A lightweight, local-only CRM built in Python with Tkinter and SQLite. No cloud, no subscription, no vendor lock-in — client data stays entirely on your device.

---

## Why this exists

Most CRMs assume a shared, always-online database. That model doesn't suit solo consultants, small non-profits, or field researchers who don't need multi-user sync and don't want sensitive client data sitting on third-party servers. 

This project bridges that gap: a rolodex-grade desktop application that runs completely offline with a relational SQLite schema (People, Organisations, Affiliations, Interactions) underneath.

Built by [Dianoetic](https://dianoetic.com.au).

---

## Features

- **Tabbed Interface** — Clean tabbed interface managing People, Organisations, Affiliations, and Interactions.
- **Relational Schema** — SQLite database with foreign key enforcement and cascading deletes across linked entities.
- **Real-Time Search** — Dynamic filtering across all record tabs as you type.
- **CSV Data Exports** — Export structured views directly to CSV from any tab.
- **Mock Data Generator** — Built-in seeding script (`seed.py`) to quickly populate sample records for testing.
- **Fully Offline** — Zero internet dependencies; zero external telemetry.

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| UI | Tkinter | Native desktop interface with no browser runtime dependency |
| Database | SQLite | File-based relational storage with cascading foreign keys |
| Language | Python 3.x | Application logic and data handling |
| Packaging | PyInstaller | Standalone single-file executable compilation |

---

## Getting Started

### 1. Clone the repo
git clone https://github.com/pooya-karambakhsh/offline-crm-demo.git
cd offline-crm-demo

### 2. Set up virtual environment & run

**Windows**
python -m venv .venv
.venv\Scripts\activate
python src/main.py

**macOS / Linux**
python3 -m venv .venv
source .venv/bin/activate
python src/main.py

### 3. Seed sample data (Optional)
To pre-populate the database with test records:
python seed.py

---

## Packaging as Standalone Executable

To compile a single executable file that runs without Python installed:

1. Install PyInstaller:
   pip install pyinstaller

2. Build binary:
   pyinstaller --noconsole --onefile --name="OfflineCRM" src/main.py

3. Locate the compiled executable inside the generated `dist/` directory.

---

## Project Structure

crm/
├── src/
│   ├── main.py            # Entry point & notebook tab controller
│   ├── db.py              # SQLite schema, queries, cascading keys & CSV exporter
│   ├── person_form.py     # People CRUD, search & UI view
│   ├── org_form.py        # Organisations CRUD, search & UI view
│   ├── affiliation_form.py# Affiliations CRUD, dropdown maps & UI view
│   └── interaction_form.py# Interactions CRUD, dropdown maps & UI view
├── seed.py                # Database seed script for dummy records
├── .gitignore
└── README.md

---

## Contact

Built by Pooya Karambakhsh. For consulting, collaboration, or feedback, reach out via [Dianoetic](https://dianoetic.com.au).