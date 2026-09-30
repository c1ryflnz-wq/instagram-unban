import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path="database.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # جدول المشرفين (المالك + المشرفين)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول التقديمات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT UNIQUE,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                severity TEXT,
                ban_date TEXT,
                is_previous TEXT,
                message TEXT,
                status TEXT DEFAULT 'pending',
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول إعدادات النظام
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        self.conn.commit()

    # ========== المشرفين ==========
    def add_admin(self, username, password, role='admin'):
        try:
            self.cursor.execute(
                "INSERT INTO admins (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def check_admin(self, username, password):
        self.cursor.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        )
        return self.cursor.fetchone()

    def get_all_admins(self):
        self.cursor.execute("SELECT * FROM admins")
        return self.cursor.fetchall()

    def delete_admin(self, admin_id):
        self.cursor.execute("DELETE FROM admins WHERE id=? AND role != 'owner'", (admin_id,))
        self.conn.commit()

    # ========== التقديمات ==========
    def add_submission(self, data):
        self.cursor.execute("""
            INSERT INTO submissions 
            (case_number, username, email, violation_type, severity, ban_date, is_previous, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('case_number'),
            data.get('username'),
            data.get('email'),
            data.get('violation_type'),
            data.get('severity'),
            data.get('ban_date'),
            data.get('is_previous'),
            data.get('message')
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_submissions(self):
        self.cursor.execute("SELECT * FROM submissions ORDER BY id DESC")
        return self.cursor.fetchall()

    def get_submission_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM submissions")
        return self.cursor.fetchone()[0]

    def update_submission_status(self, sub_id, status):
        self.cursor.execute("UPDATE submissions SET status=? WHERE id=?", (status, sub_id))
        self.conn.commit()

    def get_total_users(self):
        self.cursor.execute("SELECT COUNT(DISTINCT username) FROM submissions")
        return self.cursor.fetchone()[0]

    def close(self):
        self.conn.close()
