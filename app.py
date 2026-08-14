import os
import streamlit as st
from database.db_handler import increment_metric, init_db
from modules.admin_panel import render_admin_panel
from modules.intake_form import render_intake_form
from modules.portfolio import render_portfolio
from modules.ratings import render_ratings_section

import base64

import streamlit as st


def apply_custom_theme():
    st.markdown(
        """
    <style>
    /* 1. استدعاء خط Cairo التقني والعصري من Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }

    /* 2. خلفية المنصة التقنية (تدرج تقني ناعم ومريح للعين) */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 50%, #e2e8f0 100%) !important;
        background-attachment: fixed !important;
    }

    /* 3. القائمة الجانبية Sidebar - تصميم كحلي احترافي */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-left: 1px solid #e2e8f0 !important;
        box-shadow: -4px 0 20px rgba(0, 0, 0, 0.03) !important;
    }

    /* عناوين القائمة الجانبية */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* 4. تصميم النماذج والبطاقات (Modern Glass Card) */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
        padding: 35px !important;
    }

    /* 5. العناوين الرئيسية والفرعية */
    h1 {
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        color: #1e293b !important;
        font-weight: 700 !important;
    }

    /* 6. تحسين خانات الإدخال (Inputs & Textareas) */
    div[data-baseweb="input"] input, 
    div[data-baseweb="textarea"] textarea {
        border-radius: 12px !important;
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #0f172a !important;
        font-size: 15px !important;
        transition: all 0.2s ease-in-out !important;
    }

    /* تأثير التركيز عند الكتابة */
    div[data-baseweb="input"]:focus-within, 
    div[data-baseweb="textarea"]:focus-within {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
    }

    /* 7. الأزرار (Buttons) - تصميم زاهي وعصري */
    button[type="submit"], .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        padding: 12px 28px !important;
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    button[type="submit"]:hover, .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 20px -3px rgba(2, 132, 199, 0.4) !important;
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
    }

    /* 8. تحسين شكل أزرار الاختيار (Radio Buttons) */
    div[role="radiogroup"] label {
        background-color: #ffffff !important;
        padding: 10px 16px !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 6px !important;
        transition: all 0.2s !important;
    }

    div[role="radiogroup"] label:hover {
        border-color: #38bdf8 !important;
        background-color: #f0f9ff !important;
    }

    /* 9. تحسين شكل كروت الإحصائيات (Metrics) */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border-radius: 16px !important;
        padding: 20px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #0284c7 !important;
        font-weight: 800 !important;
    }

    /* 10. إخفاء الهيدر الافتراضي والتذييل لـ Streamlit */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }

    </style>
    """,
        unsafe_allow_html=True,
    )


# استدعاء الدالة في بداية ملف app.py
apply_custom_theme()

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