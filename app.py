import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات أساسية ---
st.set_page_config(page_title=" وجبات رمضان", layout="wide")

# استبدل الروابط هنا (تأكد أنها تبدأ بـ https://)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- تصميم CSS احترافي ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .stat-card-mini { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px; border-left: 5px solid #f1c40f; text-align: center; margin-bottom: 10px; }
    .area-tag { background: #f1c40f; color: #0a192f; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; }
    .boy-text { color: #3498db; } .girl-text { color: #e91e63; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# --- الدوال المساعدة ---
def send_otp(receiver_email, code):
    try:
        sender = st.secrets["my_email"]
        password = st.secrets["my_password"]
        msg = MIMEText(f"كود تأكيد حجز الوجبة هو: {code}")
        msg['Subject'] = 'تأكيد حجز إفطار رمضان'
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver_email, msg.as_string())
        return "success"
    except Exception as e: return str(e)

def load_data():
    try:
        df = pd.read_csv(URL_SHEET_CSV)
        df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
        return df
    except: return pd.DataFrame()

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# التبويب الأول: التسجيل مع التحكم بالوقت
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    current_minutes = now.hour * 60 + now.minute
    close_minutes = 16 * 60 + 30 # 4:30 عصراً
    is_open = 0 <= current_minutes < close_minutes

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً. يفتح الحجز يومياً من 12 صباحاً حتى 4:30 عصراً.")
    else:
        st.info("🟢 الحجز متاح الآن")
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False

        c1, c2 = st.columns(2)
        name, student_id = c1.text_input("الاسم الثلاثي"), c2.text_input("University ID")
        email = st.text_input("الإيميل الجامعي")
        loc = st.selectbox("نقطة الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gen = st.radio("الجنس", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة")

        if st.button("تأكيد الحجز 🚀", use_container_width=True):
            if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                # التحقق هل سجل سابقاً؟
                df_check = load_data()
                if not df_check.empty and email.strip() in df_check['Email'].values:
                    payload = {"name": name, "id": student_id, "email": email, "location": loc, "gender": gen, "room": room}
                    requests.post(URL_SCRIPT, json=payload); st.success("🎉 تم الحجز مباشرة (حساب مفعل)")
                else:
                    st.session_state.otp = str(random.randint(1000, 9999))
                    if send_otp(email, st.session_state.otp) == "success":
                        st.session_state.email_sent = True; st.info("✅ تم إرسال كود التأكيد.")
            else: st.warning("⚠️ يرجى إكمال البيانات")

        if st.session_state.email_sent:
            u_code = st.text_input("ادخل الكود")
            if st.button("تفعيل واشتراك"):
                if u_code == st.session_state.otp:
                    payload = {"name": name, "id": student_id, "email": email, "location": loc, "gender": gen, "room": room}
                    requests.post(URL_SCRIPT, json=payload); st.success("🎉 تم الحجز!"); st.session_state.email_sent = False
                else: st.error("❌ الكود خطأ")

# التبويب الثاني: الإدارة (تحديث تلقائي)
with tab2:
    if st.text_input("كلمة السر", type="password") == "Zewail2026":
        df = load_data()
        if not df.empty:
            st.markdown(f'<div class="total-banner">إجمالي وجبات اليوم: {len(df)}</div>', unsafe_allow_html=True)
            
            def get_c(l, g): return len(df[(df['Location'] == l) & (df['Gender'] == g)])
            
            r1, r2 = st.columns(3), st.columns(3)
            areas = [("عماير القرية الكونية", "الكونية"), ("الفيروز / المنطقة التالتة", "الفيروز"), ("سكن الجامعة (Dorms)", "Dorms")]
            for i, (f, s) in enumerate(areas):
                r1[i].markdown(f'<div class="stat-card-mini"><span class="area-tag">{s}</span><br><span class="boy-text">بنين: {get_c(f, "ولد")}</span></div>', unsafe_allow_html=True)
                r2[i].markdown(f'<div class="stat-card-mini"><span class="area-tag">{s}</span><br><span class="girl-text">بنات: {get_c(f, "بنت")}</span></div>', unsafe_allow_html=True)

            st.markdown("---")
            t_id = st.text_input("التحكم بواسطة ID")
            c_m, c_d, c_clr = st.columns(3)
            if c_m.button("✅ تأكيد استلام"): requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": t_id}); st.rerun()
            if c_d.button("❌ حذف حجز"): requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": t_id}); st.rerun()
            if c_clr.button("🗑️ مسح الكل"):
                if st.checkbox("تأكيد مسح اليوم"): requests.post(URL_SCRIPT, json={"action": "clear_day"}); st.rerun()
            st.dataframe(df, use_container_width=True)
