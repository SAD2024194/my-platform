import streamlit as st
from database.db_handler import add_rating, get_all_ratings, get_average_rating

def render_ratings_section():
    """عرض قسم التقييمات ومتوسط النجوم ونموذج الإضافة في الشاشة الرئيسية"""
    st.divider()
    st.subheader("⭐ آراء وتقييمات العملاء")

    avg_rating, total_count = get_average_rating()

    col_avg, col_space = st.columns([2, 1])

    with col_avg:
        if total_count > 0:
            stars_display = "⭐" * int(round(avg_rating))
            st.markdown(f"### **{avg_rating} / 5** {stars_display}")
            st.caption(f"بناءً على ({total_count}) تقييم من عملائنا")
        else:
            st.info("لا توجد تقييمات حالياً. كن أول من يقيّم خدمتنا!")



    # ✍️ نموذج إضافة تقييم جديد
    with st.expander("✍️ أضف تقييمك لخدمتنا"):
        with st.form("add_rating_form", clear_on_submit=True):
            r_name = st.text_input("الاسم الكريم:*")
            r_stars = st.slider("التقييم من 5 نجوم:*", min_value=1, max_value=5, value=5)
            r_comment = st.text_area("رأيك في الخدمة (اختياري):")
            
            submit_rating = st.form_submit_button("إرسال التقييم 🌟", use_container_width=True)
            
        if submit_rating:
            if not r_name:
                st.error("⚠️ يرجى كتابة اسمك أولاً لإرسال التقييم.")
            else:
                add_rating(r_name, r_stars, r_comment)
                st.success("شكراً لك! تم إضافة تقييمك بنجاح ❤️")
                st.rerun()