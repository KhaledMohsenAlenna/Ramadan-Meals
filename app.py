import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# إعداد الصفحة
st.set_page_config(page_title="وجبات رمضان", layout="wide")

# الروابط الخاصة بك
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# تنسيق CSS محسن للـ Dashboard
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; font-weight: bold; margin-top: -50px; }
    .sub-title { color: #ffffff; text-align: center; font-size: 1.8rem; margin-bottom: 30px; }
    .stat-card { background-color: #1a2a4a; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #f1c40f; margin-bottom: 10px; }
    .gender-card { border: 1px solid #3498db; background-color: #0d2137; }
    h2, h3, h6 { margin: 0; padding: 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">نتمنى لكم صوماً مقبولاً وإفطاراً شهياً</div>', unsafe_allow_html=True)

# دالة إرسال الإيميل
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

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "🔐 لوحة الإدارة الذكية"])

# --- التبويب الأول: التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً. يفتح الحجز يومياً حتى الساعة 4:30 عصراً.")
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
                    with st.spinner("جاري إرسال الكود..."):
                        res = send_code(email, st.session_state.otp)
                        if res == "success":
                            st.session_state.email_sent = True
                            st.rerun()
                        else: st.error(f"فشل الإرسال: {res}")
                else: st.warning("تأكد من صحة البيانات وإيميل الجامعة الرسمي")

        if st.session_state.email_sent:
            user_code = st.text_input("ادخل الكود المكون من 4 أرقام")
            if st.button("تأكيد الحجز النهائي"):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("جاري التسجيل..."):
                        try:
                            r = requests.post(URL_SCRIPT, json=data, timeout=25)
                            if r.json().get("result") == "success":
                                st.balloons()
                                st.success("🎉 تم تسجيل حجزك بنجاح!")
                                st.session_state.email_sent = False
                            else: st.warning("أنت مسجل بالفعل لهذا اليوم")
                        except: st.error("مشكلة في الاتصال بالسيرفر")
                else: st.error("الكود غير صحيح")

# --- التبويب الثاني: لوحة الإدارة ---
with tab2:
    pw = st.text_input("كلمة السر للمسؤول", type="password")
    if pw == "Zewail2026":
        st.write("### 📊 إحصائيات الوجبات والتوزيع")
        
        if st.button("🔄 تحديث الإحصائيات والجدول"):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                
                # 1. إحصائيات المناطق (العمود رقم 5 - Index 4)
                loc_stats = df.iloc[:, 4].value_counts()
                
                # 2. إحصائيات النوع (العمود رقم 6 - Index 5)
                gender_stats = df.iloc[:, 5].value_counts()
                
                # الصف الأول: إحصائيات عامة والنوع
                st.write("#### الإحصائيات العامة والنوع")
                c_total, c_boys, c_girls = st.columns(3)
                with c_total:
                    st.markdown(f'<div class="stat-card"><h3>الإجمالي</h3><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
                with c_boys:
                    st.markdown(f'<div class="stat-card gender-card"><h3>بنين 👦</h3><h2>{gender_stats.get("ولد", 0)}</h2></div>', unsafe_allow_html=True)
                with c_girls:
                    st.markdown(f'<div class="stat-card gender-card"><h3>بنات 👧</h3><h2>{gender_stats.get("بنت", 0)}</h2></div>', unsafe_allow_html=True)

                # الصف الثاني: توزيع المناطق (بالمسميات الجديدة)
                st.write("#### توزيع الوجبات حسب المنطقة")
                c_konia, c_fayrouz, c_dorms = st.columns(3)
                with c_konia:
                    st.markdown(f'<div class="stat-card"><h6>الكونية</h6><h2>{loc_stats.get("عماير القرية الكونية", 0)}</h2></div>', unsafe_allow_html=True)
                with c_fayrouz:
                    st.markdown(f'<div class="stat-card"><h6>الفيروز</h6><h2>{loc_stats.get("الفيروز / المنطقة التالتة", 0)}</h2></div>', unsafe_allow_html=True)
                with c_dorms:
                    st.markdown(f'<div class="stat-card"><h6>Dorms</h6><h2>{loc_stats.get("سكن الجامعة (Dorms)", 0)}</h2></div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.write("#### كشف الأسماء التفصيلي")
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"خطأ في جلب البيانات: {str(e)}")

        st.markdown("---")
        st.write("### ✅ تأكيد الاستلام (تظليل)")
        rec_id = st.text_input("ادخل ID الطالب للتظليل")
        if st.button("تأكيد استلام"):
            if rec_id:
                with st.spinner("جاري التحديث..."):
                    try:
                        res = requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": rec_id})
                        if res.json().get("result") == "success":
                            st.success(f"✅ تم تظليل الطالب {rec_id} بنجاح.")
                        else: st.error("الرقم الجامعي غير موجود")
                    except: st.error("فشل الاتصال")
