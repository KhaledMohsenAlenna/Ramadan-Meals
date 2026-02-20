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

# الروابط الخاصة بك
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- بيانات الـ OTP (تأكد من مطابقة الإيميل والباسورد المولد) ---
SENDER_EMAIL = "s-khaled.alenna@zewailcity.edu.eg" 
APP_PASSWORD = "jsse uiax musb xwhh"  # الكود اللي أنت طلعته الآن

# دالة إرسال الإيميل (SMTP)
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

# دالة تحميل البيانات بالكاش (لتحسين الأداء)
@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url)
    if len(df.columns) >= 8:
        df.columns = ["التاريخ", "الاسم", "الإيميل", "ID", "المكان", "النوع", "الغرفة", "الحالة"]
    return df

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
            gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
            room = st.text_input("رقم الغرفة (للسكن فقط)")
            
            if st.form_submit_button("إرسال كود التأكيد"):
                if email.lower().endswith("@zewailcity.edu.eg"):
                    st.session_state.otp = str(random.randint(1000, 9999))
                    st.session_state.temp_data = {
                        "name": name, "id": sid, "email": email, 
                        "location": loc, "gender": gender, "room": room
                    }
                    with st.spinner("جاري إرسال الكود..."):
                        if send_otp(email, st.session_state.otp):
                            st.session_state.step = 2
                            st.rerun()
                        else: st.error("فشل إرسال الكود، تأكد من إعدادات الحساب")
                else: st.error("يرجى استخدام إيميل الجامعة الرسمي")

    elif st.session_state.step == 2:
        u_code = st.text_input("أدخل الكود المكون من 4 أرقام المبعوث لإيميلك")
        if st.button("تأكيد الحجز النهائي"):
            if u_code == st.session_state.otp:
                with st.spinner("جاري التسجيل..."):
                    requests.post(URL_SCRIPT, json=st.session_state.temp_data)
                    st.balloons(); st.success("تم الحجز بنجاح! رمضان كريم 🌙")
                    load_data.clear()
                    st.session_state.step = 1
            else: st.error("الكود غير صحيح")

with tab2:
    if st.text_input("كلمة سر الإدمن", type="password") == "Zewail2026":
        try:
            df = load_data(URL_SHEET_CSV)
            st.markdown("### 📊 إحصائيات التوزيع اليومية")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("إجمالي الوجبات", len(df))
            # استخدام الفلترة الذكية لعرض الأعداد لكل منطقة
            counts = df.iloc[:, 4].value_counts()
            c2.metric("العماير", counts.get("عماير القرية الكونية", 0))
            c3.metric("الفيروز", counts.get("الفيروز", 0))
            c4.metric("السكن", counts.get("سكن الجامعة (Dorms)", 0))
            
            st.markdown("---")
            st.dataframe(df, use_container_width=True)
            
            # قسم الحذف أو التعديل
            update_id = st.text_input("ادخل الـ ID للتعديل")
            if st.button("✔️ تم الاستلام"):
                requests.post(URL_SCRIPT, json={"action": "update_status", "student_id": update_id, "status": "تم الاستلام ✅"})
                load_data.clear(); st.rerun()
        except:
            st.warning("لا توجد بيانات مسجلة حالياً.")
