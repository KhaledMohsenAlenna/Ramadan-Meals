import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="وجبات رمضان - زويل", layout="wide", page_icon="🌙")

# --- اللينكات بتاعتك ---
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# CSS للتنسيق
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; color: white;}
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; font-weight: bold; margin-top: -30px;}
    .metric-card { background-color: #112240; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #233554;}
    </style>
    """, unsafe_allow_html=True)

# دالة تحميل البيانات بسرعة الصاروخ (Caching)
@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url)
    if len(df.columns) >= 8:
        df.columns = ["التاريخ", "الاسم", "الإيميل", "ID", "المكان", "النوع", "الغرفة", "الحالة"]
    return df

st.markdown('<div class="main-title">وجبات رمضان</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#ccd6f6; font-size: 1.2rem;">مبادرة إفطار طلاب مدينة زويل</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 تسجيل الحجز", "🔐 لوحة الإدارة الذكية"])

# === التبويب الأول: التسجيل ===
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ انتهى وقت الحجز لليوم. الساعة الآن {now.strftime('%I:%M %p')}")
    else:
        with st.form("main_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم الثلاثي")
            student_id = col2.text_input("University ID")
            email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
            
            location = st.selectbox("مكان الاستلام", ["عماير القرية الكونية (عمو صبرى)", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
            gen_col, room_col = st.columns(2)
            gender = gen_col.radio("النوع", ["ولد", "بنت"], horizontal=True)
            room = room_col.text_input("رقم الغرفة (للسكن فقط)")
            
            submit = st.form_submit_button("تأكيد حجز الوجبة")
            if submit:
                if not email.lower().endswith("@zewailcity.edu.eg"):
                    st.error("❌ عذراً، يجب التسجيل بإيميل الجامعة الرسمي")
                elif not name or not student_id:
                    st.warning("⚠️ يرجى ملء كافة البيانات")
                else:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    try:
                        with st.spinner("جاري تسجيل طلبك..."):
                            res = requests.post(URL_SCRIPT, json=data)
                            if res.json().get("result") == "success":
                                st.balloons(); st.success(f"تقبل الله يا {name.split()[0]}! تم تسجيل طلبك بنجاح.")
                                load_data.clear() # تحديث الكاش للإدمن
                            elif res.json().get("message") == "duplicate":
                                st.warning("⚠️ هذا الحساب سجل وجبة لليوم بالفعل.")
                    except:
                        st.error("حدث خطأ في الاتصال بالسيرفر.")

# === التبويب الثاني: لوحة الإدمن ===
with tab2:
    st.markdown("### 🛠️ لوحة تحكم المسؤولين")
    pw = st.text_input("كلمة السر", type="password")
    if pw == "Zewail2026":
        
        col_btn_refresh, _ = st.columns([1, 3])
        if col_btn_refresh.button("🔄 تحديث البيانات الآن"):
            load_data.clear()
            
        try:
            df = load_data(URL_SHEET_CSV)
            
            # الإحصائيات 
            st.markdown("### 📊 إحصائيات التوزيع لليوم")
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="metric-card"><h4>إجمالي الوجبات</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
            
            loc_counts = df.iloc[:, 4].value_counts() if len(df.columns) > 4 else {} # قراءة عمود المكان
            amayer_count = loc_counts.get("عماير القرية الكونية (عمو صبرى)", 0)
            fayrouz_count = loc_counts.get("الفيروز / المنطقة التالتة", 0)
            dorms_count = loc_counts.get("سكن الجامعة (Dorms)", 0)
            
            m2.markdown(f'<div class="metric-card"><h4>العماير</h4><h2>{amayer_count}</h2></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="metric-card"><h4>الفيروز</h4><h2>{fayrouz_count}</h2></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="metric-card"><h4>السكن</h4><h2>{dorms_count}</h2></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # عرض الكشوف
            st.markdown("### 📋 كشوف الأسماء")
            locations_list = ["عرض كل المناطق"] + list(df.iloc[:, 4].dropna().unique()) if len(df.columns) > 4 else ["عرض كل المناطق"]
            selected_loc = st.selectbox("اختر الكشف لعرضه:", locations_list)
            
            if selected_loc == "عرض كل المناطق":
                st.dataframe(df, use_container_width=True)
            else:
                st.dataframe(df[df.iloc[:, 4] == selected_loc], use_container_width=True)
                
        except Exception as e:
            st.warning("لم يتم تسجيل أي وجبات اليوم حتى الآن، أو يتم تجهيز كشف البيانات.")

        st.markdown("---")
        
        # تحديث الحالة (بدل الحذف النهائي)
        st.markdown("### ✅ تحديث حالة الطالب")
        update_id = st.text_input("ادخل الـ University ID للطالب")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        if col_btn1.button("✔️ تسليم الوجبة"):
            if update_id:
                res = requests.post(URL_SCRIPT, json={"action": "update_status", "student_id": update_id, "status": "تم الاستلام ✅"})
                if res.json().get("result") == "success":
                    st.success(f"تم تحديث حالة الطالب {update_id} بنجاح.")
                    load_data.clear() 
                    st.rerun()
                else:
                    st.error("لم يتم العثور على هذا الرقم.")
        
        if col_btn2.button("❌ لم يحضر"):
            if update_id:
                res = requests.post(URL_SCRIPT, json={"action": "update_status", "student_id": update_id, "status": "لم يحضر ❌"})
                if res.json().get("result") == "success":
                    st.warning(f"تم تسجيل الطالب {update_id} كـ (لم يحضر).")
                    load_data.clear()
                    st.rerun()

        if col_btn3.button("🗑️ حذف السجل بالكامل (للطوارئ)"):
            if update_id:
                res = requests.post(URL_SCRIPT, json={"action": "delete", "student_id": update_id})
                if res.json().get("result") == "success":
                    st.error(f"تم حذف الطالب {update_id} نهائياً من الشيت.")
                    load_data.clear()
                    st.rerun()
                else:
                    st.error("لم يتم العثور على هذا الرقم.")
