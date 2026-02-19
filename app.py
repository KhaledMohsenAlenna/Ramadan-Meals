import streamlit as st
import requests
from datetime import datetime
import pytz

# Title and setup
st.set_page_config(page_title="Ramadan Iftar", layout="centered")
st.title("🌙 حجز وجبات إفطار رمضان")
st.write("جامعة العلوم والتكنولوجيا - مدينة زويل")

# Link el google script
url = "https://script.google.com/a/macros/zewailcity.edu.eg/s/AKfycbwR71E22SHUSUVV3PhTAk3ejtQ89oOlQRnV95efDbp1WAxCzjVWgf2YMoDuD8drHRLv/exec"

# 1. Check time (Cairo Time)
cairo_tz = pytz.timezone('Africa/Cairo')
now = datetime.now(cairo_tz)
current_hour = now.hour
current_minute = now.minute

# print(now) # for testing

# el wa2t hay2fl 4:30 PM
is_open = True
if current_hour > 16:
    is_open = False
elif current_hour == 16 and current_minute >= 30:
    is_open = False

# 2. Logic
if is_open == False:
    st.error("خلاص الوقت خلص النهاردة! (Closing Time: 4:30 PM)")
    st.info("ممكن تسجل لبكرة بعد الساعة 12 بالليل")
else:
    st.success("التسجيل شغال دلوقتي لحد الساعة 4:30 عصراً")

    # Form start
    with st.form("my_form"):
        # input fields
        name = st.text_input("الاسم الثلاثي")
        student_id = st.text_input("University ID")
        email = st.text_input("Zewail Email")
        
        # locations list
        locs = [
            "عماير القرية الكونية (عمو صبرى)", 
            "الفيروز / المنطقة التالتة",
            "سكن الجامعة (Dorms)"
        ]
        location = st.selectbox("مكان الاستلام", locs)
        
        gender = st.radio("النوع", ["ولد", "بنت"])
        
        # room number
        room_num = st.text_input("رقم الغرفة (لو انت سكن جامعة)")
        
        # submit button
        btn = st.form_submit_button("تسجيل")

        if btn:
            # validation
            if name == "" or student_id == "" or email == "":
                st.warning("يا ريت تملى كل البيانات")
            else:
                # check email domain
                if "@zewailcity.edu.eg" not in email:
                    st.error("لازم الايميل الجامعي")
                else:
                    # prepare data to send
                    data = {
                        "name": name,
                        "id": student_id,
                        "email": email,
                        "location": location,
                        "gender": gender,
                        "room": room_num
                    }
                    
                    try:
                        # sending request
                        res = requests.post(url, json=data)
                        
                        if res.status_code == 200:
                            st.balloons()
                            st.success("تمام تم التسجيل بنجاح، تقبل الله")
                        else:
                            st.error("في مشكلة حصلت، جرب تاني")
                    except:
                        st.error("اتأكد من النت عندك")
