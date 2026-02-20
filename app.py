import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# إعداد الصفحة
st.set_page_config(page_title="وجبات رمضان - مدينة زويل", layout="wide")

# الرابط الجديد الخاص بك
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# تنسيق CSS
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; font-weight: bold; margin-top: -50px; }
    .sub-title { color: #ffffff; text-align: center; font-size: 1.5rem; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">إفطاراً شهياً - مدينة زويل</div>', unsafe_allow_html=True)

# دالة إرسال الإيميل (SMTP)
def send_code(receiver_email, code):
    try:
        sender = st.secrets["my_email"]
        password = st.secrets["my_password"]
        msg = MIMEText(f"كود التأكيد الخاص بك هو: {code}")
        msg['Subject'] = 'تأكيد حجز الإفطار'
        msg['From'] = sender
        msg['To'] = receiver_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver_email, msg.as_string())
        return "success"
    except Exception as e:
        return str(e)

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "🔐 لوحة الإدارة"])

# --- تسجيل الطلاب ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً.")
    else:
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False

        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("الإيميل الجامعي الرسمي")
        location = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (للسكن فقط)")

        if not st.session_state.email_sent:
            if st.button("إرسال كود التأكيد"):
                if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                    st.session_state.otp = str(random.randint(1000, 9999))
                    with st.spinner("جاري الإرسال..."):
                        res = send_code(email, st.session_state.otp)
                        if res == "success":
                            st.session_state.email_sent = True
                            st.rerun()
                        else: st.error(f"فشل الإرسال: {res}")
                else: st.warning("تأكد من البيانات وإيميل الجامعة")

        if st.session_state.email_sent:
            st.info("💡 افحص الـ Spam لو الكود متأخر")
            user_code = st.text_input("ادخل الكود هنا")
            if st.button("تأكيد الحجز النهائي"):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("جاري التسجيل..."):
                        try:
                            r = requests.post(URL_SCRIPT, json=data, timeout=25)
                            if r.json().get("result") == "success":
                                st.balloons()
                                st.success("🎉 تم الحجز بنجاح!")
                                st.session_state.email_sent = False
                            else: st.warning("أنت مسجل بالفعل اليوم")
                        except: st.error("مشكلة في الاتصال")
                else: st.error("الكود خطأ")

# --- لوحة الإدمن (تظليل الاستلام) ---
with tab2:
    pw = st.text_input("كلمة السر", type="password")
    if pw == "Zewail2026":
        if st.button("🔄 تحديث الجدول"):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                st.dataframe(df, use_container_width=True)
            except: st.error("فشل تحميل البيانات")

        st.markdown("---")
        st.write("### ✅ تأكيد الاستلام (تظليل)")
        rec_id = st.text_input("ادخل ID الطالب")
        if st.button("تأكيد استلام الوجبة"):
            if rec_id:
                with st.spinner("جاري التظليل..."):
                    try:
                        res = requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": rec_id})
                        if res.json().get("result") == "success":
                            st.success(f"✅ تم تظليل الطالب {rec_id} بنجاح.")
                        else: st.error("ID غير موجود")
                    except: st.error("فشل الاتصال")
