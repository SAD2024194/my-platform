import os
import streamlit as st
from database.db_handler import increment_metric, init_db
from modules.admin_panel import render_admin_panel
from modules.intake_form import render_intake_form
from modules.portfolio import render_portfolio
from modules.ratings import render_ratings_section

import base64

st.markdown(
    """
<style>
/* 1. استدعاء خط Tajawal الاحترافي */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Tajawal', sans-serif !important;
}

/* 2. تحسين تصميم القائمة الجانبية */
section[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.88) !important;
    border-left: 1px solid rgba(229, 231, 235, 0.5);
    backdrop-filter: blur(10px);
}

/* 3. تحسين بطاقة النموذج وشكل الإدخال */
div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.93) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    border: 1px solid rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 12px 32px rgba(31, 38, 135, 0.07) !important;
}

/* 4. تحسين حقول الإدخال */
div[data-baseweb="input"] {
    border-radius: 10px !important;
    background-color: #f8fafc !important;
}

/* 5. تحسين الأزرار */
button[type="submit"], .stButton > button {
    border-radius: 10px !important;
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    font-weight: bold !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    transition: all 0.3s ease !important;
}

button[type="submit"]:hover, .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# دالة لتحويل الصورة إلى Base64 حتى يتمكن Streamlit من قراءتها كخلفية
def set_bg_hack(main_bg):
    # تحديد نوع الصورة (png أو jpg)
    main_bg_ext = main_bg.split(".")[-1]

    if os.path.exists(main_bg):
        with open(main_bg, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/{main_bg_ext};base64,{bin_str}");
                background-attachment: fixed;
                background-size: cover;
                background-position: center;
            }}
            /* تحسين شفافية البطاقات والنصوص لتبدو واضحة فوق الخلفية */
            .stApp header, .stApp > footer {{
                background-color: rgba(0,0,0,0);
            }}
            div[data-testid="stSidebar"] {{
                background-color: rgba(255, 255, 255, 0.85); /* خلفية القائمة الجانبية نصف شفافة */
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


# ضع مسار الصورة المرفقة هنا (قم بتحميل الصورة وتسميتها bg.jpg ومكانها في مجلد p)
BG_IMAGE_PATH = os.path.join("p", "bg.jpg")
set_bg_hack(BG_IMAGE_PATH)

# 1. تهيئة قاعدة البيانات أولاً قبل أي عملية
init_db()

# 2. تسجيل زيارة جديدة مرة واحدة فقط لكل جلسة زائر
if "visited" not in st.session_state:
    increment_metric("total_views")
    st.session_state["visited"] = True

# 3. تحديد المسارات المباشرة للصور داخل مجلد p
LOGO_PATH = os.path.join("p", "ss.png")
QR_PATH = os.path.join("p", "developer_qr.png")

# 4. القائمة الجانبية للتنقل الثابت
with st.sidebar:
    # 🖼️ عرض الشعار أعلى القائمة
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)

    st.title("📌 القائمة الرئيسية")

    # 🔘 خيارات التنقل
    choice = st.radio(
        "اختر الوجهة:", ["تقديم طلب مشروع", "من أعمالنا", "لوحة الإدارة"]
    )

    st.markdown("---")

    # 📱 عرض رمز الـ QR أسفل القائمة
    if os.path.exists(QR_PATH):
        st.image(
            QR_PATH,
            caption="تواصل معنا / مسح الرمز",
            use_container_width=True,
        )

# 5. توجيه الصفحات
if choice == "تقديم طلب مشروع":
    render_intake_form()
    # 🌟 عرض التقييمات في أسفل صفحة تقديم الطلب
    render_ratings_section()

elif choice == "من أعمالنا":
    # تسجيل الضغط على صفحة الأعمال مرة واحدة فقط خلال الجلسة
    if "portfolio_clicked" not in st.session_state:
        increment_metric("portfolio_clicks")
        st.session_state["portfolio_clicked"] = True

    # 🖼️ عرض معرض الأعمال
    render_portfolio()

elif choice == "لوحة الإدارة":
    render_admin_panel()