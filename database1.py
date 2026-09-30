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

        # جدول المستخدمين (لنظام الموافقة)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE,
                telegram_username TEXT,
                status TEXT DEFAULT 'pending',
                requested_at TEXT DEFAULT CURRENT_TIMESTAMP
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

    # ========== المستخدمين (الموافقات) ==========
    def add_user(self, telegram_id, telegram_username):
        try:
            self.cursor.execute(
                "INSERT INTO users (telegram_id, telegram_username) VALUES (?, ?)",
                (telegram_id, telegram_username)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_status(self, telegram_id):
        self.cursor.execute("SELECT status FROM users WHERE telegram_id=?", (telegram_id,))
        row = self.cursor.fetchone()
        return row['status'] if row else None

    def update_user_status(self, telegram_id, status):
        self.cursor.execute("UPDATE users SET status=? WHERE telegram_id=?", (status, telegram_id))
        self.conn.commit()

    def get_pending_users(self):
        self.cursor.execute("SELECT * FROM users WHERE status='pending' ORDER BY id DESC")
        return self.cursor.fetchall()

    def get_total_users(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

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

    def get_total_submitters(self):
        self.cursor.execute("SELECT COUNT(DISTINCT username) FROM submissions")
        return self.cursor.fetchone()[0]

    # ========== الإعدادات ==========
    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def get_setting(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = self.cursor.fetchone()
        return row['value'] if row else None

    def close(self):
        self.conn.close()
