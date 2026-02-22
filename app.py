import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- إعدادات الصفحة ---
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide")

# الروابط الخاصة بك
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.8rem; font-weight: bold; margin-top: -50px; }
    .stat-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #f1c40f; text-align: center; height: 100%; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.3rem; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# دالة جلب البيانات مع معالجة أخطاء الصفوف [cite: 2026-02-20]
def fetch_data():
    try:
        # قراءة الشيت وتجاهل أول صف لو كان تالفاً (مثل حرف A) [cite: 2026-02-20]
        df = pd.read_csv(URL_SHEET_CSV)
        
        # التأكد من وجود العناوين الصحيحة
        expected_cols = ['Timestamp', 'Name', 'Email', 'ID', 'Location', 'Gender', 'Room', 'Status']
        
        # لو أول صف ليس فيه كلمة Timestamp، بنعتبر إنه صف تالف وبنعيد القراءة من الصف اللي بعده
        if 'Timestamp' not in df.columns:
            df = pd.read_csv(URL_SHEET_CSV, skiprows=1)
            
        if len(df.columns) >= len(expected_cols):
            df.columns = expected_cols[:len(df.columns)]
        
        # تنظيف البيانات
        df = df.dropna(subset=['ID'])
        df['Location'] = df['Location'].astype(str).str.strip()
        df['Gender'] = df['Gender'].astype(str).str.strip()
        df['ID'] = df['ID'].astype(str).str.strip()
        return df
    except:
        return pd.DataFrame()

tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "📊 لوحة الإدارة الذكية"])

# --- واجهة التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    # الحجز متاح حتى 4:30 عصراً [cite: 2026-02-18]
    is_open = 0 <= (now.hour * 60 + now.minute) < (16 * 60 + 30)

    if not is_open:
        st.error("⛔ الحجز مغلق حالياً. يفتح يومياً حتى 4:30 عصراً.")
    else:
        with st.form("reg_form", clear_on_submit=True):
            n = st.text_input("الاسم الثلاثي")
            s = st.text_input("University ID")
            m = st.text_input("إيميل الجامعة")
            l = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
            g = st.radio("الجنس", ["ولد", "بنت"], horizontal=True)
            r = st.text_input("رقم الغرفة")
            if st.form_submit_button("تأكيد الحجز 🚀"):
                if n and s and m.lower().endswith("@zewailcity.edu.eg"):
                    res = requests.post(URL_SCRIPT, json={"action":"register","name":n,"id":s,"email":m,"location":l,"gender":g,"room":r}).json()
                    if res.get("result") == "success": st.success("🎉 تم الحجز!")
                    else: st.warning("⚠️ مسجل بالفعل لهذا اليوم")

# --- واجهة الإدارة ---
with tab2:
    if st.text_input("كلمة السر", type="password") == "Zewail2026":
        df = fetch_data()
        if not df.empty:
            st.markdown(f'<div class="total-banner">إجمالي الحجوزات: {len(df)} وجبة</div>', unsafe_allow_html=True)
            
            # إحصائيات الـ 6 كروت المفصلة [cite: 2026-02-18]
            def c_m(loc, gen): return len(df[(df['Location'] == loc) & (df['Gender'] == gen)])
            c1, c2, c3 = st.columns(3)
            areas = [("عماير القرية الكونية", "الكونية"), ("الفيروز / المنطقة التالتة", "الفيروز"), ("سكن الجامعة (Dorms)", "Dorms")]
            for i, (f, s) in enumerate(areas):
                with [c1, c2, c3][i]:
                    st.markdown(f'<div class="stat-box">🏙️ <b>{s}</b><br><span style="color:#3498db">بنين: {c_m(f,"ولد")}</span><br><span style="color:#e91e63">بنات: {c_m(f,"بنت")}</span></div>', unsafe_allow_html=True)

            # تصفية الكشوفات [cite: 2026-02-18]
            st.markdown("---")
            st.write("### 🔍 تصفية الكشوفات التفصيلية")
            f1, f2 = st.columns(2)
            a_opt = {"الكل":"الكل","الكونية":"عماير القرية الكونية","الفيروز":"الفيروز / المنطقة التالتة","Dorms":"سكن الجامعة (Dorms)"}
            sel_a = f1.selectbox("المنطقة", list(a_opt.keys()))
            sel_g = f2.selectbox("الجنس", ["الكل", "ولد", "بنت"])
            
            d_df = df.copy()
            if sel_a != "الكل": d_df = d_df[d_df['Location'] == a_opt[sel_a]]
            if sel_g != "الكل": d_df = d_df[d_df['Gender'] == sel_g]
            
            # حل تحذير use_container_width باستخدام width='stretch' [cite: 2026-02-20]
            st.dataframe(d_df, width=None, use_container_width=True)

            # التحكم بالـ ID والرسائل الإرشادية [cite: 2026-02-18]
            st.markdown("---")
            target_id = st.text_input("ادخل ID الطالب")
            b1, b2, b3 = st.columns(3)
            
            if b1.button("✅ تأكيد استلام", use_container_width=True):
                if target_id:
                    s_row = df[df['ID'] == target_id.strip()]
                    if s_row.empty: st.error("❌ غير موجود بالكشف!")
                    elif "تم الاستلام" in str(s_row['Status'].values[0]): st.warning("⚠️ استلم مسبقاً!")
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
        else:
            st.info("لا توجد بيانات مسجلة حالياً.")
