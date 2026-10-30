
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "campuscare-secret-key"

# Database configuration
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "complaints.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            department TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# HOME PAGE / DASHBOARD
# ==========================================

@app.route("/")
def home():

    conn = get_db_connection()

    total = conn.execute(
        "SELECT COUNT(*) FROM complaints"
    ).fetchone()[0]

    pending = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Pending'"
    ).fetchone()[0]

    verified = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Verified'"
    ).fetchone()[0]

    in_progress = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'"
    ).fetchone()[0]

    resolved = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'"
    ).fetchone()[0]

    recent = conn.execute("""
        SELECT * FROM complaints
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        total=total,
        pending=pending,
        verified=verified,
        in_progress=in_progress,
        resolved=resolved,
        recent=recent
    )


# ==========================================
# SUBMIT COMPLAINT
# ==========================================

@app.route("/submit", methods=["GET", "POST"])
def submit_complaint():

    if request.method == "POST":

        student_name = request.form.get("student_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        department = request.form.get("department", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        # Validate form data
        if not all([
            student_name,
            roll_number,
            department,
            category,
            description
        ]):
            flash("Please fill in all fields.", "error")
            return redirect(url_for("submit_complaint"))

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO complaints
            (student_name, roll_number, department, category, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_name,
            roll_number,
            department,
            category,
            description
        ))

        conn.commit()
        conn.close()

        flash(
            "Your complaint has been submitted successfully!",
            "success"
        )

        return redirect(url_for("track_complaints"))

    return render_template("submit.html")


# ==========================================
# TRACK COMPLAINTS
# ==========================================

@app.route("/track")
def track_complaints():

    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    if search:

        complaints = conn.execute("""
            SELECT * FROM complaints
            WHERE roll_number LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%",)).fetchall()

    else:

        complaints = conn.execute("""
            SELECT * FROM complaints
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "track.html",
        complaints=complaints,
        search=search
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin_dashboard():

    conn = get_db_connection()

    complaints = conn.execute("""
        SELECT * FROM complaints
        ORDER BY id DESC
    """).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM complaints"
    ).fetchone()[0]

    pending = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Pending'"
    ).fetchone()[0]

    verified = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Verified'"
    ).fetchone()[0]

    in_progress = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'"
    ).fetchone()[0]

    resolved = conn.execute(
        "SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        complaints=complaints,
        total=total,
        pending=pending,
        verified=verified,
        in_progress=in_progress,
        resolved=resolved
    )


# ==========================================
# UPDATE COMPLAINT STATUS
# ==========================================

@app.route(
    "/admin/update/<int:complaint_id>",
    methods=["POST"]
)
def update_complaint_status(complaint_id):

    new_status = request.form.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "Verified",
        "In Progress",
        "Resolved"
    ]

    if new_status not in allowed_statuses:

        flash("Invalid complaint status.", "error")

        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection()

    complaint = conn.execute(
        "SELECT id FROM complaints WHERE id = ?",
        (complaint_id,)
    ).fetchone()

    if complaint is None:

        conn.close()

        flash("Complaint not found.", "error")

        return redirect(url_for("admin_dashboard"))

    conn.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """, (new_status, complaint_id))

    conn.commit()
    conn.close()

    flash(
        "Complaint status updated successfully!",
        "success"
    )

    return redirect(url_for("admin_dashboard"))


# ==========================================
# START APPLICATION
# ==========================================

initialize_database()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
