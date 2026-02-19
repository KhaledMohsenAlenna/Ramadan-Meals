import streamlit as st
import requests
from datetime import datetime
import pytz

# 1. إعدادات الصفحة والتنسيق الجمالي (UI/UX)
st.set_page_config(page_title="Ramadan Iftar - Zewail City", layout="centered", page_icon="🌙")

# كود لتغيير ألوان النصوص عشان تليق مع الخلفية الكحلي
st.markdown("""
    <style>
    h1 { color: #f1c40f; text-align: center; text-shadow: 2px 2px 4px #000; } /* ذهبي للعنوان */
    .stMarkdown p { color: #ffffff; text-align: center; font-size: 1.1em; } /* أبيض للوصف */
    div.stButton > button:first-child { background-color: #f1c40f; color: #000; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. الرابط المباشر للصورة اللي أنت اخترتها
img_url = "https://i.postimg.cc/c6NK7LMH/SL-112419-25350-04.jpg"
st.image(img_url, use_container_width=True)

# 3. بيانات الربط (تأكد أن هذا هو آخر رابط /exec عندك)
url = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"

st.markdown("# 🌙 مبادرة إفطار صائم")
st.markdown("كل عام وأنتم بخير - خدمة طلاب مدينة زويل المغتربين")

# 4. لوحة تحكم الـ Admin (Sidebar)
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    if st.checkbox("دخول المسؤولين"):
        admin_pw = st.text_input("كلمة السر", type="password")
        if admin_pw == "Zewail2026":
            st.success("مرحباً يا أدمن")
            del_email = st.text_input("إيميل الطالب للحذف")
            if st.button("حذف الحجز الآن"):
                with st.spinner("جاري الحذف من الشيت..."):
                    res = requests.post(url, json={"action": "delete", "email": del_email})
                    if res.status_code == 200: st.success("تم الحذف بنجاح")
                    else: st.error("حدث خطأ في الحذف")

# 5. منطق الوقت (الفتح والقفل)
cairo_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(cairo_tz)
is_open = False
if 0 <= now.hour < 16: is_open = True
elif now.hour == 16 and now.minute < 30: is_open = True

# 6. واجهة الحجز
if not is_open:
    st.error(f"⛔ انتهى وقت الحجز لليوم. الساعة الآن {now.strftime('%I:%M %p')}")
else:
    with st.form("iftar_form", clear_on_submit=True):
        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
        
        locations = ["عماير القرية الكونية (عمو صبرى)", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"]
        location = st.selectbox("مكان الاستلام", locations)
        
        gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (لسكان السكن)")
        
        submit = st.form_submit_button("تأكيد حجز الوجبة")

        if submit:
            if not email.lower().endswith("@zewailcity.edu.eg"):
                st.error("❌ عذراً، يجب استخدام إيميل الجامعة")
            else:
                data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                with st.spinner("جاري تسجيل طلبك..."):
                    try:
                        res = requests.post(url, json=data)
                        res_data = res.json()
                        if res_data.get("result") == "success":
                            st.balloons()
                            st.success(f"تقبل الله يا {name.split()[0]}! تم حجز وجبتك بنجاح 🌙✨")
                        elif res_data.get("message") == "duplicate":
                            st.warning("⚠️ إيميلك مسجل بالفعل لهذا اليوم.")
                    except:
                        st.error("❌ مشكلة في الربط، تأكد من الـ Script URL.")
