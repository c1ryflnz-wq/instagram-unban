// متغيرات عامة
let currentLang = 'ar';
let currentData = {};

// ========== اختيار اللغة ==========
function setLang(lang) {
    currentLang = lang;
    document.getElementById('lang-section').style.display = 'none';
    document.getElementById('form-section').style.display = 'block';
    
    if (lang === 'ar') {
        document.getElementById('form-title').textContent = '📝 أدخل بياناتك';
        document.getElementById('label-username').textContent = '👤 اسم المستخدم (اليوزر):';
        document.getElementById('label-email').textContent = '📧 البريد الإلكتروني:';
        document.getElementById('label-type').textContent = '🔍 نوع الحظر:';
        document.getElementById('label-severity').textContent = '⚠️ نوع الحظر:';
        document.getElementById('label-date').textContent = '📅 تاريخ الحظر:';
        document.getElementById('label-prev').textContent = '❓ هل قدمت طلباً من قبل؟';
        document.getElementById('label-case').textContent = '📝 رقم القضية:';
        document.getElementById('violation_type').placeholder = 'مثال: عنف، احتيال، كراهية...';
        document.querySelector('.primary-btn').textContent = '✨ توليد الرسالة';
    } else {
        document.getElementById('form-title').textContent = '📝 Enter your data';
        document.getElementById('label-username').textContent = '👤 Username:';
        document.getElementById('label-email').textContent = '📧 Email:';
        document.getElementById('label-type').textContent = '🔍 Violation type:';
        document.getElementById('label-severity').textContent = '⚠️ Ban severity:';
        document.getElementById('label-date').textContent = '📅 Ban date:';
        document.getElementById('label-prev').textContent = '❓ Have you submitted before?';
        document.getElementById('label-case').textContent = '📝 Case Number:';
        document.getElementById('violation_type').placeholder = 'e.g., violence, fraud, hate...';
        document.querySelector('.primary-btn').textContent = '✨ Generate Message';
    }
}

// ========== إظهار/إخفاء حقل رقم القضية ==========
document.addEventListener('change', function(e) {
    if (e.target.id === 'is_previous') {
        const caseGroup = document.getElementById('case-group');
        if (e.target.value === 'yes') {
            caseGroup.style.display = 'block';
        } else {
            caseGroup.style.display = 'none';
        }
    }
});

// ========== توليد الرسالة ==========
async function generateMessage() {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const violation_type = document.getElementById('violation_type').value.trim();
    const severity = document.getElementById('severity').value;
    const ban_date = document.getElementById('ban_date').value;
    const is_previous = document.getElementById('is_previous').value;
    const case_number = document.getElementById('case_number').value.trim();

    // التحقق من الحقول
    if (!username || !email || !violation_type) {
        alert(currentLang === 'ar' ? 'يرجى ملء جميع الحقول المطلوبة' : 'Please fill all required fields');
        return;
    }

    currentData = {
        username: username,
        email: email,
        violation_type: violation_type,
        severity: severity,
        ban_date: ban_date,
        is_previous: is_previous,
        case_number: case_number,
        lang: currentLang
    };

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(currentData)
        });

        const result = await response.json();
        document.getElementById('result-message').value = result.message;
        document.getElementById('result-section').style.display = 'block';
        document.getElementById('form-section').style.display = 'none';
    } catch (error) {
        alert(currentLang === 'ar' ? 'حدث خطأ، حاول مرة أخرى' : 'An error occurred, try again');
    }
}

// ========== تغيير الصيغة ==========
async function changeMessage() {
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(currentData)
        });

        const result = await response.json();
        document.getElementById('result-message').value = result.message;
    } catch (error) {
        alert(currentLang === 'ar' ? 'حدث خطأ، حاول مرة أخرى' : 'An error occurred, try again');
    }
}

// ========== نسخ الرسالة ==========
function copyMessage() {
    const message = document.getElementById('result-message');
    message.select();
    message.setSelectionRange(0, 99999);
    
    navigator.clipboard.writeText(message.value).then(function() {
        alert(currentLang === 'ar' ? '✅ تم نسخ الرسالة!' : '✅ Message copied!');
    });
}
