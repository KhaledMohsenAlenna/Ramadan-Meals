import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# إعدادات الصفحة
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide")

# الروابط
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# تنسيق CSS احترافي
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

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً. يفتح يومياً حتى 4:30 عصراً.")
    else:
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False

        col1, col2 = st.columns(2)
        name = col1.text_input("الاسم الثلاثي")
        student_id = col2.text_input("University ID")
        email = st.text_input("الإيميل الجامعي الرسمي")
        
        col3, col4 = st.columns(2)
        location = col3.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gender = col4.radio("الجنس", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (للسكن فقط)")

        if not st.session_state.email_sent:
            if st.button("إرسال كود التأكيد 📩", use_container_width=True):
                if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                    st.session_state.otp = str(random.randint(1000, 9999))
                    with st.spinner("جاري الإرسال..."):
                        res = send_code(email, st.session_state.otp)
                        if res == "success":
                            st.session_state.email_sent = True
                            st.rerun()
                        else: st.error(f"❌ فشل الإرسال: {res}")
                else: st.warning("⚠️ تأكد من البيانات وإيميل الجامعة الرسمي")

        if st.session_state.email_sent:
            user_code = st.text_input("ادخل الكود المكون من 4 أرقام")
            if st.button("تأكيد الحجز النهائي 🚀", use_container_width=True):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("جاري التسجيل..."):
                        try:
                            r = requests.post(URL_SCRIPT, json=data, timeout=25)
                            if r.json().get("result") == "success":
                                st.balloons(); st.success("🎉 تم الحجز بنجاح!"); st.session_state.email_sent = False
                            else: st.warning("⚠️ أنت مسجل بالفعل لهذا اليوم")
                        except: st.error("❌ مشكلة في الاتصال بالسيرفر")
                else: st.error("❌ الكود غير صحيح")

# --- لوحة الإدارة (التعديل الجوهري هنا) ---
with tab2:
    pw = st.text_input("كلمة السر", type="password")
    if pw == "Zewail2026":
        # حفظ البيانات في الـ Session State عشان متختفيش مع الفلترة
        if 'raw_data' not in st.session_state:
            st.session_state.raw_data = None

        if st.button("🔄 تحديث البيانات من الشيت", use_container_width=True):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                all_cols = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status']
                df.columns = all_cols[:len(df.columns)]
                df['Location'] = df['Location'].astype(str).str.strip()
                df['Gender'] = df['Gender'].astype(str).str.strip()
                st.session_state.raw_data = df # حفظ النسخة الأصلية
                st.success("✅ تم تحديث البيانات بنجاح")
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")

        if st.session_state.raw_data is not None:
            df = st.session_state.raw_data
            
            st.markdown(f'<div class="total-banner">إجمالي الحجوزات: {len(df)} وجبة</div>', unsafe_allow_html=True)

            def show_stats(loc_val, title):
                area = df[df['Location'] == loc_val]
                b, g = len(area[area['Gender'] == 'ولد']), len(area[area['Gender'] == 'بنت'])
                st.markdown(f'<div class="area-header">{title}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-card"><span class="boy-stat">بنين: {b}</span> | <span class="girl-stat">بنات: {g}</span><br><b>المجموع: {len(area)}</b></div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: show_stats("عماير القرية الكونية", "الكونية")
            with c2: show_stats("الفيروز / المنطقة التالتة", "الفيروز")
            with c3: show_stats("سكن الجامعة (Dorms)", "Dorms")

            st.markdown("---")
            st.write("### 📋 تصفية الكشوفات التفصيلية")
            
            f_area, f_gender = st.columns(2)
            area_map = {"الكل": "الكل", "الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
            sel_area = f_area.selectbox("المنطقة", list(area_map.keys()))
            sel_gender = f_gender.selectbox("الجنس", ["الكل", "ولد", "بنت"])

            # الفلترة بتتم على النسخة المحفوظة
            display_df = df.copy()
            if sel_area != "الكل":
                display_df = display_df[display_df['Location'] == area_map[sel_area]]
            if sel_gender != "الكل":
                display_df = display_df[display_df['Gender'] == sel_gender]

            if not display_df.empty:
                st.write(f"✅ تم العثور على {len(display_df)} سجل")
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("⚠️ لا توجد نتائج مطابقة")

            st.markdown("---")
            rec_id = st.text_input("ادخل ID الطالب لتأكيد الاستلام")
            if st.button("تأكيد الاستلام ✅", use_container_width=True):
                if rec_id:
                    try:
                        res = requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": rec_id})
                        if res.json().get("result") == "success": 
                            st.success("✅ تم التظليل بنجاح")
                            st.session_state.raw_data = None # مسح الكاش لإجبار الموقع على التحديث
                        else: st.error("❌ الرقم غير موجود")
                    except: st.error("❌ فشل الاتصال")
