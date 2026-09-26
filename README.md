# Contact Management System (Flask)

A web-based contact manager converted from a console Python script.
Contacts are validated with regex, stored in JSON, and can be
exported to / imported from CSV.

## Features
- **Add** a contact (name, phone, email) with regex-validated phone and email
- **View / Search** all contacts by name, phone, or email (case-insensitive substring match)
- **Edit** an existing contact
- **Delete** a contact (with confirmation)
- **Export** all contacts to a downloadable CSV file
- **Import** contacts from an uploaded CSV file (invalid rows are skipped and counted)

## Tech Stack
- Python 3, Flask, Jinja2 templates
- Storage: `contacts.json` (primary), CSV for export/import

## Project Structure
```
contact_web/
├── app.py             # Flask routes (web layer)
├── contact_core.py    # Validation, storage, CRUD, search (business logic)
├── templates/
│   ├── layout.html
│   ├── index.html
│   └── edit.html
├── static/
│   └── style.css
├── uploads/            # Temp storage for imported CSV files
└── exports/            # Generated CSV exports
```

## Setup
```bash
pip install flask
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

## Data Format
`contacts.json`:
```json
{
  "1": {"name": "Jane Doe", "phone": "9876543210", "email": "jane@example.com"}
}
```

CSV import/export columns: `id, name, phone, email` (id is ignored on import; new IDs are always generated to avoid collisions).
