import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from database import Database
from message_generator import generator

# ========== إعدادات ==========
TOKEN = "8664100867:AAHuQfANb8Uq42rrZtzz15bpqpCrvpZ_3QI"
ADMIN_USERNAME = "W44GW"

# حالات المحادثة
(LANG, REQUEST_USERNAME, PREVIOUS, CASE_NUMBER, VIOLATION_TYPE, SEVERITY, DATE, USERNAME_INPUT, EMAIL_INPUT, GENERATE) = range(10)

db = Database()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ========== دالة البدء ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # إذا كان المالك، نحفظ معرّف شاته الخاص
    if user.username == ADMIN_USERNAME:
        db.set_setting("owner_chat_id", str(update.message.chat_id))

    # التحقق من حالة المستخدم
    status = db.get_user_status(str(user.id))

    if status == "pending":
        await update.message.reply_text(
            "⏳ *طلبك قيد المراجعة من قبل المالك.*\n"
            "يرجى الانتظار حتى تتم الموافقة، ثم أرسل /start مرة أخرى."
        )
        return ConversationHandler.END

    if status == "rejected":
        await update.message.reply_text(
            "❌ *تم رفض طلبك.*\n"
            "إذا كنت تعتقد أن هذا خطأ، راسل المالك مباشرة."
        )
        return ConversationHandler.END

    # ترحيب + اختيار اللغة
    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await update.message.reply_text(
        "👋 مرحباً بك في بوت استرجاع حسابات إنستغرام!\n\n"
        "📌 سأساعدك في صياغة رسالة احترافية لفريق الدعم لاسترجاع حسابك.\n\n"
        "🔽 اختر لغتك المفضلة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LANG

# ========== اختيار اللغة ==========
async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    user = query.from_user

    # إذا كان المستخدم غير موافق عليه، نطلب منه إرسال يوزره
    status = db.get_user_status(str(user.id))
    if status != "approved":
        if lang == "ar":
            await query.edit_message_text(
                "🔐 *للاستخدام، يجب موافقة المالك أولاً.*\n\n"
                "📝 أرسل اسم المستخدم الخاص بك (يوزر تيليجرام أو إنستغرام):"
            )
        else:
            await query.edit_message_text(
                "🔐 *To use the bot, owner approval is required first.*\n\n"
                "📝 Send your username (Telegram or Instagram):"
            )
        return REQUEST_USERNAME

    # المستخدم موافق عليه → ننتقل مباشرة للخطوة التالية
    return await ask_previous(query, context, lang)

# ========== استقبال يوزر المستخدم وإرسال طلب الموافقة للمالك ==========
async def receive_request_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    user = update.message.from_user
    lang = context.user_data.get("lang", "ar")

    # حفظ المستخدم في قاعدة البيانات
    db.add_user(str(user.id), username)

    # إرسال إشعار للمالك
    owner_chat_id = db.get_setting("owner_chat_id")
    if owner_chat_id:
        keyboard = [
            [InlineKeyboardButton("✅ موافق", callback_data=f"approve_{user.id}")],
            [InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user.id}")]
        ]
        try:
            await context.bot.send_message(
                chat_id=owner_chat_id,
                text=(
                    f"🔔 *طلب استخدام جديد!*\n\n"
                    f"👤 اليوزر: {username}\n"
                    f"🆔 المعرف: {user.id}\n"
                    f"🌐 اللغة: {'العربية' if lang == 'ar' else 'English'}\n\n"
                    f"هل توافق على استخدامه للبوت؟"
                ),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print("خطأ في إرسال الإشعار للمالك:", e)

    # إبلاغ المستخدم
    if lang == "ar":
        await update.message.reply_text(
            "✅ *تم إرسال طلبك إلى المالك.*\n"
            "⏳ انتظر الموافقة... عندما يوافق المالك، ستصلك رسالة، ثم أرسل /start للمتابعة."
        )
    else:
        await update.message.reply_text(
            "✅ *Your request has been sent to the owner.*\n"
            "⏳ Please wait for approval... Once approved, you'll receive a message, then send /start to continue."
        )
    return ConversationHandler.END

# ========== معالجة موافقة/رفض المالك ==========
async def handle_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # التحقق أن الشخص الذي يضغط هو المالك
    if query.from_user.username != ADMIN_USERNAME:
        await query.answer("❌ فقط المالك يمكنه الموافقة!", show_alert=True)
        return

    data = query.data.split("_")
    action = data[0]  # approve or reject
    user_id = data[1]

    if action == "approve":
        db.update_user_status(user_id, "approved")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ *تمت الموافقة على طلبك!*\nأرسل /start للمتابعة."
            )
        except Exception as e:
            print("خطأ في إشعار المستخدم:", e)
        await query.edit_message_text("✅ تمت الموافقة على المستخدم!")
    else:
        db.update_user_status(user_id, "rejected")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ *تم رفض طلبك.*\nإذا كنت تعتقد أن هذا خطأ، راسل المالك."
            )
        except Exception as e:
            print("خطأ في إشعار المستخدم:", e)
        await query.edit_message_text("❌ تم رفض المستخدم.")

    return ConversationHandler.END

