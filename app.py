from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import Database
from message_generator import generator
import os

app = Flask(__name__)
app.secret_key = "supersecretkey_instagram_unban_2026"

db = Database()

# ========== إعدادات المالك ==========
OWNER_USERNAME = "W44GW"
OWNER_PASSWORD = "owner12345"  # ← غيّر كلمة المرور هذه!

# ========== الصفحة الرئيسية (للمستخدمين) ==========
@app.route("/")
def index():
    return render_template("index.html")

# ========== معالجة طلب المستخدم من الموقع ==========
@app.route("/generate", methods=["POST"])
def generate():
    data = {
        'case_number': request.form.get('case_number', ''),
        'username': request.form.get('username', ''),
        'email': request.form.get('email', ''),
        'violation_type': request.form.get('violation_type', ''),
        'severity': request.form.get('severity', 'light'),
        'ban_date': request.form.get('ban_date', ''),
        'is_previous': request.form.get('is_previous', 'no')
    }
    lang = request.form.get('lang', 'ar')
    
    # توليد الرسالة
    message = generator.generate(data, lang)
    
    # حفظ التقديم
    db.add_submission({**data, 'message': message})
    
    return jsonify({'message': message})

# ========== صفحة تسجيل دخول المشرفين ==========
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        # التحقق من المالك
        if username == OWNER_USERNAME and password == OWNER_PASSWORD:
            session['admin'] = username
            session['role'] = 'owner'
            return redirect(url_for('admin'))
        
        # التحقق من المشرفين المضافين
        admin = db.check_admin(username, password)
        if admin:
            session['admin'] = admin['username']
            session['role'] = admin['role']
            return redirect(url_for('admin'))
        
        return render_template("login.html", error="بيانات الدخول غير صحيحة")
    
    return render_template("login.html")

# ========== لوحة التحكم ==========
@app.route("/admin")
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    total_subs = db.get_submission_count()
    total_users = db.get_total_users()
    submissions = db.get_all_submissions()
    admins = db.get_all_admins()
    pending_users = db.get_pending_users()
    
    return render_template(
        "admin.html",
        total_subs=total_subs,
        total_users=total_users,
        submissions=submissions,
        admins=admins,
        pending_users=pending_users,
        role=session.get('role')
    )

# ========== إضافة مشرف جديد ==========
@app.route("/add_admin", methods=["POST"])
def add_admin():
    if 'admin' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    if db.add_admin(username, password, 'admin'):
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('admin'))

# ========== حذف مشرف ==========
@app.route("/delete_admin/<int:admin_id>", methods=["POST"])
def delete_admin(admin_id):
    if 'admin' not in session or session.get('role') != 'owner':
        return redirect(url_for('login'))
    
    db.delete_admin(admin_id)
    return redirect(url_for('admin'))

# ========== تحديث حالة تقديم ==========
@app.route("/update_status/<int:sub_id>/<status>", methods=["POST"])
def update_status(sub_id, status):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    db.update_submission_status(sub_id, status)
    return redirect(url_for('admin'))

# ========== تسجيل الخروج ==========
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========== تشغيل الخادم ==========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
