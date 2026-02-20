import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="وجبات رمضان - مدينة زويل", layout="wide")

# الروابط الخاصة بك
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyu51AdH5kuXUMHV2gVEHLguQNNNc0u8lnEFlDoB4czzAz7Le6rPBbSxUuCFjnrHen3/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# 2. تنسيق الموقع (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; }
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; margin-top: -50px; font-weight: bold;}
    .sub-title { color: #ffffff; text-align: center; font-size: 1.5rem; margin-bottom: 30px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">وجبات رمضان</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">كل عام وأنتم بخير</div>', unsafe_allow_html=True)

# 3. دالة إرسال الإيميل مع فحص الأخطاء
def send_code(receiver_email, code):
    try:
        # قراءة البيانات من الـ Secrets السري
        sender = st.secrets["my_email"]
        password = st.secrets["my_password"]
        
        msg = MIMEText(f"كود التأكيد الخاص بك هو: {code}")
        msg['Subject'] = 'تأكيد حجز الإفطار - مدينة زويل'
        msg['From'] = sender
        msg['To'] = receiver_email
        
        # الاتصال بسيرفر جوجل
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver_email, msg.as_string())
        return "success"
    except Exception as e:
        # إرجاع نص الخطأ الحقيقي للتشخيص
        return str(e)

# 4. التبويبات (Tabs)
tab1, tab2 = st.tabs(["📝 تسجيل حجز جديد", "🔐 لوحة الإدارة الذكية"])

# --- التبويب الأول: التسجيل ---
with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    
    # فتح الحجز من 12 صباحاً لـ 4:30 عصراً
    is_open = (0 <= now.hour < 16) or (now.hour == 16 and now.minute < 30)

    if not is_open:
        st.error(f"⛔ انتهى وقت الحجز لليوم. الساعة الآن {now.strftime('%I:%M %p')}")
    else:
        if 'otp' not in st.session_state:
            st.session_state.otp = ""
        if 'email_sent' not in st.session_state:
            st.session_state.email_sent = False

        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("الإيميل الجامعي الرسمي")
        
        location = st.selectbox("مكان الاستلام", ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"])
        
        col1, col2 = st.columns(2)
        gender = col1.radio("النوع", ["ولد", "بنت"], horizontal=True)
        room = col2.text_input("رقم الغرفة (للسكن فقط)")
        
        # المرحلة الأولى: إرسال الكود
        if not st.session_state.email_sent:
            if st.button("إرسال كود التأكيد"):
                if not name or not student_id or not email:
                    st.warning("⚠️ يرجى ملء كافة البيانات أولاً")
                elif not email.lower().endswith("@zewailcity.edu.eg"):
                    st.error("❌ يجب استخدام إيميل الجامعة الرسمي")
                else:
                    st.session_state.otp = str(random.randint(1000, 9999))
                    with st.spinner("جاري إرسال الكود..."):
                        result = send_code(email, st.session_state.otp)
                        if result == "success":
                            st.session_state.email_sent = True
                            st.rerun()
                        else:
                            # عرض الخطأ الحقيقي
                            st.error(f"❌ فشل الإرسال. السبب: {result}")

        # المرحلة الثانية: التأكيد والحجز
        if st.session_state.email_sent:
            st.success("✅ تم إرسال الكود لإيميلك (افحص الـ Spam)")
            st.info("📞 للدعم: 01025687330 | 01094541437 | 01017194365")
            
            user_code = st.text_input("اكتب الكود المكون من 4 أرقام")
            if st.button("تأكيد وحجز الوجبة"):
                if user_code == st.session_state.otp:
                    data = {"name": name, "id": student_id, "email": email, "location": location, "gender": gender, "room": room}
                    with st.spinner("جاري الحجز..."):
                        res = requests.post(URL_SCRIPT, json=data)
                        try:
                            if res.json().get("result") == "success":
                                st.balloons()
                                st.success("🎉 تم تسجيل حجزك بنجاح!")
                                st.session_state.email_sent = False
                            else:
                                st.warning("⚠️ أنت مسجل بالفعل لهذا اليوم")
                        except:
                            st.error("⚠️ مشكلة في الرد من جوجل سكريبت")
                else:
                    st.error("❌ الكود غير صحيح")

# --- التبويب الثاني: الإدمن ---
with tab2:
    st.write("### 🛠️ لوحة تحكم المسؤولين")
    admin_pw = st.text_input("كلمة السر", type="password")
    if admin_pw == "Zewail2026":
        st.success("أهلاً يا خالد")
        if st.button("🔄 عرض كشف الأسماء الحالية"):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                st.write(f"إجمالي الحجوزات: {len(df)}")
                st.dataframe(df, use_container_width=True)
            except:
                st.error("❌ فشل تحميل البيانات")

        st.markdown("---")
        del_id = st.text_input("ادخل ID الطالب للحذف")
        if st.button("🗑️ حذف الحجز"):
            if del_id:
                res = requests.post(URL_SCRIPT, json={"action": "delete", "student_id": del_id})
                try:
                    if res.json().get("result") == "success":
                        st.success(f"✅ تم حذف الطالب {del_id}")
                    else:
                        st.error("❌ الـ ID غير موجود")
                except:
                    st.error("⚠️ جوجل سكريبت رد بـ HTML. تأكد من عمل New Deployment.")
