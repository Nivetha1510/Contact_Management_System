"""
Contact Management System - Core Logic
-----------------------------------------
Validation (regex), JSON storage, CSV import/export, and CRUD
operations. This module has no console/menu code - it is imported
by the Flask app instead of running as a script.

Author: Nivetha S
"""

import json
import csv
import os
import re

JSON_FILE = "contacts.json"

# Regex patterns
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_PATTERN = re.compile(r"^\+?\d{1,3}?[-.\s]?\d{10}$|^\+?\d{1,3}?[-.\s]?\d{5}[-.\s]?\d{5}$")


# --------------------------------------------------------------------
# VALIDATION (Regex)
# --------------------------------------------------------------------
def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email))


def is_valid_phone(phone):
    # Normalize by stripping spaces/dashes for a simpler core check too
    digits_only = re.sub(r"[^\d+]", "", phone)
    return bool(re.match(r"^\+?\d{10,13}$", digits_only))


# --------------------------------------------------------------------
# FILE HANDLING: JSON (primary storage)
# --------------------------------------------------------------------
def load_contacts():
    """Load contacts dict from JSON: {contact_id: {name, phone, email}}."""
    if not os.path.exists(JSON_FILE):
        return {}
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: could not read contacts file ({e}). Starting fresh.")
        return {}


def save_contacts(contacts):
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(contacts, f, indent=4)
    except IOError as e:
        print(f"Error saving contacts: {e}")


# --------------------------------------------------------------------
# FILE HANDLING: CSV (export / import)
# --------------------------------------------------------------------
def export_to_csv(contacts, filepath):
    try:
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "phone", "email"])
            for contact_id, info in contacts.items():
                writer.writerow([contact_id, info["name"], info["phone"], info["email"]])
        return True
    except IOError as e:
        print(f"Error exporting to CSV: {e}")
        return False


def import_from_csv(contacts, filepath):
    """
    Import contacts from a CSV file with columns: name, phone, email
    (id column optional/ignored - new IDs are always generated to avoid collisions).
    Returns (added_count, skipped_count).
    """
    if not os.path.exists(filepath):
        print(f"File '{filepath}' not found.")
        return 0, 0

    added, skipped = 0, 0
    try:
        with open(filepath, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                phone = row.get("phone", "").strip()
                email = row.get("email", "").strip()

                if not name or not is_valid_phone(phone) or not is_valid_email(email):
                    skipped += 1
                    continue

                new_id = generate_id(contacts)
                contacts[new_id] = {"name": name, "phone": phone, "email": email}
                added += 1
        save_contacts(contacts)
        return added, skipped
    except (IOError, csv.Error) as e:
        print(f"Error importing CSV: {e}")
        return added, skipped


# --------------------------------------------------------------------
# CRUD OPERATIONS
# --------------------------------------------------------------------
def generate_id(contacts):
    """Generate the next numeric contact ID as a string."""
    if not contacts:
        return "1"
    existing_ids = [int(cid) for cid in contacts.keys() if cid.isdigit()]
    return str(max(existing_ids, default=0) + 1)


def create_contact(contacts, name, phone, email):
    if not name.strip():
        raise ValueError("Name cannot be empty.")
    if not is_valid_phone(phone):
        raise ValueError(f"Invalid phone number: '{phone}'.")
    if not is_valid_email(email):
        raise ValueError(f"Invalid email address: '{email}'.")

    # Prevent exact duplicate (same name + phone)
    for info in contacts.values():
        if info["name"].lower() == name.lower() and info["phone"] == phone:
            raise ValueError(f"Contact '{name}' with this phone number already exists.")

    contact_id = generate_id(contacts)
    contacts[contact_id] = {"name": name.strip(), "phone": phone.strip(), "email": email.strip()}
    save_contacts(contacts)
    return contact_id


def read_contact(contacts, contact_id):
    if contact_id not in contacts:
        raise KeyError(f"Contact ID '{contact_id}' not found.")
    return contacts[contact_id]


def search_contacts(contacts, keyword):
    """Case-insensitive search across name, phone, and email."""
    keyword = keyword.lower()
    results = {}
    for contact_id, info in contacts.items():
        if (keyword in info["name"].lower()
                or keyword in info["phone"].lower()
                or keyword in info["email"].lower()):
            results[contact_id] = info
    return results


def update_contact(contacts, contact_id, name=None, phone=None, email=None):
    if contact_id not in contacts:
        raise KeyError(f"Contact ID '{contact_id}' not found.")

    contact = contacts[contact_id]
    if name is not None and name.strip():
        contact["name"] = name.strip()
    if phone is not None and phone.strip():
        if not is_valid_phone(phone):
            raise ValueError(f"Invalid phone number: '{phone}'.")
        contact["phone"] = phone.strip()
    if email is not None and email.strip():
        if not is_valid_email(email):
            raise ValueError(f"Invalid email address: '{email}'.")
        contact["email"] = email.strip()

    save_contacts(contacts)


def delete_contact(contacts, contact_id):
    if contact_id not in contacts:
        raise KeyError(f"Contact ID '{contact_id}' not found.")
    del contacts[contact_id]
    save_contacts(contacts)
