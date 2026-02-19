import streamlit as st
import requests
from datetime import datetime
import pytz

# 1. إعدادات الصفحة
st.set_page_config(page_title="Ramadan Iftar - Zewail City", layout="centered", page_icon="🌙")

# رابط جوجل سكريبت (حط اللينك بتاعك هنا)
url = "اhttps://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"

# 2. صورة رمضانية (GIF)
st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJtZnd4eGZyeGZyeGZyeGZyeGZyeGZyeGZyeGZyeGZyeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LpALgGQNZLz9yvVdQu/giphy.gif", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>🌙 مبادرة إفطار صائم</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>كل عام وأنتم بخير - خدمة طلاب مدينة زويل المغتربين</p>", unsafe_allow_html=True)

# 3. منطق الوقت (الفتح 12 ص، القفل 4:30 م)
cairo_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(cairo_tz)
is_open = False
if 0 <= now.hour < 16: is_open = True
elif now.hour == 16 and now.minute < 30: is_open = True

# 4. لوحة تحكم الـ Admin (مخفية في الجنب)
with st.sidebar:
    st.header("⚙️ الإدارة")
    if st.checkbox("دخول المسؤولين"):
        admin_pw = st.text_input("كلمة السر", type="password")
        if admin_pw == "Zewail2026": # كلمة السر
            del_email = st.text_input("إيميل الطالب للحذف")
            if st.button("حذف الآن"):
                res = requests.post(url, json={"action": "delete", "email": del_email})
                if res.status_code == 200: st.success("تم الحذف بنجاح")
                else: st.error("لم يتم العثور على الإيميل")

# 5. واجهة المستخدم (الفورم)
if not is_open:
    st.error(f"⛔ انتهى وقت الحجز لليوم. الساعة الآن {now.strftime('%I:%M %p')}")
else:
    with st.form("my_form"):
        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("Email (@zewailcity.edu.eg)")
        location = st.selectbox("مكان الاستلام", ["عماير القرية الكونية (عمو صبرى)", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (لطلاب السكن)")
        submit = st.form_submit_button("تأكيد حجز الوجبة")

        if submit:
            if not email.lower().endswith("@zewailcity.edu.eg"):
                st.error("❌ سجل بإيميل الجامعة")
            else:
                data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                with st.spinner("جاري التحقق..."):
                    res = requests.post(url, json=data)
                    res_data = res.json()
                    if res_data.get("result") == "success":
                        st.balloons()
                        st.success("تقبل الله! تم تسجيل وجبتك بنجاح. كل سنة وأنتم طيبين 🌙✨")
                    elif res_data.get("message") == "duplicate":
                        st.warning("⚠️ أنت سجلت قبل كدة النهاردة!")
