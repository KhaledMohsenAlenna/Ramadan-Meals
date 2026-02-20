import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- الإعدادات ---
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide")

URL_SCRIPT = "رابط_سكريبت_جوجل_هنا"
URL_SHEET_CSV = "رابط_نشر_CSV_هنا"

# --- تصميم CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .stat-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #f1c40f; text-align: center; height: 100%; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.3rem; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

def fetch_data():
    try:
        df = pd.read_csv(URL_SHEET_CSV)
        df.columns = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status'][:len(df.columns)]
        df['Location'] = df['Location'].astype(str).str.strip()
        df['Gender'] = df['Gender'].astype(str).str.strip()
        df['ID'] = df['ID'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# --- واجهة التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = 0 <= (now.hour * 60 + now.minute) < (16 * 60 + 30)

    if not is_open:
        st.error("⛔ الحجز مغلق حالياً. يفتح يومياً حتى 4:30 عصراً.")
    else:
        with st.form("reg_form", clear_on_submit=True):
            name, sid = st.columns(2)
            n_val = name.text_input("الاسم الثلاثي")
            s_val = sid.text_input("University ID")
            mail = st.text_input("إيميل الجامعة الرسمي")
            loc = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
            gen = st.radio("الجنس", ["ولد", "بنت"], horizontal=True)
            rm = st.text_input("رقم الغرفة")
            if st.form_submit_button("تأكيد الحجز 🚀"):
                if n_val and s_val and mail.lower().endswith("@zewailcity.edu.eg"):
                    res = requests.post(URL_SCRIPT, json={"action":"register","name":n_val,"id":s_val,"email":mail,"location":loc,"gender":gen,"room":rm}).json()
                    if res.get("result") == "success": st.success("🎉 تم الحجز بنجاح!")
                    else: st.warning("⚠️ مسجل بالفعل لهذا اليوم")
                else: st.error("❌ يرجى التأكد من البيانات وإيميل الجامعة")

# --- واجهة الإدارة ---
with tab2:
    if st.text_input("كلمة السر", type="password") == "Zewail2026":
        df = fetch_data()
        if not df.empty:
            st.markdown(f'<div class="total-banner">إجمالي الحجوزات: {len(df)} وجبة</div>', unsafe_allow_html=True)
            
            # إحصائيات الـ 6 كروت
            def c_m(l, g): return len(df[(df['Location'] == l) & (df['Gender'] == g)])
            c1, c2, c3 = st.columns(3)
            areas = [("عماير القرية الكونية", "الكونية"), ("الفيروز / المنطقة التالتة", "الفيروز"), ("سكن الجامعة (Dorms)", "Dorms")]
            for i, (f, s) in enumerate(areas):
                with [c1, c2, c3][i]:
                    st.markdown(f'<div class="stat-box">🏙️ <b>{s}</b><br><span style="color:#3498db">بنين: {c_m(f,"ولد")}</span><br><span style="color:#e91e63">بنات: {c_m(f,"بنت")}</span></div>', unsafe_allow_html=True)

            st.markdown("---")
            # تصفية الكشوفات
            st.write("### 🔍 تصفية الكشوفات التفصيلية")
            f1, f2 = st.columns(2)
            a_opt = {"الكل":"الكل","الكونية":"عماير القرية الكونية","الفيروز":"الفيروز / المنطقة التالتة","Dorms":"سكن الجامعة (Dorms)"}
            sel_a = f1.selectbox("المنطقة", list(a_opt.keys()))
            sel_g = f2.selectbox("الجنس", ["الكل", "ولد", "بنت"])
            d_df = df.copy()
            if sel_a != "الكل": d_df = d_df[d_df['Location'] == a_opt[sel_a]]
            if sel_g != "الكل": d_df = d_df[d_df['Gender'] == sel_g]
            st.dataframe(d_df, use_container_width=True)

            # إجراءات التحكم والرسائل الإرشادية
            st.markdown("---")
            st.write("### ✅ بوابة تسليم الوجبات")
            target_id = st.text_input("ادخل ID الطالب")
            b1, b2, b3 = st.columns(3)
            
            if b1.button("✅ تأكيد استلام", use_container_width=True):
                if target_id:
                    s_row = df[df['ID'] == target_id.strip()]
                    if s_row.empty: st.error("❌ الرقم غير موجود بالكشف!")
                    elif "تم الاستلام" in str(s_row['Status'].values[0]): st.warning("⚠️ هذا الطالب استلم مسبقاً!")
                    else:
                        requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": target_id})
                        st.toast(f"✅ تم تأكيد استلام {target_id}", icon='🍱'); st.rerun()

            if b2.button("❌ حذف حجز", use_container_width=True):
                if target_id:
                    requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": target_id})
                    st.toast(f"🗑️ تم الحذف {target_id}", icon='🔥'); st.rerun()

            if b3.button("🗑️ مسح الكل", use_container_width=True):
                if st.checkbox("تأكيد مسح اليوم"):
                    requests.post(URL_SCRIPT, json={"action": "clear_day"})
                    st.toast("✨ تم تصفير الكشف", icon='🧹'); st.rerun()
        else: st.info("لا توجد بيانات حالية.")
