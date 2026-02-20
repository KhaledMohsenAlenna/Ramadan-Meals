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

# تنسيق CSS احترافي للـ Dashboard
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .sub-title { color: #ffffff; text-align: center; font-size: 1.5rem; margin-bottom: 30px; }
    .stat-card { background-color: #1a2a4a; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #f1c40f; margin-bottom: 5px; }
    .area-header { background-color: #f1c40f; color: #0a192f; padding: 5px 15px; border-radius: 5px; font-weight: bold; margin: 15px 0 10px 0; text-align: center; }
    .boy-stat { color: #3498db; font-size: 1.2rem; font-weight: bold; }
    .girl-stat { color: #e91e63; font-size: 1.2rem; font-weight: bold; }
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
        if st.button("🔄 تحديث الإحصائيات والكشوفات"):
            try:
                # قراءة الشيت وتحديد أسماء الأعمدة يدوياً للتأكد من العد الصحيح
                df = pd.read_csv(URL_SHEET_CSV)
                df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room']

                # --- الإحصائيات التفصيلية ---
                st.write("### 📊 إحصائيات الوجبات (ولاد وبنات)")
                
                def get_stats(loc_name):
                    area_df = df[df['Location'] == loc_name]
                    boys = len(area_df[area_df['Gender'] == 'ولد'])
                    girls = len(area_df[area_df['Gender'] == 'بنت'])
                    return boys, girls, len(area_df)

                # حساب الأرقام
                k_b, k_g, k_t = get_stats("عماير القرية الكونية")
                f_b, f_g, f_t = get_stats("الفيروز / المنطقة التالتة")
                d_b, d_g, d_t = get_stats("سكن الجامعة (Dorms)")

                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown('<div class="area-header">الكونية</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-card"><span class="boy-stat">بنين: {k_b}</span><br><span class="girl-stat">بنات: {k_g}</span><br><b>الإجمالي: {k_t}</b></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="area-header">الفيروز</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-card"><span class="boy-stat">بنين: {f_b}</span><br><span class="girl-stat">بنات: {f_g}</span><br><b>الإجمالي: {f_t}</b></div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="area-header">Dorms</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-card"><span class="boy-stat">بنين: {d_b}</span><br><span class="girl-stat">بنات: {d_g}</span><br><b>الإجمالي: {d_t}</b></div>', unsafe_allow_html=True)

                st.markdown(f'<div style="text-align:center; font-size:1.5rem; margin-top:10px;"><b>إجمالي الوجبات الكلي: {len(df)}</b></div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # --- عرض الجداول حسب المنطقة والجنس ---
                st.write("### 📋 كشوفات التوزيع التفصيلية")
                
                selected_area = st.selectbox("اختر المنطقة لعرض الأسماء", ["الكل", "الكونية", "الفيروز", "Dorms"])
                selected_gender = st.selectbox("اختر الجنس", ["الكل", "ولد", "بنت"])
                
                # منطق الفلترة
                display_df = df.copy()
                area_map = {"الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
                
                if selected_area != "الكل":
                    display_df = display_df[display_df['Location'] == area_map[selected_area]]
                if selected_gender != "الكل":
                    display_df = display_df[display_df['Gender'] == selected_gender]
                
                st.write(f"عدد المسجلين في هذا القسم: {len(display_df)}")
                st.dataframe(display_df, use_container_width=True)
                
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
