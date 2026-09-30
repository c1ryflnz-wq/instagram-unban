import random
import re
from datetime import datetime

class SmartMessageGenerator:
    """خوارزمية ذكية محلية تحلل مشكلة المستخدم وتولد رسائل ديناميكية متغيرة باستمرار"""
    
    def __init__(self):
        # كلمات مفتاحية عربية لفهم أنواع الحظر
        self.violation_keywords = {
            'porn': ['اباحي', 'اباحية', 'porn', 'sex', 'جنسي', 'إباحي', 'نشاط جنسي', 'jinsi', 'ibahi', 'محتوى جنسي'],
            'violence': ['عنف', 'عنيف', 'violence', 'قتال', 'إيذاء', 'اعتداء', 'تهديد', 'unf', 'aenaef', 'ضرب'],
            'fraud': ['احتيال', 'خداع', 'نصب', 'fraud', 'scam', 'احتيالية', 'نشاط احتيالي', 'ihtial', 'khadae', 'نصب واحتيال'],
            'hate': ['كراهية', 'كراهية', 'عنصرية', 'hate', 'تمييز', 'تنمر', 'كراها', 'karahia', 'عنصري', 'حقد'],
            'spam': ['سبام', 'مزعج', 'spam', 'بريد مزعج', 'نشر مزعج', 'إزعاج', 'sibam'],
            'copyright': ['حقوق نشر', 'ملكية فكرية', 'copyright', 'انتهاك', 'copy', 'huquq', 'محتوى مسروق'],
            'impersonation': ['انتحال شخصية', 'مزيف', 'impersonation', 'حساب مزيف', 'انتحال', 'intihal shakhsia'],
            'other': ['أخرى', 'آخر', 'other', 'غير ذلك', 'لا أعرف', 'مشكلة أخرى']
        }
        
        # نبرات مختلفة لتوليد رسائل متنوعة
        self.tone_words_ar = {
            'formal': ['المحترم', 'الفاضل', 'الموقر', 'المكرم'],
            'polite': ['أرجو', 'أطلب', 'ألتمس', 'أتمنى'],
            'clarify': ['أود أن أوضح', 'أشير إلى', 'أؤكد', 'أوضح'],
            'closing': ['مع جزيل الشكر والتقدير', 'شاكرًا لكم حسن تعاونكم', 'مع خالص الاحترام', 'مقدرًا جهودكم']
        }
        
        self.tone_words_en = {
            'formal': ['Respected', 'Dear', 'Honored', 'Distinguished'],
            'polite': ['I kindly request', 'I respectfully ask', 'I sincerely request', 'I politely request'],
            'clarify': ['I would like to clarify', 'I wish to point out', 'I confirm', 'I would like to state'],
            'closing': ['With sincere thanks and appreciation', 'Thank you for your kind cooperation', 'With all due respect', 'Appreciating your efforts']
        }
        
        # قوالب تركيب الجمل المتقدمة
        self.sentence_structures_ar = [
            "{greeting}، {intro} {username} {clarify} {situation}. {reason} {severity_text}. {date_text} {request} {closing}، {username}",
            "{greeting}، {subject} {username}. {clarify2} {details}. {ban_info} {action_request} {thanks}، {username}",
            "{greeting}، {statement} {username} ({email}). {clause} {ban_type} {time_info}. {plea} {gratitude}، {username}"
        ]
        
        self.sentence_structures_en = [
            "{greeting}, {intro} {username} {clarify} {situation}. {reason} {severity_text}. {date_text} {request} {closing}, {username}",
            "{greeting}, {subject} {username}. {clarify2} {details}. {ban_info} {action_request} {thanks}, {username}",
            "{greeting}, {statement} {username} ({email}). {clause} {ban_type} {time_info}. {plea} {gratitude}, {username}"
        ]

    def analyze_text(self, user_text, lang="ar"):
        """تحليل نص المستخدم لفهم نوع الحظر تلقائيًا"""
        user_text = user_text.lower()
        detected_type = 'other'
        confidence = 0
        
        for vtype, keywords in self.violation_keywords.items():
            match_count = sum(1 for kw in keywords if kw in user_text)
            if match_count > confidence:
                confidence = match_count
                detected_type = vtype
        
        # تحليل الشدة من النص
        severity = 'light'
        if any(kw in user_text for kw in ['شديد', 'ثلاث', 'xxx', 'ثلاثة x', 'شديدة', 'severe', 'triple']):
            severity = 'severe'
        
        # تحليل التاريخ من النص
        date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', user_text)
        ban_date = date_match.group(1) if date_match else ''
        
        # تحليل رقم القضية
        case_match = re.search(r'(?:قضية|case)[\s:]*([0-9]+)', user_text, re.IGNORECASE)
        case_number = case_match.group(1) if case_match else ''
        
        return {
            'violation_type': detected_type,
            'severity': severity,
            'ban_date': ban_date,
            'case_number': case_number,
            'confidence': confidence
        }

    def extract_user_info(self, user_text, lang="ar"):
        """استخراج اسم المستخدم والبريد تلقائيًا من النص"""
        username = ''
        email = ''
        
        # استخراج اليوزر
        user_match = re.search(r'[@＠]([a-zA-Z0-9_.]+)', user_text)
        if user_match:
            username = user_match.group(1)
        
        # استخراج البريد الإلكتروني
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_text)
        if email_match:
            email = email_match.group(0)
        
        return username, email

    def get_violation_name(self, vtype, lang="ar"):
        """ترجمة نوع الحظر لاسم واضح"""
        names = {
            'porn': ('محتوى إباحي', 'pornographic content'),
            'violence': ('عنف أو تهديد', 'violence or threats'),
            'fraud': ('احتيال وخداع', 'fraud and deception'),
            'hate': ('كراهية أو عنصرية', 'hate speech or racism'),
            'spam': ('سبام أو إزعاج', 'spam or nuisance'),
            'copyright': ('انتهاك حقوق النشر', 'copyright infringement'),
            'impersonation': ('انتحال شخصية', 'impersonation'),
            'other': ('أخرى', 'other')
        }
        return names.get(vtype, names['other'])[0 if lang=='ar' else 1]

    def generate(self, data, lang="ar"):
        """
        توليد رسالة ذكية ديناميكية تتغير باستمرار
        data يحتوي: violation_type, severity, ban_date, username, email, case_number, is_previous
        """
        violation_type = self.get_violation_name(data.get('violation_type', 'other'), lang)
        severity = data.get('severity', 'light')
        ban_date = data.get('ban_date', '')
        username = data.get('username', '')
        email = data.get('email', '')
        case_number = data.get('case_number', '')
        is_previous = data.get('is_previous', 'no')

        if lang == "ar":
            return self._build_ar_message(violation_type, severity, ban_date, username, email, case_number, is_previous)
        else:
            return self._build_en_message(violation_type, severity, ban_date, username, email, case_number, is_previous)

    def _build_ar_message(self, vtype, severity, ban_date, username, email, case_number, is_previous):
        t = self.tone_words_ar
        severity_text = "حظر خفيف" if severity == 'light' else "حظر شديد (ثلاث إكسات)"
        
        # حالة مراجعة قضية سابقة
        if is_previous == "yes" and case_number:
            greeting = random.choice(['إلى فريق دعم إنستغرام المحترم', 'عزيزي فريق الدعم الفني', 'تحية طيبة لفريق إنستغرام'])
            subject = f"الموضوع: طلب مراجعة رقم القضية {case_number}"
            return f"""{greeting}،

{subject}

أتواصل معكم بخصوص رقم القضية {case_number} الخاص بحسابي @{username} الذي تم حظره.

نوع الحظر: {vtype}
نوع الحظر: {severity_text}
تاريخ الحظر: {ban_date}
البريد الإلكتروني: {email}

أطلب منكم {random.choice(t['polite'])} إعادة النظر في هذه القضية، حيث أنني {random.choice(t['clarify'])} أن الحظر تم بدون سبب مشروع.

{random.choice(t['closing'])}،
{username}"""

        # حالة عادية
        structure = random.choice(self.sentence_structures_ar)
        
        parts = {
            'greeting': random.choice(['إلى فريق دعم إنستغرام المحترم', 'عزيزي فريق الدعم الفني', 'تحية طيبة لفريق إنستغرام']),
            'intro': random.choice(['أتواصل معكم بخصوص حسابي', 'أكتب إليكم بخصوص حسابي', 'أراسلكم بخصوص الحساب']),
            'username': f"@{username}",
            'clarify': random.choice(['الذي تم حظره', 'الذي تعرض للحظر', 'الذي تم تعطيله']),
            'situation': random.choice(['بدون سبب واضح', 'بشكل مفاجئ', 'لأسباب غير معروفة']),
            'reason': f"نوع الحظر المذكور: {vtype}",
            'severity_text': f"نوع الحظر: {severity_text}",
            'date_text': f"تاريخ الحظر: {ban_date}" if ban_date else "تاريخ الحظر: غير محدد",
            'request': random.choice(['أرجو منكم مراجعة الحساب وإعادة تفعيله', 'أطلب إعادة النظر في قرار الحظر', 'ألتمس إعادة تفعيل حسابي']),
            'closing': random.choice(t['closing']),
            'subject': f"الموضوع: طلب استرجاع حساب تم حظره",
            'clarify2': random.choice(['أود أن أوضح', 'أشير إلى', 'أؤكد']),
            'details': f"أنني لم أنتهك سياسات المنصة وأن الحظر كان خاطئاً",
            'ban_info': f"حسابي @{username} (البريد: {email}) تعرض لـ({vtype}) بنوع ({severity_text}) بتاريخ {ban_date}",
            'action_request': 'أطلب منكم إعادة النظر في القرار وإعادة حسابي.',
            'thanks': random.choice(['شكراً لتفهمكم', 'مع جزيل الشكر', 'أشكركم على وقتكم']),
            'statement': 'أكتب لكم بخصوص حسابي',
            'email': email,
            'clause': f'الذي تم حظره بتهمة',
            'ban_type': vtype,
            'time_info': f'بشكل {severity_text}',
            'plea': random.choice(['أرجو منكم النظر في طلبي', 'أتمنى منكم الموافقة على طلبي']),
            'gratitude': random.choice(['مع الاحترام', 'شاكرًا لكم', 'مقدرًا تعاونكم'])
        }
        
        message = structure.format(**parts)
        
        # إضافة البريد إذا وجد
        if email:
            message += f"\n\nالبريد الإلكتروني: {email}"
        
        return message

    def _build_en_message(self, vtype, severity, ban_date, username, email, case_number, is_previous):
        t = self.tone_words_en
        severity_text = "light ban" if severity == 'light' else "severe ban (triple X)"
        
        if is_previous == "yes" and case_number:
            greeting = random.choice(['Dear Instagram Support Team', 'Dear Support Team', 'Dear Instagram Team'])
            return f"""{greeting},

Subject: Request for review of case number {case_number}

I am contacting you regarding case number {case_number} for my account @{username} which was banned.

Violation type: {vtype}
Ban severity: {severity_text}
Ban date: {ban_date}
Email: {email}

I {random.choice(t['polite'])} a reconsideration of this case, as I {random.choice(t['clarify'])} the ban was not justified.

{random.choice(t['closing'])},
{username}"""

        structure = random.choice(self.sentence_structures_en)
        
        parts = {
            'greeting': random.choice(['Dear Instagram Support Team', 'Dear Support Team', 'Dear Instagram Team']),
            'intro': random.choice(['I am contacting you regarding my account', 'I am writing to you about my account', 'I am reaching out regarding my account']),
            'username': f"@{username}",
            'clarify': random.choice(['which was banned', 'which was disabled', 'which was blocked']),
            'situation': random.choice(['without a clear reason', 'unexpectedly', 'for unknown reasons']),
            'reason': f"Stated violation: {vtype}",
            'severity_text': f"Ban severity: {severity_text}",
            'date_text': f"Ban date: {ban_date}" if ban_date else "Ban date: not specified",
            'request': random.choice(['Please review my account and reactivate it', 'I request a reconsideration of the ban decision', 'I kindly ask for reactivation of my account']),
            'closing': random.choice(t['closing']),
            'subject': "Subject: Request to restore banned account",
            'clarify2': random.choice(['I would like to clarify', 'I wish to point out', 'I confirm']),
            'details': "that I have not violated the platform policies and the ban was a mistake",
            'ban_info': f"My account @{username} (email: {email}) was banned for ({vtype}) with ({severity_text}) on {ban_date}",
            'action_request': 'I request a reconsideration and restoration of my account.',
            'thanks': random.choice(['Thank you for your understanding', 'Thank you very much', 'Thank you for your time']),
            'statement': 'I am writing about my account',
            'email': email,
            'clause': 'which was banned for',
            'ban_type': vtype,
            'time_info': f'with {severity_text}',
            'plea': random.choice(['Please consider my request', 'I hope you will approve my request']),
            'gratitude': random.choice(['Best regards', 'Thank you', 'Appreciating your cooperation'])
        }
        
        message = structure.format(**parts)
        
        if email:
            message += f"\n\nEmail: {email}"
        
        return message

# إنشاء نسخة عامة
generator = SmartMessageGenerator()
