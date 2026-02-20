import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات الصفحة ---
st.set_page_config(page_title=" وجبات رمضان", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; font-weight: bold; margin-top: -50px; }
    .stat-box { background: linear-gradient(145deg, #1e3a5f, #0d1b33); padding: 15px; border-radius: 15px; border: 1px solid #f1c40f; text-align: center; }
    .stat-val { font-size: 2rem; font-weight: bold; color: #f1c40f; }
    .area-header { background: #f1c40f; color: #0a192f; padding: 10px; border-radius: 10px; font-weight: bold; text-align: center; margin: 20px 0; }
    .admin-actions { background: #162a47; padding: 20px; border-radius: 15px; border: 1px dashed #f1c40f; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# الدوال المساعدة
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
    except Exception as e: return str(e)

def is_email_verified(email_to_check):
    try:
        df_all = pd.read_csv(URL_SHEET_CSV)
        verified_emails = df_all.iloc[:, 2].astype(str).str.strip().unique()
        return email_to_check.strip() in verified_emails
    except: return False

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# --- التبويب الأول: التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً.")
    else:
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False

        c1, c2 = st.columns(2)
        name = c1.text_input("الاسم الثلاثي")
        student_id = c2.text_input("University ID")
        email = st.text_input("الإيميل الجامعي الرسمي")
        
        c3, c4 = st.columns(2)
        location = c3.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gender = c4.radio("الجنس", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة")

        if st.button("تأكيد الحجز 🚀", use_container_width=True):
            if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                if is_email_verified(email):
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    try:
                        r = requests.post(URL_SCRIPT, json=data, timeout=25)
                        if r.json().get("result") == "success": st.balloons(); st.success("🎉 تم الحجز بنجاح!")
                        else: st.warning("⚠️ مسجل بالفعل لهذا اليوم")
                    except: st.error("❌ مشكلة في الاتصال")
                else:
                    st.session_state.otp = str(random.randint(1000, 9999))
                    res = send_code(email, st.session_state.otp)
                    if res == "success": st.session_state.email_sent = True; st.info("✅ تم إرسال الكود لإيميلك.")
            else: st.warning("⚠️ تأكد من البيانات")

        if st.session_state.email_sent:
            user_code = st.text_input("ادخل الكود")
            if st.button("تفعيل واشتراك"):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    r = requests.post(URL_SCRIPT, json=data)
                    if r.json().get("result") == "success": st.success("🎉 تم التفعيل والحجز!"); st.session_state.email_sent = False
                else: st.error("❌ الكود خطأ")

# --- التبويب الثاني: لوحة الإدارة (الأدوات الجديدة) ---
with tab2:
    pw = st.text_input("كلمة سر الإدارة", type="password")
    if pw == "Zewail2026":
        if 'raw_data' not in st.session_state: st.session_state.raw_data = None
        
        # أزرار التحديث والمسح الشامل
        col_up, col_clr = st.columns(2)
        if col_up.button("🔄 تحديث البيانات", use_container_width=True):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
                df['Location'] = df['Location'].astype(str).str.strip()
                df['Gender'] = df['Gender'].astype(str).str.strip()
                st.session_state.raw_data = df
                st.success("✅ تم التحديث")
            except: st.error("❌ فشل الجلب")

        if col_clr.button("🗑️ مسح كشف اليوم بالكامل", use_container_width=True):
            if st.checkbox("أنا متأكد من مسح جميع الحجوزات الحالية لليوم"):
                try:
                    res = requests.post(URL_SCRIPT, json={"action": "clear_day"})
                    if res.json().get("result") == "success":
                        st.success("✅ تم مسح الكشف بنجاح."); st.session_state.raw_data = None
                    else: st.error("❌ فشل المسح")
                except: st.error("❌ خطأ اتصال")

        if st.session_state.raw_data is not None:
            df = st.session_state.raw_data
            
            # عرض الإحصائيات (مختصرة)
            st.markdown(f'<div class="area-header">إحصائيات سريعة (الإجمالي: {len(df)})</div>', unsafe_allow_html=True)
            
            # --- أدوات التحكم بالـ ID ---
            st.markdown('<div class="admin-actions">', unsafe_allow_html=True)
            st.write("### 🛠️ التحكم بواسطة ID الطالب")
            target_id = st.text_input("ادخل الرقم الجامعي للطالب المستهدف")
            
            c_mark, c_del = st.columns(2)
            
            if c_mark.button("✅ تحديد كـ (تم الاستلام)", use_container_width=True):
                if target_id:
                    res = requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": target_id})
                    if res.json().get("result") == "success":
                        st.success(f"✅ تم تحديد {target_id} مستلم."); st.session_state.raw_data = None
                    else: st.error("❌ الرقم غير موجود")

            if c_del.button("❌ مسح هذا الحجز فقط", use_container_width=True):
                if target_id:
                    res = requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": target_id})
                    if res.json().get("result") == "success":
                        st.warning(f"🗑️ تم حذف حجز {target_id}."); st.session_state.raw_data = None
                    else: st.error("❌ الرقم غير موجود")
            st.markdown('</div>', unsafe_allow_html=True)

            # --- عرض الجدول المفلتر ---
            st.markdown("---")
            f1, f2 = st.columns(2)
            a_map = {"الكل": "الكل", "الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
            s_a = f1.selectbox("المنطقة", list(a_map.keys()))
            s_g = f2.selectbox("الجنس", ["الكل", "ولد", "بنت"])
            
            d_df = df.copy()
            if s_a != "الكل": d_df = d_df[d_df['Location'] == a_map[s_a]]
            if s_g != "الكل": d_df = d_df[d_df['Gender'] == s_g]
            st.dataframe(d_df, use_container_width=True)
