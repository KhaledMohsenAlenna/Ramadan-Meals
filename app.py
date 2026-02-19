import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# 1. إعدادات الصفحة
st.set_page_config(page_title="وجبات رمضان - مدينة زويل", layout="wide", page_icon="🌙")

# --- الروابط الهامة ---
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# 2. تحسين الشكل الجمالي (بدون صورة مبكسلة)
st.markdown("""
    <style>
    /* تغيير خلفية الموقع ولون الخط */
    .stApp {
        background-color: #0a192f;
    }
    .main-title {
        color: #f1c40f; 
        text-align: center; 
        font-family: 'Cairo', sans-serif;
        font-size: 3rem;
        font-weight: bold;
        margin-top: -50px;
        padding: 20px;
        text-shadow: 2px 2px 10px rgba(241, 196, 15, 0.3);
    }
    .sub-title {
        color: #ffffff;
        text-align: center;
        font-size: 1.5rem;
        margin-bottom: 30px;
    }
    /* تنسيق الفورم */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #112240;
        color: white;
        border: 1px solid #233554;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. العنوان الجديد
st.markdown('<div class="main-title">وجبات رمضان</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">كل عام وأنتم بخير</div>', unsafe_allow_html=True)

# 4. نظام التبويبات
tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "🔐 لوحة تحكم المسؤولين"])

# --- التبويب الأول: تسجيل الطلاب ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ انتهى وقت الحجز لليوم. الساعة الآن {now.strftime('%I:%M %p')}")
    else:
        st.success("✨ باب الحجز مفتوح الآن")
        with st.form("main_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("الاسم الثلاثي")
            student_id = col2.text_input("University ID")
            email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
            
            location = st.selectbox("مكان الاستلام", [
                "عماير القرية الكونية (عمو صبرى)", 
                "الفيروز / المنطقة التالتة", 
                "سكن الجامعة (Dorms)"
            ])
            
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
                        res = requests.post(URL_SCRIPT, json=data)
                        if res.json().get("result") == "success":
                            st.balloons(); st.success(f"تقبل الله يا {name.split()[0]}! تم تسجيل طلبك بنجاح.")
                        elif res.json().get("message") == "duplicate":
                            st.warning("⚠️ هذا الحساب سجل وجبة لليوم بالفعل.")
                    except:
                        st.error("حدث خطأ في الاتصال بالسيرفر.")

# --- التبويب الثاني: لوحة تحكم الإدمن ---
with tab2:
    st.markdown("### 🛠️ لوحة تحكم المسؤولين")
    pw = st.text_input("كلمة السر", type="password")
    
    if pw == "Zewail2026":
        st.info("مرحباً خالد، يمكنك متابعة الكشوف والحذف بالـ ID")
        
        if st.button("🔄 تحديث وعرض الجدول"):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                st.write(f"عدد المسجلين حالياً: {len(df)}")
                st.dataframe(df, use_container_width=True)
            except:
                st.error("تأكد من تفعيل Publish to web بصيغة CSV")

        st.markdown("---")
        del_id = st.text_input("ادخل الـ University ID للحذف")
        if st.button("حذف الحجز نهائياً"):
            if del_id:
                res = requests.post(URL_SCRIPT, json={"action": "delete", "student_id": del_id})
                if res.json().get("result") == "success":
                    st.success(f"تم حذف الرقم {del_id} بنجاح.")
                else:
                    st.error("الرقم غير موجود.")
