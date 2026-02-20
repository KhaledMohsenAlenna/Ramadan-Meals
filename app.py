import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide")

# الروابط
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .sub-title { color: #ffffff; text-align: center; font-size: 1.5rem; margin-bottom: 30px; }
    .stat-card { background: #1a2a4a; padding: 10px; border-radius: 12px; text-align: center; border: 1px solid #f1c40f; }
    .area-header { background-color: #f1c40f; color: #0a192f; padding: 8px; border-radius: 8px; font-weight: bold; margin: 15px 0 5px 0; text-align: center; }
    .boy-stat { color: #3498db; font-size: 1.2rem; font-weight: bold; }
    .girl-stat { color: #e91e63; font-size: 1.2rem; font-weight: bold; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 10px; border-radius: 10px; font-size: 1.3rem; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">نتمنى لكم صوماً مقبولاً وإفطاراً شهياً</div>', unsafe_allow_html=True)

# --- دالة إرسال الإيميل ---
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

# --- دالة التحقق من تسجيل الإيميل سابقاً ---
def is_email_verified(email_to_check):
    try:
        df_all = pd.read_csv(URL_SHEET_CSV)
        # التأكد من وجود عمود الإيميلات (العمود رقم 3 - Index 2)
        verified_emails = df_all.iloc[:, 2].astype(str).str.strip().unique()
        return email_to_check.strip() in verified_emails
    except:
        return False

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# --- التبويب الأول: التسجيل (المنطق الجديد) ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً. يفتح يومياً حتى 4:30 عصراً.")
    else:
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False
        if 'verified_user' not in st.session_state: st.session_state.verified_user = False

        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        student_id = col2.text_input("University ID")
        email = st.text_input("الإيميل الجامعي الرسمي")
        
        col3, col4 = st.columns(2)
        location = col3.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gender = col4.radio("الجنس", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (للسكن فقط)")

        # الزرار الأساسي للحجز
        if st.button("تأكيد الحجز 🚀", use_container_width=True):
            if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                # 1. فحص هل الإيميل سجل قبل كدة؟
                if is_email_verified(email):
                    # سجل قبل كدة -> حجز مباشر
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("أهلاً بك مجدداً.. جاري الحجز المباشر..."):
                        try:
                            r = requests.post(URL_SCRIPT, json=data, timeout=25)
                            if r.json().get("result") == "success":
                                st.balloons(); st.success("🎉 تم الحجز بنجاح بدون كود تأكيد!")
                            else: st.warning("⚠️ مسجل بالفعل لهذا اليوم")
                        except: st.error("❌ مشكلة في الاتصال")
                else:
                    # أول مرة يسجل -> نطلب OTP
                    st.session_state.otp = str(random.randint(1000, 9999))
                    with st.spinner("أول مرة تسجل؟ جاري إرسال كود التأكيد لإيميلك..."):
                        res = send_code(email, st.session_state.otp)
                        if res == "success":
                            st.session_state.email_sent = True
                            st.info("✅ تم إرسال الكود. ادخله بالأسفل لإتمام الحجز وتفعيل حسابك.")
                        else: st.error(f"❌ فشل الإرسال: {res}")
            else:
                st.warning("⚠️ تأكد من البيانات وإيميل الجامعة الرسمي")

        # خانة الـ OTP تظهر فقط لو المستخدم جديد
        if st.session_state.email_sent:
            user_code = st.text_input("ادخل كود التأكيد (لمرة واحدة فقط)")
            if st.button("تفعيل الحجز والاشتراك"):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("جاري التفعيل والحجز..."):
                        try:
                            r = requests.post(URL_SCRIPT, json=data, timeout=25)
                            if r.json().get("result") == "success":
                                st.balloons(); st.success("🎉 تم التفعيل والحجز! المرة القادمة ستحجز مباشرة."); st.session_state.email_sent = False
                            else: st.warning("⚠️ مسجل بالفعل لهذا اليوم")
                        except: st.error("❌ مشكلة في الاتصال")
                else: st.error("❌ الكود غير صحيح")

# --- لوحة الإدارة (نفس كود الكاش الذكي السابق) ---
with tab2:
    pw = st.text_input("كلمة السر", type="password")
    if pw == "Zewail2026":
        if 'raw_data' not in st.session_state: st.session_state.raw_data = None
        
        if st.button("🔄 تحديث البيانات", use_container_width=True):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
                df['Location'] = df['Location'].astype(str).str.strip()
                df['Gender'] = df['Gender'].astype(str).str.strip()
                st.session_state.raw_data = df
                st.success("✅ تم التحديث")
            except Exception as e: st.error(f"❌ خطأ: {str(e)}")

        if st.session_state.raw_data is not None:
            df = st.session_state.raw_data
            st.markdown(f'<div class="total-banner">إجمالي الحجوزات: {len(df)}</div>', unsafe_allow_html=True)
            
            # (إحصائيات المناطق والفلترة كما في النسخة السابقة)
            c1, c2, c3 = st.columns(3)
            def show_stats(v, t):
                a = df[df['Location'] == v]
                st.markdown(f'<div class="area-header">{t}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-card">بنين: {len(a[a["Gender"]=="ولد"])} | بنات: {len(a[a["Gender"]=="بنت"])}<br><b>{len(a)}</b></div>', unsafe_allow_html=True)
            
            show_stats("عماير القرية الكونية", "الكونية")
            show_stats("الفيروز / المنطقة التالتة", "الفيروز")
            show_stats("سكن الجامعة (Dorms)", "Dorms")
            
            st.markdown("---")
            f_area, f_gender = st.columns(2)
            a_map = {"الكل": "الكل", "الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
            s_a = f_area.selectbox("المنطقة", list(a_map.keys()))
            s_g = f_gender.selectbox("الجنس", ["الكل", "ولد", "بنت"])
            
            d_df = df.copy()
            if s_a != "الكل": d_df = d_df[d_df['Location'] == a_map[s_a]]
            if s_g != "الكل": d_df = d_df[d_df['Gender'] == s_g]
            st.dataframe(d_df, use_container_width=True)
