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

# الروابط الخاصة بك (تأكد من وضع روابطك الفعلية هنا)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- التنسيق الجمالي ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px; }
    .stat-box { background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 10px; border-left: 5px solid #f1c40f; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# --- الدوال المساعدة ---
def load_current_data():
    try:
        df = pd.read_csv(URL_SHEET_CSV)
        df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
        df['Location'] = df['Location'].astype(str).str.strip()
        df['Gender'] = df['Gender'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# --- التبويب الأول: التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    # الحجز متاح من 12 صباحاً لـ 4:30 عصراً
    is_open = 0 <= (now.hour * 60 + now.minute) < (16 * 60 + 30)

    if not is_open:
        st.error("⛔ الحجز مغلق حالياً. يفتح يومياً حتى 4:30 عصراً.")
    else:
        st.success("🟢 الحجز متاح الآن للطلاب")
        c1, c2 = st.columns(2)
        name = c1.text_input("الاسم الثلاثي")
        student_id = c2.text_input("ID الطالب")
        email = st.text_input("الإيميل الجامعي الرسمي")
        loc = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        gen = st.radio("الجنس", ["ولد", "بنت"], horizontal=True)
        room = st.text_input("رقم الغرفة")

        if st.button("تأكيد الحجز 🚀", use_container_width=True):
            payload = {"action": "register", "name": name, "id": student_id, "email": email, "location": loc, "gender": gen, "room": room}
            res = requests.post(URL_SCRIPT, json=payload).json()
            if res.get("result") == "success": st.balloons(); st.success("🎉 تم الحجز!")
            else: st.warning("⚠️ مسجل بالفعل")

# --- التبويب الثاني: الإدارة (الرجوع للمنطق المستقر) ---
with tab2:
    if st.text_input("كلمة السر", type="password") == "Zewail2026":
        
        # زرار التحديث اليدوي لضمان استقرار الصفحة
        if st.button("🔄 تحديث وعرض البيانات", use_container_width=True):
            st.session_state.admin_df = load_current_data()
            st.success("✅ تم جلب أحدث البيانات")

        if 'admin_df' in st.session_state and not st.session_state.admin_df.empty:
            df = st.session_state.admin_df
            
            # 1. إحصائيات سريعة
            st.markdown(f'<div class="total-banner">إجمالي وجبات اليوم: {len(df)}</div>', unsafe_allow_html=True)
            def c_v(l, g): return len(df[(df['Location'] == l) & (df['Gender'] == g)])
            
            cols = st.columns(3)
            areas = [("عماير القرية الكونية", "الكونية"), ("الفيروز / المنطقة التالتة", "الفيروز"), ("سكن الجامعة (Dorms)", "Dorms")]
            for i, (f, s) in enumerate(areas):
                with cols[i]:
                    st.markdown(f'<div class="stat-box"><b>{s}</b><br><span style="color:#3498db">بنين: {c_v(f, "ولد")}</span><br><span style="color:#e91e63">بنات: {c_v(f, "بنت")}</span></div>', unsafe_allow_html=True)

            # 2. فلاتر الكشوفات (التي طلبت إرجاعها)
            st.markdown("---")
            st.write("### 🔍 تصفية الكشوفات التفصيلية")
            f1, f2 = st.columns(2)
            a_map = {"الكل": "الكل", "الكونية": "عماير القرية الكونية", "الفيروز": "الفيروز / المنطقة التالتة", "Dorms": "سكن الجامعة (Dorms)"}
            sel_a = f1.selectbox("فلتر المنطقة", list(a_map.keys()))
            sel_g = f2.selectbox("فلتر الجنس", ["الكل", "ولد", "بنت"])

            display_df = df.copy()
            if sel_a != "الكل": display_df = display_df[display_df['Location'] == a_map[sel_a]]
            if sel_g != "الكل": display_df = display_df[display_df['Gender'] == sel_g]
            
            st.write(f"✅ عدد النتائج المفلترة: {len(display_df)}")
            st.dataframe(display_df, use_container_width=True)

            # 3. إجراءات التحكم بالـ ID
            st.markdown("---")
            st.write("### 🛠️ إجراءات سريعة بالـ ID")
            target_id = st.text_input("ادخل الـ ID للطالب المستهدف")
            b1, b2, b3 = st.columns(3)
            
            if b1.button("✅ تأكيد استلام"):
                if target_id:
                    requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": target_id})
                    st.session_state.admin_df = load_current_data() # تحديث الداتا بعد الإجراء
                    st.rerun()

            if b2.button("❌ حذف حجز"):
                if target_id:
                    requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": target_id})
                    st.session_state.admin_df = load_current_data()
                    st.rerun()

            if b3.button("🗑️ مسح الكل"):
                if st.checkbox("تأكيد مسح اليوم"):
                    requests.post(URL_SCRIPT, json={"action": "clear_day"})
                    st.session_state.admin_df = load_current_data()
                    st.rerun()
