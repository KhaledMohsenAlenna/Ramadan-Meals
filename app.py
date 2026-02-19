import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# 1. إعدادات الصفحة
st.set_page_config(page_title="Ramadan Iftar - Zewail City", layout="wide", page_icon="🌙")

# الروابط الهامة
URL_SCRIPT = "حط_رابط_الاسكريبت_هنا"
URL_SHEET_CSV = "حط_رابط_الـ_CSV_اللي_جبته_من_Publish_to_web_هنا"

# 2. التنسيق والصورة
st.image("https://i.postimg.cc/c6NK7LMH/SL-112419-25350-04.jpg", use_container_width=True)

# 3. نظام التبويبات (صفحة تسجيل / صفحة إدمن)
tab1, tab2 = st.tabs(["📋 تسجيل الحجز", "🔐 لوحة التحكم (Admins)"])

# --- الصفحة الأولى: تسجيل الطلاب ---
with tab1:
    st.markdown("<h1 style='text-align: center;'>🌙 مبادرة إفطار صائم</h1>", unsafe_allow_html=True)
    
    # منطق الوقت
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ انتهى وقت الحجز لليوم ({now.strftime('%I:%M %p')})")
    else:
        with st.form("iftar_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم الثلاثي")
            student_id = col2.text_input("University ID")
            email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
            location = st.selectbox("مكان الاستلام", ["عماير القرية الكونية (عمو صبرى)", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
            gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
            room = st.text_input("رقم الغرفة (لسكان السكن)")
            
            submit = st.form_submit_button("تأكيد الحجز")
            if submit:
                if not email.lower().endswith("@zewailcity.edu.eg"):
                    st.error("❌ سجل بإيميل الجامعة")
                else:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    res = requests.post(URL_SCRIPT, json=data)
                    if res.json().get("result") == "success":
                        st.balloons(); st.success("تم الحجز بنجاح! رمضان كريم 🌙")
                    elif res.json().get("message") == "duplicate":
                        st.warning("⚠️ مسجل بالفعل لهذا اليوم")

# --- الصفحة الثانية: لوحة تحكم الإدمن ---
with tab2:
    st.markdown("### 🛠️ إدارة الحجوزات")
    password = st.text_input("كلمة السر", type="password")
    if password == "Zewail2026":
        st.success("مرحباً خالد")
        
        # عرض الشيت
        if st.button("🔄 تحديث وعرض كشف الأسماء"):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                st.dataframe(df, use_container_width=True)
            except:
                st.error("تأكد من عمل Publish to web بصيغة CSV")

        # الحذف بالـ ID
        del_id = st.text_input("ادخل الـ University ID للحذف")
        if st.button("حذف الطالب"):
            res = requests.post(URL_SCRIPT, json={"action": "delete", "student_id": del_id})
            if res.json().get("result") == "success":
                st.success(f"تم حذف الرقم {del_id}")
            else:
                st.error("لم يتم العثور على الرقم")
