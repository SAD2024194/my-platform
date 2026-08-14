import os
import urllib.parse
import streamlit as st

# استدعي دالة إضافة الطلب مباشرة من وحدة قاعدة البيانات
from database.db_handler import add_project_request

# 1. تهيئة الصفحة وقاعدة البيانات (تُشغّل فقط عند تشغيل هذا الملف بشكل منفصل)
if __name__ == "__main__":
    st.set_page_config(
        page_title="منصة تحويل البيانات إلى الويب",
        page_icon="🚀",
        layout="centered",
    )

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MY_WHATSAPP_NUMBER = "966505327091"


def save_to_db(name, phone, source_type, challenge, saved_path):
    """إرسال البيانات واستدعاء الدالة المعتمدة في db_handler"""
    return add_project_request(name, phone, source_type, challenge, saved_path)


def render_intake_form():
    # 🎨 تنسيق CSS مخصص للتحكم بأحجام الخطوط
    st.markdown(
        """
        <style>
            /* 1. حجم عنوان الصفحة الرئيسي */
            .main-header {
                font-size: 28px !important;
                font-weight: bold;
                text-align: center;
                color: #1E293B;
                margin-bottom: 5px;
            }

            /* 2. حجم عنوان العرض الترويجي */
            .sub-header {
                font-size: 22px !important;
                font-weight: bold;
                text-align: center;
                color: #2563EB;
                margin-bottom: 15px;
            }
            
            /* 3. حجم النصوص التوضيحية */
            .intro-text {
                font-size: 16px !important;
                text-align: center;
                color: #475569;
                line-height: 1.6;
            }
            
            /* 4. تصغير حجم عناوين الأسئلة داخل الاستمارة */
            .stTextInput label, .stSelectbox label, .stRadio label, .stTextArea label, .stFileUploader label {
                font-size: 15px !important;
                font-weight: 600 !important;
                color: #334155 !important;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # 🚀 العناوين والمقدمة في الواجهة الرئيسية
    st.markdown(
        '<div class="main-header">استقبال المشاريع</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">🚀 حوّل ملفاتك (Excel / Access) إلى نظام ويب احترافي</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
    <div class="intro-text">
        <b>خذ نفساً عميقاً... وشارِكنا تفاصيل فكرتك!</b><br>
        نساعدك في ترجمة ملفاتك اليومية ومتطلباتك إلى منصة سهلة، آمنة، ومتاحة من أي مكان.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    with st.form("intake_form"):
        # 👤 الاسم الكريم
        name = st.text_input(
            "👤 نتشرف بمعرفة اسمك الكريم وكيف نتوجه إليك؟*",
            placeholder="مثال: أ. محمد / م. سارة",
        )

        # 📞 رقم التواصل
        phone = st.text_input(
            "📞 رقم التواصل (واتساب) لمتابعة تفاصيل العرض معك:*",
            placeholder="05xxxxxxxx",
        )

        # 📁 البيئة الحالية
        source_type = st.radio(
            "📁 ما هي البيئة التي تعمل عليها حالياً؟",
            [
                "ملفات أكسل (Excel)",
                "قاعدة بيانات أكسس (MS Access)",
                "ملفات PDF وأوراق",
                "أخرى",
            ],
        )

        # 💡 التحدي والرؤية
        challenge = st.text_area(
            "💡 اشرح لنا التحدي الذي تواجهه حالياً أو ما تطمح للحصول عليه في النظام الجديد:",
            placeholder="مثال: أريد صلاحيات مختلفة للموظفين، أريد تقارير تلقائية، أريد ربطه ببرنامج آخر...",
        )

        # 📎 رفع الملف
        uploaded_file = st.file_uploader(
            "📎 أرفق نموذجاً من ملفاتك الحالية (اختياري) - يساعدنا على تقديم عرض دقيق وسريع:",
            type=["xlsx", "xls", "accdb", "mdb", "pdf", "zip"],
        )

        submit_btn = st.form_submit_button("إرسال الفكرة لبدء التحليل ✨")

    if submit_btn:
        if not name or not phone:
            st.error("⚠️ يرجى كتابة الاسم ورقم التواصل للاستمرار.")
        else:
            file_status = "لم يتم إرفاق ملف"
            saved_path = ""

            if uploaded_file is not None:
                saved_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(saved_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_status = f"تم رفع ملف باسم: ({uploaded_file.name})"

            # 🎯 1. حفظ البيانات في القاعدة واسترجاع رقم الطلب (ID)
            req_id = save_to_db(name, phone, source_type, challenge, saved_path)

            # 🎯 2. بناء نص رسالة الواتساب شاملة رقم الطلب
            msg = (
                f"*طلب تحويل نظام إلى الويب* 🚀\n"
                f"🔖 *رقم الطلب:* #{req_id}\n"
                f"👤 *الاسم:* {name}\n"
                f"📱 *رقم التواصل:* {phone}\n"
                f"📁 *البيئة الحالية:* {source_type}\n"
                f"💡 *التحدي/الطلب:* {challenge if challenge else 'غير محدد'}\n"
                f"📎 *الملف المرفق:* {file_status}"
            )

            encoded_msg = urllib.parse.quote_plus(msg)
            whatsapp_url = f"https://api.whatsapp.com/send?phone={MY_WHATSAPP_NUMBER}&text={encoded_msg}"

            # 🎯 3. إظهار رقم الطلب للعميل
            st.success(
                f"شكراً لك! تم استلام بيانات فكرتك بنجاح. 🎉 (رقم مرجع الطلب الخاص بك: **#{req_id}**)"
            )
            st.info(
                "💡 اضغط على الزر أدناه لإرسال التفاصيل مباشرة عبر الواتساب لتأكيد الاستلام وبدء النقاش:"
            )

            st.markdown(
                f'<a href="{whatsapp_url}" target="_blank" style="padding:10px 20px; background-color:#25D366; color:white; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:5px; font-size:14px;">📲 إرسال الفكرة عبر الواتساب (رقم الطلب #{req_id})</a>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    render_intake_form()