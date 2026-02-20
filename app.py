import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# --- إعدادات أساسية ---
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide")

# استبدل هذه الروابط بروابطك الخاصة
URL_SCRIPT = "رابط_سكريبت_جوجل_الجديد"
URL_SHEET_CSV = "رابط_نشر_CSV_الخاص_بالشيت"

# --- تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .stat-card { background: rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px; border-left: 5px solid #f1c40f; text-align: center; margin-bottom: 10px; }
    .area-tag { background: #f1c40f; color: #0a192f; padding: 3px 10px; border-radius: 5px; font-weight: bold; font-size: 0.85rem; }
    .boy-text { color: #3498db; font-size: 1.2rem; font-weight: bold; }
    .girl-text { color: #e91e63; font-size: 1.2rem; font-weight: bold; }
    .total-banner { background: linear-gradient(90deg, #f1c40f, #f39c12); color: #0a192f; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.3rem; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# --- وظائف الاتصال ---
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

def get_data_auto():
    try:
        df = pd.read_csv(URL_SHEET_CSV)
        df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
        return df
    except: return pd.DataFrame()

# --- التبويبات ---
tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# التبويب الأول: التسجيل مع التحكم بالوقت
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    # الفتح من 12:00 صباحاً (0) حتى 4:30 عصراً (16:30)
    current_minutes = now.hour * 60 + now.minute
    is_open = 0 <= current_minutes < (16 * 60 + 30)

    if not is_open:
        st.error(f"⛔ الحجز مغلق حالياً. يفتح الحجز يومياً من 12 صباحاً حتى 4:30 عصراً.")
    else:
        st.success("🟢 الحجز متاح حالياً للطلاب")
        if 'otp' not in st.session_state: st.session_state.otp = ""
        if 'email_sent' not in st.session_state: st.session_state.email_sent = False

        c1, c2 = st.columns(2)
        name = c1.text_input("الاسم الثلاثي")
        student_id = c2.text_input("ID الطالب")
        email = st.text_input("الإيميل الجامعي الرسمي (@zewailcity.edu.eg)")
        loc = st.selectbox("نقطة الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gen = st.radio("الجنس", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة (إن وجد)")

        if st.button("تأكيد الحجز 🚀", use_container_width=True):
            if name and student_id and email.lower().endswith("@zewailcity.edu.eg"):
                st.session_state.otp = str(random.randint(1000, 9999))
                if send_otp(email, st.session_state.otp) == "success":
                    st.session_state.email_sent = True; st.info("✅ تم إرسال الكود لإيميلك.")
            else: st.warning("⚠️ يرجى التأكد من البيانات وإيميل الجامعة")

        if st.session_state.email_sent:
            u_code = st.text_input("ادخل كود التفعيل")
            if st.button("تفعيل واشتراك"):
                if u_code == st.session_state.otp:
                    payload = {"name": name, "id": student_id, "email": email, "location": loc, "gender": gen, "room": room}
                    res = requests.post(URL_SCRIPT, json=payload).json()
                    if res.get("result") == "success": st.balloons(); st.success("🎉 تم الحجز بنجاح!"); st.session_state.email_sent = False
                    else: st.error("⚠️ مسجل بالفعل لهذا اليوم")
                else: st.error("❌ الكود غير صحيح")

# التبويب الثاني: الإدارة مع التحديث التلقائي
with tab2:
    if st.text_input("كلمة سر الإدارة", type="password") == "Zewail2026":
        df = get_data_auto()
        if not df.empty:
            st.markdown(f'<div class="total-banner">إجمالي وجبات اليوم: {len(df)}</div>', unsafe_allow_html=True)
            
            # إحصائيات فورية لكل منطقة ونوع
            def c_val(l, g): return len(df[(df['Location'] == l) & (df['Gender'] == g)])
            
            r1, r2 = st.columns(3), st.columns(3)
            areas = [("عماير القرية الكونية", "الكونية"), ("الفيروز / المنطقة التالتة", "الفيروز"), ("سكن الجامعة (Dorms)", "Dorms")]
            
            for i, (f, s) in enumerate(areas):
                r1[i].markdown(f'<div class="stat-card"><span class="area-tag">{s}</span><br><span class="boy-text">بنين: {c_val(f, "ولد")}</span></div>', unsafe_allow_html=True)
                r2[i].markdown(f'<div class="stat-card"><span class="area-tag">{s}</span><br><span class="girl-text">بنات: {c_val(f, "بنت")}</span></div>', unsafe_allow_html=True)

            st.markdown("---")
            # إجراءات الحذف والاستلام
            t_id = st.text_input("التحكم بواسطة ID الطالب")
            c_m, c_d, c_clr = st.columns(3)
            if c_m.button("✅ تأكيد استلام", use_container_width=True):
                if t_id: requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": t_id}); st.rerun()
            if c_d.button("❌ حذف حجز", use_container_width=True):
                if t_id: requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": t_id}); st.rerun()
            if c_clr.button("🗑️ مسح كشف اليوم", use_container_width=True):
                if st.checkbox("أنا متأكد"): requests.post(URL_SCRIPT, json={"action": "clear_day"}); st.rerun()

            st.write("### 📋 الكشف الحالي")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد بيانات مسجلة لليوم حتى الآن.")
