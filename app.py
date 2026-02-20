import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide", initial_sidebar_state="collapsed")

# الروابط الخاصة بك
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- التنسيق الجمالي (Custom CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; font-weight: bold; margin-top: -50px; text-shadow: 2px 2px 4px #000; }
    .sub-title { color: #ffffff; text-align: center; font-size: 1.6rem; margin-bottom: 30px; font-style: italic; }
    .stat-card { background: linear-gradient(145deg, #1a2a4a, #0d1b33); padding: 15px; border-radius: 12px; text-align: center; border: 1px solid #f1c40f; box-shadow: 5px 5px 15px #050b16; }
    .area-header { background-color: #f1c40f; color: #0a192f; padding: 8px; border-radius: 8px; font-weight: bold; margin: 20px 0 10px 0; text-align: center; font-size: 1.2rem; }
    .boy-stat { color: #3498db; font-size: 1.3rem; font-weight: bold; }
    .girl-stat { color: #e91e63; font-size: 1.3rem; font-weight: bold; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 10px; border-radius: 10px; font-size: 1.5rem; font-weight: bold; text-align: center; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">نتمنى لكم صوماً مقبولاً وإفطاراً شهياً</div>', unsafe_allow_html=True)

# --- دالة إرسال الإيميل ---
def send_code(receiver_email, code):
    try:
        sender = st.secrets["my_email"]
        password = st.secrets["my_password"]
        msg = MIMEText(f"كود التأكيد الخاص بك لحجز وجبة الإفطار هو: {code}")
        msg['Subject'] = 'تأكيد حجز الإفطار - مدينة زويل'
        msg['From'] = sender
        msg['To'] = receiver_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver_email, msg.as_string())
        return "success"
    except Exception as e:
        return str(e)

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# --- التبويب الأول: التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ عذراً، الحجز مغلق حالياً. الموعد اليومي من 12 صباحاً حتى 4:30 عصراً.")
    else:
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False

        with st.container():
            col_a, col_b = st.columns(2)
            name = col_a.text_input("الاسم الثلاثي")
            student_id = col_b.text_input("University ID")
            
            email = st.text_input("الإيميل الجامعي الرسمي (@zewailcity.edu.eg)")
            
            col_c, col_d = st.columns(2)
            location = col_c.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
            gender = col_d.radio("الجنس", ["ولد", "بنت"], horizontal=True)
            
            room = st.text_input("رقم الغرفة (لطلاب السكن فقط)")

        if not st.session_state.email_sent:
            if st.button("إرسال كود التأكيد 📩", use_container_width=True):
                if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                    st.session_state.otp = str(random.randint(1000, 9999))
                    with st.spinner("جاري إرسال الكود..."):
                        res = send_code(email, st.session_state.otp)
                        if res == "success":
                            st.session_state.email_sent = True
                            st.rerun()
                        else: st.error(f"❌ فشل الإرسال: {res}")
                else: st.warning("⚠️ يرجى التأكد من ملء البيانات واستخدام إيميل الجامعة")

        if st.session_state.email_sent:
            st.info("✅ تم إرسال الكود بنجاح. يرجى فحص البريد الوارد أو مجلد Spam.")
            user_code = st.text_input("ادخل الكود المكون من 4 أرقام")
            if st.button("تأكيد الحجز النهائي 🚀", use_container_width=True):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("جاري تسجيل حجزك..."):
                        try:
                            r = requests.post(URL_SCRIPT, json=data, timeout=25)
                            if r.json().get("result") == "success":
                                st.balloons()
                                st.success("🎉 مبروك! تم تسجيل حجزك بنجاح. صوماً مقبولاً!")
                                st.session_state.email_sent = False
                            else: st.warning("⚠️ عذراً، هذا الرقم أو الإيميل مسجل بالفعل اليوم.")
                        except: st.error("❌ حدث خطأ في الاتصال، يرجى المحاولة لاحقاً.")
                else: st.error("❌ الكود المدخل غير صحيح")

# --- التبويب الثاني: لوحة الإدارة (Dashboard) ---
with tab2:
    pw = st.text_input("كلمة مرور المسؤول", type="password")
    if pw == "Zewail2026":
        if st.button("🔄 تحديث الإحصائيات والكشوفات", use_container_width=True):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                num_cols = len(df.columns)
                all_cols = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status']
                df.columns = all_cols[:num_cols]
                
                # تنظيف البيانات لضمان دقة الفلترة
                df['Location'] = df['Location'].astype(str).str.strip()
                df['Gender'] = df['Gender'].astype(str).str.strip()

                st.markdown(f'<div class="total-banner">إجمالي الحجوزات الكلي: {len(df)} وجبة</div>', unsafe_allow_html=True)

                # --- دالة الإحصائيات ---
                def show_area_stats(loc_name, display_name):
                    area_df = df[df['Location'] == loc_name]
                    b = len(area_df[area_df['Gender'] == 'ولد'])
                    g = len(area_df[area_df['Gender'] == 'بنت'])
                    st.markdown(f'<div class="area-header">{display_name}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-card"><span class="boy-stat">بنين: {b}</span> | <span class="girl-stat">بنات: {g}</span><br><b style="font-size:1.2rem;">المجموع: {len(area_df)}</b></div>', unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1: show_area_stats("عماير القرية الكونية", "الكونية")
                with c2: show_area_stats("الفيروز / المنطقة التالتة", "الفيروز")
                with c3: show_area_stats("سكن الجامعة (Dorms)", "Dorms")

                st.markdown("---")
                
                # --- الكشوفات المفلترة ---
                st.write("### 📋 تصفية الكشوفات التفصيلية")
                f_area, f_gender = st.columns(2)
                sel_area = f_area.selectbox("المنطقة", ["الكل", "الكونية", "الفيروز", "Dorms"])
                sel_gender = f_gender.selectbox("الجنس", ["الكل", "ولد", "بنت"])

                display_df = df.copy()
                area_map = {"الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
                
                if sel_area != "الكل": display_df = display_df[display_df['Location'] == area_map[sel_area]]
                if sel_gender != "الكل": display_df = display_df[display_df['Gender'] == sel_gender]

                if not display_df.empty:
                    st.write(f"✅ تم العثور على {len(display_df)} سجل:")
                    st.dataframe(display_df, use_container_width=True)
                else:
                    st.warning("⚠️ لا توجد حجوزات مطابقة لهذا الاختيار حالياً.")

            except Exception as e:
                st.error(f"❌ خطأ في جلب البيانات: {str(e)}")

        st.markdown("---")
        st.write("### ✅ تأكيد استلام الوجبات")
        rec_id = st.text_input("ادخل ID الطالب لتأكيد استلامه للوجبة")
        if st.button("تأكيد الاستلام ✅"):
            if rec_id:
                with st.spinner("جاري التحديث..."):
                    try:
                        res = requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": rec_id})
                        if res.json().get("result") == "success":
                            st.success(f"✅ تم تأكيد استلام الطالب {rec_id} وتظليله في الشيت.")
                        else: st.error("❌ هذا الرقم غير موجود في كشف الحجوزات.")
                    except: st.error("❌ فشل الاتصال بالسيرفر.")
