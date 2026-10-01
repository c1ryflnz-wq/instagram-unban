#!/bin/bash

# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل البوت في الخلفية
python bot.py &

# تشغيل الخادم
python app.py
