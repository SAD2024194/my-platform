import os
import streamlit as st
from database.db_handler import get_images, get_unique_titles


def render_portfolio():
    st.header("🖼️ معرض الأعمال والأنظمة المنفذة")

    # 1. جلب قائمة العناوين الفريدة (بيان / وصف الصورة) للفلترة
    # في حال عدم وجود الدالة get_unique_titles سنستبدلها بفلترة مرنة
    try:
        titles_data = get_unique_titles()
        titles_list = ["الكل"] + titles_data
    except (NameError, AttributeError):
        # حل بديل مستقر في حال كانت الدالة غير معرفة في db_handler
        all_images = get_images("الكل")
        unique_titles = list(
            dict.fromkeys([img[1] for img in all_images if img[1]])
        )
        titles_list = ["الكل"] + unique_titles

    # 2. الفلترة حسب بيان / وصف الصورة
    selected_title = st.selectbox(
        "🔍 فلترة حسب بيان / وصف الصورة:", titles_list
    )
    st.divider()

    # 3. جلب كافة الصور
    all_images = get_images("الكل")

    # 4. تصفية الصور بناءً على العنوان المحدد
    if selected_title != "الكل":
        images_to_show = [
            img for img in all_images if img[1] == selected_title
        ]
    else:
        images_to_show = all_images

    # 5. عرض النتائج
    if not images_to_show:
        st.info("لا توجد صور معروضة تحت هذا الوصف حالياً.")
    else:
        for img_id, title, img_path, cat_name in images_to_show:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
                st.caption(f"📌 **{title}** | التصنيف: *{cat_name}*")
                st.divider()