# ========== سؤال: هل قدمت من قبل؟ ==========
async def ask_previous(query, context, lang):
    if lang == "ar":
        text = (
            "📋 *طريقة الاستخدام:*\n\n"
            "1️⃣ أخبرني بمشكلتك (نوع الحظر).\n"
            "2️⃣ حدد نوع الحظر (خفيف ⚠️ أو شديد ❌❌❌).\n"
            "3️⃣ أدخل تاريخ الحظر.\n"
            "4️⃣ أدخل اليوزر والإيميل.\n"
            "5️⃣ سأولد لك رسالة احترافية مع إمكانية تغييرها.\n\n"
            "❓ هل سبق أن قدمت طلباً من قبل؟"
        )
        keyboard = [
            [InlineKeyboardButton("✅ نعم", callback_data="prev_yes")],
            [InlineKeyboardButton("❌ لا", callback_data="prev_no")]
        ]
    else:
        text = (
            "📋 *How to use:*\n\n"
            "1️⃣ Tell me your problem (violation type).\n"
            "2️⃣ Specify severity (light ⚠️ or severe ❌❌❌).\n"
            "3️⃣ Enter ban date.\n"
            "4️⃣ Enter username and email.\n"
            "5️⃣ I'll generate a professional message.\n\n"
            "❓ Have you submitted before?"
        )
        keyboard = [
            [InlineKeyboardButton("✅ Yes", callback_data="prev_yes")],
            [InlineKeyboardButton("❌ No", callback_data="prev_no")]
        ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return PREVIOUS

async def handle_previous(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    is_prev = query.data.split("_")[1]
    context.user_data["is_previous"] = is_prev
    lang = context.user_data.get("lang", "ar")

    if is_prev == "yes":
        if lang == "ar":
            await query.edit_message_text("📝 يرجى إرسال رقم القضية (Case Number) الخاص بطلبك السابق:")
        else:
            await query.edit_message_text("📝 Please send your previous Case Number:")
        return CASE_NUMBER
    else:
        if lang == "ar":
            await query.edit_message_text(
                "🔍 ما نوع الحظر الذي تعرض له حسابك؟\n\n"
                "اكتب النوع (مثال: عنف، احتيال، كراهية، إباحي، حقوق نشر، إلخ):"
            )
        else:
            await query.edit_message_text(
                "🔍 What violation type did your account face?\n\n"
                "Type it (e.g., violence, fraud, hate, porn, copyright, etc.):"
            )
        return VIOLATION_TYPE

# ========== استقبال رقم القضية ==========
async def receive_case_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["case_number"] = update.message.text.strip()
    lang = context.user_data.get("lang", "ar")
    if lang == "ar":
        await update.message.reply_text("✅ تم استلام رقم القضية. الآن أخبرني بنوع الحظر (مثال: عنف، احتيال، إلخ):")
    else:
        await update.message.reply_text("✅ Case number received. Now tell me the violation type (e.g., violence, fraud, etc.):")
    return VIOLATION_TYPE

# ========== استقبال نوع الحظر ==========
async def receive_violation_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    violation = update.message.text.strip()
    context.user_data["violation_type"] = violation
    lang = context.user_data.get("lang", "ar")

    if lang == "ar":
        text = (
            f"📊 فهمت أن نوع الحظر هو: *{violation}*\n\n"
            "⚠️ ما نوع الحظر الذي تعرض له حسابك؟\n"
            "[⚠️ حظر خفيف] أو [❌❌❌ حظر شديد (ثلاث إكسات)]"
        )
        keyboard = [
            [InlineKeyboardButton("⚠️ حظر خفيف", callback_data="sev_light")],
            [InlineKeyboardButton("❌❌❌ حظر شديد", callback_data="sev_severe")]
        ]
    else:
        text = (
            f"📊 I understood the violation type: *{violation}*\n\n"
            "⚠️ What is the ban severity?\n"
            "[⚠️ Light ban] or [❌❌❌ Severe ban (triple X)]"
        )
        keyboard = [
            [InlineKeyboardButton("⚠️ Light ban", callback_data="sev_light")],
            [InlineKeyboardButton("❌❌❌ Severe ban", callback_data="sev_severe")]
        ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return SEVERITY

# ========== استقبال الشدة ==========
async def receive_severity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["severity"] = query.data.split("_")[1]
    lang = context.user_data.get("lang", "ar")

    if lang == "ar":
        await query.edit_message_text(
            "📅 متى تم حظر حسابك؟\n"
            "يرجى إدخال التاريخ (مثال: 2026/05/15)\n\n"
            "📌 *تنبيه مهم:* إذا مر أكثر من 6 أشهر على الحظر، فلن تتمكن من استرجاع الحساب."
        )
    else:
        await query.edit_message_text(
            "📅 When was your account banned?\n"
            "Please enter the date (e.g., 2026/05/15)\n\n"
            "📌 *Important:* If more than 6 months have passed, the account cannot be recovered."
        )
    return DATE

# ========== استقبال التاريخ ==========
async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_input = update.message.text.strip()
    context.user_data["ban_date"] = date_input
    lang = context.user_data.get("lang", "ar")

    try:
        ban_date = datetime.strptime(date_input, "%Y/%m/%d")
        months_diff = (datetime.now() - ban_date).days / 30
        if months_diff > 6:
            if lang == "ar":
                await update.message.reply_text("❌ *عذراً:* مر أكثر من 6 أشهر على حظر حسابك، لذلك لن تتمكن من استرجاعه.")
            else:
                await update.message.reply_text("❌ *Sorry:* More than 6 months have passed, your account cannot be recovered.")
            return ConversationHandler.END
    except:
        pass

    if lang == "ar":
        await update.message.reply_text("👤 أدخل اسم المستخدم (اليوزر) الخاص بحسابك:")
    else:
        await update.message.reply_text("👤 Enter your Instagram username:")
    return USERNAME_INPUT

# ========== استقبال اليوزر ==========
async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text.strip().replace("@", "")
    lang = context.user_data.get("lang", "ar")
    if lang == "ar":
        await update.message.reply_text("📧 أدخل البريد الإلكتروني المسجل في حسابك:")
    else:
        await update.message.reply_text("📧 Enter the email registered on your account:")
    return EMAIL_INPUT

# ========== استقبال الإيميل وتوليد الرسالة ==========
async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    context.user_data["email"] = email
    lang = context.user_data.get("lang", "ar")

    data = {
        'case_number': context.user_data.get('case_number', ''),
        'username': context.user_data.get('username', ''),
        'email': email,
        'violation_type': context.user_data.get('violation_type', ''),
        'severity': context.user_data.get('severity', ''),
        'ban_date': context.user_data.get('ban_date', ''),
        'is_previous': context.user_data.get('is_previous', 'no')
    }

    message = generator.generate(data, lang)
    context.user_data["current_message"] = message
    db.add_submission({**data, 'message': message})

    if lang == "ar":
        text = "✅ *تم تجهيز رسالتك الاحترافية:*\n\n" + message
        keyboard = [
            [InlineKeyboardButton("🔄 تغيير الصيغة", callback_data="change_msg")],
            [InlineKeyboardButton("📋 نسخ الرسالة", callback_data="copy_msg")]
        ]
    else:
        text = "✅ *Your professional message is ready:*\n\n" + message
        keyboard = [
            [InlineKeyboardButton("🔄 Change", callback_data="change_msg")],
            [InlineKeyboardButton("📋 Copy", callback_data="copy_msg")]
        ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return GENERATE

# ========== تغيير الرسالة ==========
async def change_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ar")

    data = {
        'case_number': context.user_data.get('case_number', ''),
        'username': context.user_data.get('username', ''),
        'email': context.user_data.get('email', ''),
        'violation_type': context.user_data.get('violation_type', ''),
        'severity': context.user_data.get('severity', ''),
        'ban_date': context.user_data.get('ban_date', ''),
        'is_previous': context.user_data.get('is_previous', 'no')
    }

    message = generator.generate(data, lang)
    context.user_data["current_message"] = message

    if lang == "ar":
        text = "🔄 *صيغة جديدة:*\n\n" + message
        keyboard = [
            [InlineKeyboardButton("🔄 تغيير مرة أخرى", callback_data="change_msg")],
            [InlineKeyboardButton("📋 نسخ الرسالة", callback_data="copy_msg")]
        ]
    else:
        text = "🔄 *New version:*\n\n" + message
        keyboard = [
            [InlineKeyboardButton("🔄 Change again", callback_data="change_msg")],
            [InlineKeyboardButton("📋 Copy", callback_data="copy_msg")]
        ]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    return GENERATE

# ========== نسخ الرسالة ==========
async def copy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "ar")
    if lang == "ar":
        await query.answer("الرسالة جاهزة للنسخ!", show_alert=True)
    else:
        await query.answer("Message ready to copy!", show_alert=True)
    return GENERATE

# ========== أمر الإحصائيات (للمالك) ==========
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.username == ADMIN_USERNAME:
        total_subs = db.get_submission_count()
        total_users = db.get_total_users()
        pending = db.get_pending_users()
        await update.message.reply_text(
            f"📊 *لوحة التحكم*\n\n"
            f"👥 إجمالي المستخدمين: {total_users}\n"
            f"📝 إجمالي التقديمات: {total_subs}\n"
            f"⏳ بانتظار الموافقة: {len(pending)}"
        )
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANG: [CallbackQueryHandler(choose_lang)],
            REQUEST_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_request_username)],
            PREVIOUS: [CallbackQueryHandler(handle_previous)],
            CASE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_case_number)],
            VIOLATION_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_violation_type)],
            SEVERITY: [CallbackQueryHandler(receive_severity)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)],
            USERNAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)],
            EMAIL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            GENERATE: [CallbackQueryHandler(change_message, pattern='^change_msg$'),
                      CallbackQueryHandler(copy_message, pattern='^copy_msg$')],
        },
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('admin', admin_stats))
    app.add_handler(CallbackQueryHandler(handle_approval, pattern='^(approve|reject)_'))


    print("🤖 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
