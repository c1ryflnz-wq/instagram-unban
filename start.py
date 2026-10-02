import subprocess
import sys
import os

# تثبيت المكتبات
print("📦 جاري تثبيت المكتبات...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# تشغيل البوت في الخلفية
print("🤖 جاري تشغيل البوت...")
bot_process = subprocess.Popen([sys.executable, "bot.py"])

# تشغيل الخادم
print("🌐 جاري تشغيل الخادم...")
os.system(f"{sys.executable} app.py")
