import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات الصفحة ---
st.set_page_config(page_title="إدارة وجبات رمضان", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- تصميم الواجهة الاحترافي (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .stat-card-mini { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px; border-left: 5px solid #f1c40f; text-align: center; margin-bottom: 10px; }
    .stat-val-mini { font-size: 1.5rem; font-weight: bold; display: block; }
    .stat-label-mini { font-size: 0.9rem; color: #bdc3c7; }
    .area-tag { background: #f1c40f; color: #0a192f; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; margin-bottom: 5px; display: inline-block; }
    .boy-text { color: #3498db; }
    .girl-text { color: #e91e63; }
    .total-banner { background: linear-gradient(90deg, #f1c40f, #f39c12); color: #0a192f; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.2rem; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# --- الدوال المساعدة ---
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
            user_code = st.text_input("ادخل الكود المستلم")
            if st.button("تفعيل واشتراك"):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    r = requests.post(URL_SCRIPT, json=data)
                    if r.json().get("result") == "success": st.success("🎉 تم التفعيل والحجز!"); st.session_state.email_sent = False
                else: st.error("❌ الكود خطأ")

# --- التبويب الثاني: لوحة الإدارة المطورة ---
with tab2:
    pw = st.text_input("كلمة سر الإدارة", type="password")
    if pw == "Zewail2026":
        if 'raw_data' not in st.session_state: st.session_state.raw_data = None
        
        if st.button("🔄 تحديث وإحصاء البيانات", use_container_width=True):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
                df['Location'] = df['Location'].astype(str).str.strip()
                df['Gender'] = df['Gender'].astype(str).str.strip()
                st.session_state.raw_data = df
                st.success("✅ تم التحديث")
            except: st.error("❌ فشل الجلب")

        if st.session_state.raw_data is not None:
            df = st.session_state.raw_data
            
            # --- الإحصائية الشاملة والسريعة ---
            st.markdown(f'<div class="total-banner">إجمالي وجبات اليوم: {len(df)}</div>', unsafe_allow_html=True)
            
            def get_counts(loc, gen):
                return len(df[(df['Location'] == loc) & (df['Gender'] == gen)])

            # عرض 6 كروت تفصيلية
            row1_col1, row1_col2, row1_col3 = st.columns(3)
            row2_col1, row2_col2, row2_col3 = st.columns(3)

            # الكونية
            row1_col1.markdown(f'<div class="stat-card-mini"><span class="area-tag">الكونية</span><span class="stat-label-mini boy-text">بنين</span><span class="stat-val-mini">{get_counts("عماير القرية الكونية", "ولد")}</span></div>', unsafe_allow_html=True)
            row2_col1.markdown(f'<div class="stat-card-mini"><span class="area-tag">الكونية</span><span class="stat-label-mini girl-text">بنات</span><span class="stat-val-mini">{get_counts("عماير القرية الكونية", "بنت")}</span></div>', unsafe_allow_html=True)
            
            # الفيروز
            row1_col2.markdown(f'<div class="stat-card-mini"><span class="area-tag">الفيروز</span><span class="stat-label-mini boy-text">بنين</span><span class="stat-val-mini">{get_counts("الفيروز / المنطقة التالتة", "ولد")}</span></div>', unsafe_allow_html=True)
            row2_col2.markdown(f'<div class="stat-card-mini"><span class="area-tag">الفيروز</span><span class="stat-label-mini girl-text">بنات</span><span class="stat-val-mini">{get_counts("الفيروز / المنطقة التالتة", "بنت")}</span></div>', unsafe_allow_html=True)
            
            # Dorms
            row1_col3.markdown(f'<div class="stat-card-mini"><span class="area-tag">Dorms</span><span class="stat-label-mini boy-text">بنين</span><span class="stat-val-mini">{get_counts("سكن الجامعة (Dorms)", "ولد")}</span></div>', unsafe_allow_html=True)
            row2_col3.markdown(f'<div class="stat-card-mini"><span class="area-tag">Dorms</span><span class="stat-label-mini girl-text">بنات</span><span class="stat-val-mini">{get_counts("سكن الجامعة (Dorms)", "بنت")}</span></div>', unsafe_allow_html=True)

            st.markdown("---")
            # --- أدوات الفلترة والتحكم ---
            f1, f2 = st.columns(2)
            a_map = {"الكل": "الكل", "الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
            sel_a = f1.selectbox("فلتر المنطقة للعرض", list(a_map.keys()))
            sel_g = f2.selectbox("فلتر الجنس للعرض", ["الكل", "ولد", "بنت"])
            
            filtered_df = df.copy()
            if sel_a != "الكل": filtered_df = filtered_df[filtered_df['Location'] == a_map[sel_a]]
            if sel_g != "الكل": filtered_df = filtered_df[filtered_df['Gender'] == sel_g]
            
            st.write(f"✅ كشف مفصل (العدد: {len(filtered_df)})")
            st.dataframe(filtered_df, use_container_width=True)

            st.markdown("---")
            # --- التحكم بالـ ID ومسح اليوم ---
            st.write("### 🛠️ عمليات إدارية")
            t_id = st.text_input("ادخل الـ ID للإجراء")
            c_m, c_d, c_clr = st.columns(3)
            
            if c_m.button("✅ تحديد استلام", use_container_width=True):
                if t_id: requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": t_id}); st.session_state.raw_data = None
            
            if c_d.button("❌ حذف حجز", use_container_width=True):
                if t_id: requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": t_id}); st.session_state.raw_data = None
            
            if c_clr.button("🗑️ مسح كشف اليوم", use_container_width=True):
                if st.checkbox("تأكيد مسح الكل"):
                    requests.post(URL_SCRIPT, json={"action": "clear_day"}); st.session_state.raw_data = None
