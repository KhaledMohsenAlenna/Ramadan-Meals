import streamlit as st
import requests
from datetime import datetime
import pytz

# 1. Page Config
st.set_page_config(page_title="Ramadan Iftar", layout="centered", page_icon="🌙")

# 2. Link el google script (Update this with your NEW /exec link)
url = "https://script.google.com/macros/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"
# 3. Header & Description
st.markdown("<h1 style='text-align: center;'>🌙 مبادرة إفطار صائم</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #555; margin-bottom: 20px; font-size: 18px;'>
    موقع خيري تطوعي لتنظيم وتوزيع وجبات الإفطار<br>
    لطلاب مدينة زويل المغتربين خلال شهر رمضان المبارك
</div>
""", unsafe_allow_html=True)

# 4. Check time (Cairo Time)
cairo_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(cairo_tz)
current_hour = now.hour
current_minute = now.minute

# el wa2t hay2fl 4:30 PM
is_open = True
if current_hour > 16:
    is_open = False
elif current_hour == 16 and current_minute >= 30:
    is_open = False

# 5. UI Logic
if not is_open:
    st.error(f"⛔ انتهى وقت الحجز لليوم (الساعة الآن {now.strftime('%I:%M %p')})")
    st.info("يبدأ الحجز لليوم التالي بعد منتصف الليل.")
else:
    st.success(f"✅ الحجز مفتوح حتى 4:30 عصراً")

    with st.form("iftar_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("الاسم الثلاثي")
        with col2:
            student_id = st.text_input("University ID")
            
        email = st.text_input("Zewail Email (@zewailcity.edu.eg)")
        
        locs = [
            "عماير القرية الكونية (عمو صبرى)", 
            "الفيروز / المنطقة التالتة",
            "سكن الجامعة (Dorms)"
        ]
        location = st.selectbox("مكان الاستلام", locs)
        
        gender = st.radio("النوع", ["ولد", "بنت"], horizontal=True)
        room_num = st.text_input("رقم الغرفة (لطلاب السكن فقط)")
        
        btn = st.form_submit_button("تأكيد حجز الوجبة")

        if btn:
            # First check: Empty fields
            if name == "" or student_id == "" or email == "":
                st.warning("⚠️ يا ريت تملى كل البيانات")
            
            # Second check: Zewail Email only
            elif not email.lower().endswith("@zewailcity.edu.eg"):
                st.error("❌ عذراً، التسجيل متاح فقط بـ @zewailcity.edu.eg")
            
            else:
                data_to_send = {
                    "name": name,
                    "id": student_id,
                    "email": email,
                    "location": location,
                    "gender": gender,
                    "room": room_num
                }
                
                with st.spinner("جاري فحص البيانات وتسجيل طلبك..."):
                    try:
                        res = requests.post(url, json=data_to_send)
                        # Read the JSON response from Google Script
                        result_json = res.json()
                        
                        if res.status_code == 200:
                            if result_json.get("result") == "success":
                                st.balloons()
                                st.success(f"تم تسجيل وجبتك بنجاح يا {name.split()[0]}! تقبل الله.")
                            elif result_json.get("message") == "duplicate":
                                st.warning("⚠️ أنت سجلت قبل كدة! مسموح بتسجيل وجبة واحدة فقط لكل طالب.")
                        else:
                            st.error("في مشكلة في السيرفر، جرب تاني كمان شوية.")
                    except:
                        st.error("مشكلة في الاتصال.. اتأكد من النت عندك أو إن سكريبت جوجل شغال.")


