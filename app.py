"""
Contact Management System - Flask Web App
--------------------------------------------
Replaces the console menu with routes: the list/search screen, add
form, edit form, delete action, and CSV export/import all render
HTML templates instead of printing to a terminal.

Run with:
    python app.py
Then open http://127.0.0.1:5000
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import contact_core as core

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret-key"

UPLOAD_FOLDER = "uploads"
EXPORT_FOLDER = "exports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# In-memory contacts dict, backed by contacts.json
contacts = core.load_contacts()


@app.route("/")
def index():
    """List all contacts, or search results if a keyword was given."""
    keyword = request.args.get("q", "").strip()
    results = core.search_contacts(contacts, keyword) if keyword else contacts
    return render_template("index.html", contacts=results, keyword=keyword)


@app.route("/add", methods=["POST"])
def add_contact():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    try:
        contact_id = core.create_contact(contacts, name, phone, email)
        flash(f"Contact added successfully with ID {contact_id}.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("index"))


@app.route("/edit/<contact_id>", methods=["GET", "POST"])
def edit_contact(contact_id):
    try:
        existing = core.read_contact(contacts, contact_id)
    except KeyError as e:
        flash(str(e), "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        try:
            core.update_contact(contacts, contact_id,
                                 name=name or None, phone=phone or None, email=email or None)
            flash("Contact updated successfully.", "success")
            return redirect(url_for("index"))
        except ValueError as e:
            flash(str(e), "error")

    return render_template("edit.html", contact_id=contact_id, contact=existing)


@app.route("/delete/<contact_id>", methods=["POST"])
def delete_contact(contact_id):
    try:
        core.delete_contact(contacts, contact_id)
        flash(f"Contact ID {contact_id} deleted.", "success")
    except KeyError as e:
        flash(str(e), "error")
    return redirect(url_for("index"))


@app.route("/export")
def export_contacts():
    """Write contacts to CSV and let the browser download it."""
    filepath = os.path.join(EXPORT_FOLDER, "contacts_export.csv")
    if core.export_to_csv(contacts, filepath):
        return send_file(filepath, as_attachment=True, download_name="contacts_export.csv")
    flash("Error exporting contacts.", "error")
    return redirect(url_for("index"))


@app.route("/import", methods=["POST"])
def import_contacts():
    """Accept an uploaded CSV file (name, phone, email columns) and import it."""
    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("Please choose a CSV file to import.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    added, skipped = core.import_from_csv(contacts, filepath)
    flash(f"Import complete: {added} added, {skipped} skipped (invalid or missing data).", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
