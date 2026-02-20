import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import random

st.set_page_config(page_title="وجبات رمضان - مدينة زويل", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqNEDayFNEgFoQqq-wF29BRkxF9u5YIrPYac54o3_hy3O5MvuQiQiwKKQ9oSlkx08JnXeN-mPu95Qk/pub?output=csv"

# css style
st.markdown("""
    <style>
    .stApp { background-color: #0a192f; }
    .main-title { color: #f1c40f; text-align: center; font-size: 3rem; margin-top: -50px;}
    .sub-title { color: #ffffff; text-align: center; font-size: 1.5rem; margin-bottom: 30px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">وجبات رمضان</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">كل عام وأنتم بخير</div>', unsafe_allow_html=True)

# function to send otp email
def send_code(receiver_email, code):
    sender = st.secrets["my_email"]
    password = st.secrets["my_password"]
    
    msg = MIMEText("كود التأكيد الخاص بك هو: " + str(code))
    msg['Subject'] = 'تأكيد حجز الإفطار - مدينة زويل'
    msg['From'] = sender
    msg['To'] = receiver_email
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.sendmail(sender, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

tab1, tab2 = st.tabs(["تسجيل حجز جديد", "لوحة تحكم المسؤولين"])

with tab1:
    cairo_tz = pytz.timezone('Africa/Cairo')
    now = datetime.now(cairo_tz)
    
    is_open = False
    if now.hour >= 0 and now.hour < 16:
        is_open = True
    elif now.hour == 16 and now.minute < 30:
        is_open = True

    if is_open == False:
        st.error("انتهى وقت الحجز لليوم")
    else:
        # session state variables
        if 'otp' not in st.session_state:
            st.session_state.otp = ""
        if 'email_sent' not in st.session_state:
            st.session_state.email_sent = False

        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
        
        locations = ["عماير القرية الكونية", "الفيروز / المنطقة التالتة", "سكن الجامعة (Dorms)"]
        location = st.selectbox("مكان الاستلام", locations)
        
        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
        with col2:
            room = st.text_input("رقم الغرفة (للسكن فقط)")
        
        # check if email is sent
        if st.session_state.email_sent == False:
            if st.button("إرسال كود التأكيد"):
                if name == "" or student_id == "" or email == "":
                    st.warning("اكتب كل البيانات الاول")
                elif email.lower().endswith("@zewailcity.edu.eg") == False:
                    st.error("لازم تستخدم ايميل الجامعة")
                else:
                    generated_otp = random.randint(1000, 9999)
                    st.session_state.otp = str(generated_otp)
                    
                    with st.spinner("جاري ارسال الكود..."):
                        is_sent = send_code(email, st.session_state.otp)
                        if is_sent == True:
                            st.session_state.email_sent = True
                            st.rerun()
                        else:
                            st.error("فشل الارسال، راجع اعدادات الايميل")
        
        # if email is sent, show the confirmation box
        if st.session_state.email_sent == True:
            st.success("الكود اتبعت للايميل بتاعك")
            user_otp = st.text_input("اكتب الكود هنا")
            
            if st.button("تأكيد وحجز الوجبة"):
                if user_otp == st.session_state.otp:
                    data = {
                        "name": name, 
                        "id": student_id, 
                        "email": email, 
                        "location": location, 
                        "gender": gender, 
                        "room": room
                    }
                    
                    with st.spinner("جاري الحجز..."):
                        res = requests.post(URL_SCRIPT, json=data)
                        res_json = res.json()
                        
                        if res_json.get("result") == "success":
                            st.balloons()
                            st.success("تم تسجيل وجبتك بنجاح")
                            st.session_state.email_sent = False
                        elif res_json.get("message") == "duplicate":
                            st.warning("الرقم الجامعي أو الإيميل سجل قبل كدا النهاردة")
                else:
                    st.error("الكود غلط، راجع الايميل تاني")

with tab2:
    st.write("لوحة تحكم المسؤولين")
    pw = st.text_input("كلمة السر", type="password")
    
    if pw == "Zewail2026":
        st.success("اهلا بك")
        
        if st.button("عرض الجدول"):
            try:
                df = pd.read_csv(URL_SHEET_CSV)
                st.write("عدد المسجلين: " + str(len(df)))
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error("مشكلة في تحميل الشيت")

        st.write("حذف بيانات طالب")
        del_id = st.text_input("ادخل ال ID للحذف")
        
        if st.button("تأكيد الحذف"):
            if del_id != "":
                del_data = {"action": "delete", "student_id": del_id}
                res = requests.post(URL_SCRIPT, json=del_data)
                res_json = res.json()
                
                if res_json.get("result") == "success":
                    st.success("تم مسح الطالب بنجاح")
                else:
                    st.error("ال ID مش موجود في الحجوزات")
            else:
                st.warning("اكتب الرقم الاول")
