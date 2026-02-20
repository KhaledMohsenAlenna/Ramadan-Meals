import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import random

# --- إعدادات أساسية ---
st.set_page_config(page_title="منظومة وجبات رمضان", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# --- تصميم CSS احترافي يمنع اختفاء العناصر ---
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white; }
    .main-title { color: #f1c40f; text-align: center; font-size: 2.5rem; font-weight: bold; margin-top: -50px; }
    .stat-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; border: 1px solid #f1c40f; text-align: center; height: 100%; }
    .total-banner { background: #f1c40f; color: #0a192f; padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.3rem; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">منظومة وجبات رمضان 🌙</div>', unsafe_allow_html=True)

# دالة جلب البيانات (مباشرة لضمان عدم الضياع)
def fetch_data():
    try:
        df = pd.read_csv(URL_SHEET_CSV)
        # التأكد من الأعمدة الـ 8 الأساسية
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
    is_open = 0 <= (now.hour * 60 + now.minute) < (16 * 60 + 30)

    if not is_open:
        st.error("⛔ الحجز مغلق حالياً. يفتح يومياً حتى 4:30 عصراً.")
    else:
        with st.form("reg_form", clear_on_submit=True):
            name = st.text_input("الاسم الثلاثي")
            sid = st.text_input("University ID")
            mail = st.text_input("إيميل الجامعة")
            loc = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
            gen = st.radio("الجنس", ["ولد", "بنت"], horizontal=True)
            rm = st.text_input("رقم الغرفة")
            if st.form_submit_button("تأكيد الحجز 🚀"):
                if name and sid and mail.lower().endswith("@zewailcity.edu.eg"):
                    res = requests.post(URL_SCRIPT, json={"action":"register","name":name,"id":sid,"email":mail,"location":loc,"gender":gen,"room":rm}).json()
                    if res.get("result") == "success": st.success("🎉 تم الحجز!")
                    else: st.warning("⚠️ مسجل بالفعل")

# --- التبويب الثاني: لوحة الإدارة (النسخة المستقرة والكاملة) ---
with tab2:
    if st.text_input("كلمة السر", type="password") == "Zewail2026":
        
        # جلب البيانات فوراً عند الدخول
        df = fetch_data()
        
        if not df.empty:
            # 1. شريط الإجمالي
            st.markdown(f'<div class="total-banner">إجمالي الحجوزات: {len(df)} وجبة</div>', unsafe_allow_html=True)
            
            # 2. إحصائيات المناطق (ولاد وبنات منفصلين)
            def count_me(l, g): return len(df[(df['Location'] == l) & (df['Gender'] == g)])
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="stat-box">🏙️ <b>الكونية</b><br><span style="color:#3498db">بنين: {count_me("عماير القرية الكونية","ولد")}</span><br><span style="color:#e91e63">بنات: {count_me("عماير القرية الكونية","بنت")}</span></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-box">💎 <b>الفيروز</b><br><span style="color:#3498db">بنين: {count_me("الفيروز / المنطقة التالتة","ولد")}</span><br><span style="color:#e91e63">بنات: {count_me("الفيروز / المنطقة التالتة","بنت")}</span></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-box">🏠 <b>Dorms</b><br><span style="color:#3498db">بنين: {count_me("سكن الجامعة (Dorms)","ولد")}</span><br><span style="color:#e91e63">بنات: {count_me("سكن الجامعة (Dorms)","بنت")}</span></div>', unsafe_allow_html=True)

            # 3. الفلاتر (التي طلبتها)
            st.markdown("---")
            st.write("### 🔍 تصفية الكشوفات التفصيلية")
            f1, f2 = st.columns(2)
            a_opt = {"الكل":"الكل","الكونية":"عماير القرية الكونية","الفيروز":"الفيروز / المنطقة التالتة","Dorms":"سكن الجامعة (Dorms)"}
            sel_a = f1.selectbox("المنطقة", list(a_opt.keys()))
            sel_g = f2.selectbox("الجنس", ["الكل", "ولد", "بنت"])

            d_df = df.copy()
            if sel_a != "الكل": d_df = d_df[d_df['Location'] == a_opt[sel_a]]
            if sel_g != "الكل": d_df = d_df[d_df['Gender'] == sel_g]
            
            st.write(f"📊 النتائج المفلترة: {len(d_df)}")
            st.dataframe(d_df, use_container_width=True)

            # 4. إجراءات الـ ID
            st.markdown("---")
            st.write("### ✅ بوابة تسليم الوجبات")
            target_id = st.text_input("ادخل ID الطالب")
            b1, b2, b3 = st.columns(3)
            
            if b1.button("✅ تأكيد استلام", use_container_width=True):
                if target_id:
                    requests.post(URL_SCRIPT, json={"action": "mark_received", "student_id": target_id})
                    st.rerun() # تحديث فوري

            if b2.button("❌ حذف حجز", use_container_width=True):
                if target_id:
                    requests.post(URL_SCRIPT, json={"action": "delete_student", "student_id": target_id})
                    st.rerun()

            if b3.button("🗑️ مسح الكل", use_container_width=True):
                if st.checkbox("تأكيد مسح بيانات اليوم"):
                    requests.post(URL_SCRIPT, json={"action": "clear_day"})
                    st.rerun()
        else:
            st.info("لا توجد بيانات مسجلة لليوم حتى الآن.")
            if st.button("🔄 تحديث يدوي"): st.rerun()
