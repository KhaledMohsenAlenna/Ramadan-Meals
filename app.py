import streamlit as st
import requests
from datetime import datetime
import pytz

# 1. إعدادات الصفحة
st.set_page_config(page_title="Ramadan Iftar - Zewail City", layout="centered", page_icon="🌙")

# --- الرابط بتاعك (تأكد إنه آخر نسخة /exec) ---
url = "اhttps://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"

# 2. إضافة الصورة الرمضانية (رابط جديد ومستقر)
# تقدر تغير الرابط ده بأي صورة تحبها
st.image("https://img.freepik.com/free-vector/ramadan-kareem-greeting-card-design-with-mosque-crescent-moon_1017-31154.jpg", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🌙 مبادرة إفطار صائم</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>كل عام وأنتم بخير - خدمة طلاب مدينة زويل المغتربين</p>", unsafe_allow_html=True)

# 3. منطق الوقت (توقيت القاهرة)
cairo_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(cairo_tz)

# الحجز يفتح من 12 بليل (0) لحد 4:30 عصراً (16:30)
is_open = False
if 0 <= now.hour < 16:
    is_open = True
elif now.hour == 16 and now.minute < 30:
    is_open = True

# 4. لوحة تحكم المسؤولين (في الشريط الجانبي)
with st.sidebar:
    st.header("🛠️ لوحة التحكم")
    if st.checkbox("دخول الإدمن"):
        admin_pw = st.text_input("كلمة السر", type="password")
        if admin_pw == "Zewail2026":
            st.info("مرحباً يا أدمن، يمكنك حذف حجز أي طالب هنا.")
            del_email = st.text_input("إيميل الطالب المراد حذفه")
            if st.button("تأكيد الحذف النهائي"):
                with st.spinner("جاري الحذف..."):
                    res = requests.post(url, json={"action": "delete", "email": del_email})
                    if res.status_code == 200:
                        st.success(f"تم حذف الإيميل {del_email} بنجاح من الشيت.")
                    else:
                        st.error("حدث خطأ أو الإيميل غير موجود.")

# 5. واجهة المستخدم الرئيسية
if not is_open:
    st.error(f"⛔ انتهى وقت الحجز لليوم. الساعة الآن {now.strftime('%I:%M %p')}")
    st.info("يفتح باب الحجز لليوم التالي في تمام الساعة 12:00 منتصف الليل.")
else:
    st.success("✅ باب الحجز مفتوح الآن لطلاب المدينة")
    with st.form("iftar_form", clear_on_submit=True):
        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
        
        locations = [
            "عماير القرية الكونية (عمو صبرى)", 
            "الفيروز / المنطقة التالتة",
            "سكن الجامعة (Dorms)"
        ]
        location = st.selectbox("مكان الاستلام", locations)
        
        gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (لسكان السكن الجامعي)")
        
        submit = st.form_submit_button("إرسال طلب الحجز")

        if submit:
            if not name or not student_id or not email:
                st.warning("⚠️ يرجى ملء البيانات الأساسية.")
            elif not email.lower().endswith("@zewailcity.edu.eg"):
                st.error("❌ عذراً، يجب استخدام الإيميل الجامعي الرسمي لمدينة زويل.")
            else:
                data = {
                    "name": name,
                    "id": student_id,
                    "email": email,
                    "location": location,
                    "gender": gender,
                    "room": room
                }
                with st.spinner("جاري تسجيل طلبك..."):
                    try:
                        res = requests.post(url, json=data)
                        res_data = res.json()
                        
                        if res_data.get("result") == "success":
                            st.balloons()
                            st.success(f"تقبل الله منا ومنكم يا {name.split()[0]}! تم تسجيل وجبتك بنجاح. رمضان كريم 🌙✨")
                        elif res_data.get("message") == "duplicate":
                            st.warning("⚠️ عفواً، هذا الإيميل مسجل لدينا بالفعل لهذا اليوم. مسموح بوجبة واحدة فقط لكل طالب.")
                    except:
                        st.error("❌ فشل الاتصال بالسيرفر. تأكد من تحديث رابط الـ Script.")
