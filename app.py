import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات الصفحة والروابط ---
st.set_page_config(page_title="وجبات رمضان - زويل", layout="wide", page_icon="🌙")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- بيانات الـ OTP (بناءً على صورك الأخيرة) ---
SENDER_EMAIL = "s-khaled.alenna@zewailcity.edu.eg" 
APP_PASSWORD = "jsse uiax musb xwhh" 

# دالة إرسال الإيميل
def send_otp(receiver, code):
    try:
        msg = MIMEText(f"كود التأكيد الخاص بك لحجز وجبة رمضان هو: {code}")
        msg['Subject'] = 'تأكيد حجز وجبة إفطار'
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        return True
    except: return False

# --- واجهة الموقع ---
st.markdown("<h1 style='text-align: center; color: #f1c40f;'>وجبات رمضان</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>كل عام وأنتم بخير</h3>", unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = 1

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "🔐 لوحة الإدارة الذكية"])

with tab1:
    if st.session_state.step == 1:
        with st.form("main_form"):
            name = st.text_input("الاسم الثلاثي")
            sid = st.text_input("University ID")
            email = st.text_input("الإيميل الجامعي الرسمي")
            loc = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز", "سكن الجامعة (Dorms)"])
            if st.form_submit_button("إرسال كود التأكيد"):
                if email.lower().endswith("@zewailcity.edu.eg"):
                    st.session_state.otp = str(random.randint(1000, 9999))
                    st.session_state.temp_data = {"name": name, "id": sid, "email": email, "location": loc}
                    if send_otp(email, st.session_state.otp):
                        st.session_state.step = 2
                        st.rerun()
                    else: st.error("فشل إرسال الكود، تأكد من إعدادات الحساب")
                else: st.error("يرجى استخدام إيميل الجامعة الرسمي")

    elif st.session_state.step == 2:
        u_code = st.text_input("أدخل الكود المكون من 4 أرقام")
        if st.button("تأكيد الحجز النهائي"):
            if u_code == st.session_state.otp:
                requests.post(URL_SCRIPT, json=st.session_state.temp_data)
                st.balloons(); st.success("تم الحجز بنجاح! رمضان كريم 🌙")
                st.session_state.step = 1
            else: st.error("الكود غير صحيح")

with tab2:
    if st.text_input("كلمة سر الإدمن", type="password") == "Zewail2026":
        try:
            df = pd.read_csv(URL_SHEET_CSV)
            st.markdown("### 📊 إحصائيات التوزيع")
            st.write(f"إجمالي الحجوزات: {len(df)}")
            st.dataframe(df, use_container_width=True)
        except:
            st.warning("لا توجد بيانات مسجلة حالياً.")
