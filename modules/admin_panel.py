import os
import sqlite3
import streamlit as st

# استدعاء جميع الدوال المطلوبة في بداية الملف
from database.db_handler import (
    add_image_to_category,
    delete_image,
    delete_rating,
    export_requests_to_excel,
    get_all_ratings,
    get_analytics,
    get_categories,
    get_images,
    get_images_count_by_title,
    update_db_schema,
    update_request_details,
)

PORTFOLIO_DIR = "portfolio_images"
UPLOAD_DIR = "uploads"
os.makedirs(PORTFOLIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------- 1. دوال التحكم والمسح والإحصائيات -------------------


def delete_request_full(req_id, file_path):
    """حذف السجل من قاعدة البيانات وحذف الملف المرفق من القرص الصلب"""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            st.warning(f"تعذر حذف الملف: {e}")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM project_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()


def render_analytics_tab():
    """دالة عرض تبويب الإحصائيات والتحليلات"""
    st.subheader("📊 تحليلات وأداء المنصة")

    # جلب البيانات
    stats = get_analytics()
    views = stats.get("total_views", 0)
    requests = stats.get("total_requests", 0)
    portfolio_clicks = stats.get("portfolio_clicks", 0)

    # حساب نسبة التحويل (العملاء المهتمين الذين قدموا طلبات)
    conversion_rate = (
        round((requests / views) * 100, 1) if views > 0 else 0.0
    )

    # عرض الكروت بجانب بعضها
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="👀 إجمالي الزيارات", value=views)

    with col2:
        st.metric(
            label="📩 الطلبات الفعلية",
            value=requests,
            delta=f"{requests} طلب",
        )

    with col3:
        st.metric(
            label="🖼️ نقرات 'من أعمالنا'",
            value=portfolio_clicks,
            delta="تفاعل المعرض",
        )

    with col4:
        st.metric(
            label="🎯 نسبة التحويل",
            value=f"{conversion_rate}%",
            help="نسبة الزوار الذين قاموا بتقديم طلب بالفعل",
        )

    st.markdown("---")


# ------------------- 2. الواجهة الرئيسية للوحة الإدارة -------------------


def render_admin_panel():
    st.header("🔒 لوحة الإدارة")

    # تحديث هيكل قاعدة البيانات للتأكد من وجود أعمدة الماليات والجدية
    update_db_schema()

    # 📌 التحقق من تسجيل الدخول وإخفاء النموذج بعد النجاح
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        pwd = st.text_input("أدخل كلمة مرور الإدارة:", type="password")
        if pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        elif pwd != "":
            st.error("كلمة المرور خاطئة")
        return

    # زر الخروج في الأعلى
    col_head, col_out = st.columns([5, 1])
    with col_out:
        if st.button("تسجيل الخروج 🚪"):
            st.session_state.logged_in = False
            st.rerun()

    # 📌 إنشاء التبويبات الأربعة الرئيسية
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 الإحصائيات",
            "🖼️ إدارة صور المعرض",
            "📋 طلبات العملاء والماليات",
            "🌟 إدارة التقييمات",
        ]
    )

    # ------------------- التبويب الأول: الإحصائيات والتحليلات -------------------
    with tab1:
        render_analytics_tab()

    # ------------------- التبويب الثاني: إدارة المعرض -------------------
    with tab2:
        st.subheader(
            "إضافة صورة وتنسيقها مع التصنيف (حد أقصى 3 صور لكل بيان/وصف)"
        )

        categories = get_categories()
        cat_dict = {name: cat_id for cat_id, name in categories}

        with st.form("add_multi_images_form"):
            proj_title = st.text_input("بيان / وصف الصورة:")
            selected_cat_name = st.selectbox(
                "اختر التصنيف (الرأس):", list(cat_dict.keys())
            )

            st.write("اختر صور المشروع (رفع حتى 3 صور أفقية):")

            col1, col2, col3 = st.columns(3)
            with col1:
                img1 = st.file_uploader(
                    "الصورة الأولى", type=["png", "jpg", "jpeg"], key="img1"
                )
            with col2:
                img2 = st.file_uploader(
                    "الصورة الثانية", type=["png", "jpg", "jpeg"], key="img2"
                )
            with col3:
                img3 = st.file_uploader(
                    "الصورة الثالثة", type=["png", "jpg", "jpeg"], key="img3"
                )

            st.markdown("---")
            submit_btn = st.form_submit_button(
                "إدراج الصور في المسار", use_container_width=True
            )

        if submit_btn:
            if not proj_title:
                st.error("⚠️ يرجى كتابة بيان/وصف الصورة أولاً.")
            else:
                cat_id = cat_dict[selected_cat_name]

                current_count = get_images_count_by_title(proj_title)
                uploaded_imgs = [
                    img for img in [img1, img2, img3] if img is not None
                ]

                if not uploaded_imgs:
                    st.error("⚠️ يرجى اختيار صورة واحدة على الأقل.")
                elif current_count + len(uploaded_imgs) > 3:
                    st.error(
                        f"❌ تعذر الإضافة! (بيان / وصف الصورة) هذا يتضمن ({current_count}) صور حالياً. والحد الأقصى هو 3 صور لكل بيان."
                    )
                else:
                    for idx, img in enumerate(
                        uploaded_imgs, start=current_count + 1
                    ):
                        img_path = os.path.join(
                            PORTFOLIO_DIR, f"{cat_id}_{idx}_{img.name}"
                        )
                        with open(img_path, "wb") as f:
                            f.write(img.getbuffer())
                        add_image_to_category(cat_id, proj_title, img_path)

                    st.success("✅ تم إدراج الصور بنجاح!")
                    st.rerun()

        st.divider()
        st.subheader("🗑️ المسارات والصور المرتبطة حالياً")
        all_imgs = get_images("الكل")
        if all_imgs:
            for img_id, title, img_path, cat_name in all_imgs:
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.write(f"🖼️ **{title}**")
                with c2:
                    st.caption(f"التصنيف: {cat_name}")
                with c3:
                    if st.button("حذف 🗑️", key=f"del_img_{img_id}"):
                        delete_image(img_id)
                        if os.path.exists(img_path):
                            os.remove(img_path)
                        st.success("تم الحذف بنجاح!")
                        st.rerun()
        else:
            st.info("لا توجد صور مضافة حالياً.")

    # ------------------- التبويب الثالث: طلبات العملاء والتتبع المالي -------------------
    with tab3:
        col_title, col_export = st.columns([3, 1])

        with col_title:
            st.subheader("📋 متابعة طلبات العملاء والماليات")

        with col_export:
            # 📊 زر تصدير إكسل منسق
            excel_data = export_requests_to_excel()
            st.download_button(
                label="تصدير إلى Excel 📊",
                data=excel_data,
                file_name="تقرير_طلبات_العملاء.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.markdown("---")

        # جلب جميع البيانات المحدثة من قاعدة البيانات
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, phone, project_type, details, file_path, created_at,
                   status, total_amount, paid_amount, lead_quality, admin_notes, is_blacklisted
            FROM project_requests ORDER BY id DESC
        """
        )
        requests = cursor.fetchall()
        conn.close()

        if requests:
            for req in requests:
                (
                    req_id,
                    name,
                    phone,
                    proj_type,
                    details,
                    file_path,
                    created_at,
                    status,
                    total,
                    paid,
                    quality,
                    notes,
                    is_black,
                ) = req

                total = total or 0.0
                paid = paid or 0.0
                remaining = total - paid
                status = status or "طلب جديد"
                quality = quality or "غير محدد"
                notes = notes or ""

                black_badge = " ⛔ [قائمة سوداء]" if is_black else ""
                header_label = f"📌 {name or 'غير مسمى'} | ({status}) | المتبقي: {remaining:.0f} ريال {black_badge}"

                with st.expander(header_label):
                    c1, c2 = st.columns([2, 1])

                    with c1:
                        st.write(f"👤 **الاسم:** {name or 'غير محدد'}")
                        st.write(f"📞 **الجوال:** {phone or 'غير محدد'}")
                        st.write(
                            f"🏷️ **نوع البيانات:** {proj_type or 'غير محدد'}"
                        )
                        st.write(
                            f"📝 **تفاصيل العميل:**\n{details or 'لا يوجد'}"
                        )

                        if file_path and os.path.exists(file_path):
                            fname = os.path.basename(file_path)
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    f"تحميل مرفق العميل ({fname}) ⬇️",
                                    data=f,
                                    file_name=fname,
                                    key=f"dl_{req_id}",
                                )

                    with c2:
                        st.markdown("### ⚙️ إدارة الطلب والماليات")

                        status_list = [
                            "طلب جديد",
                            "جاري الاتفاق",
                            "قيد التنفيذ",
                            "مكتمل ومسلم",
                            "ملغي",
                        ]
                        status_index = (
                            status_list.index(status)
                            if status in status_list
                            else 0
                        )
                        new_status = st.selectbox(
                            "حالة المشروع:",
                            status_list,
                            index=status_index,
                            key=f"status_{req_id}",
                        )

                        quality_list = [
                            "عميل جاد جداً",
                            "استفسار فقط",
                            "متردد / متابعة",
                            "غير جاد / وهمي",
                        ]
                        quality_index = (
                            quality_list.index(quality)
                            if quality in quality_list
                            else 0
                        )
                        new_quality = st.selectbox(
                            "تقييم الجدية:",
                            quality_list,
                            index=quality_index,
                            key=f"qual_{req_id}",
                        )

                        col_tot, col_paid = st.columns(2)
                        with col_tot:
                            new_total = st.number_input(
                                "الإجمالي (ريال):",
                                value=float(total),
                                step=100.0,
                                key=f"tot_{req_id}",
                            )
                        with col_paid:
                            new_paid = st.number_input(
                                "المدفوع (ريال):",
                                value=float(paid),
                                step=100.0,
                                key=f"paid_{req_id}",
                            )

                        st.info(
                            f"💵 **المتبقي:** `{new_total - new_paid:.2f}` ريال"
                        )

                        new_notes = st.text_area(
                            "ملاحظات إدارية خاصة:",
                            value=notes,
                            key=f"notes_{req_id}",
                        )

                        new_is_black = st.checkbox(
                            "إضافة إلى القائمة السوداء ⛔",
                            value=bool(is_black),
                            key=f"black_{req_id}",
                        )

                        st.divider()
                        col_save, col_del = st.columns(2)

                        with col_save:
                            if st.button(
                                "حفظ التحديثات 💾", key=f"save_{req_id}"
                            ):
                                update_request_details(
                                    req_id,
                                    new_status,
                                    new_total,
                                    new_paid,
                                    new_quality,
                                    new_notes,
                                    new_is_black,
                                )
                                st.success("تم الحفظ بنجاح!")
                                st.rerun()

                        with col_del:
                            if st.button(
                                "حذف الطلب 🗑️",
                                key=f"del_req_{req_id}",
                                type="primary",
                            ):
                                delete_request_full(req_id, file_path)
                                st.success("تم الحذف!")
                                st.rerun()
        else:
            st.info("لا توجد طلبات مسجلة حالياً.")

    # ------------------- التبويب الرابع: إدارة التقييمات -------------------
    with tab4:
        st.subheader("⭐ جميع التقييمات المسجلة")

        all_ratings = get_all_ratings()
        if all_ratings:
            for r_id, c_name, stars, comment, created_at in all_ratings:
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.write(
                        f"👤 **{c_name}** | {'⭐' * stars} ({stars}/5)"
                    )
                    if comment:
                        st.caption(f"💬 {comment}")
                    st.caption(f"📅 {created_at}")
                with col_del:
                    if st.button("حذف 🗑️", key=f"del_rate_{r_id}"):
                        delete_rating(r_id)
                        st.success("تم حذف التقييم")
                        st.rerun()
                st.divider()
        else:
            st.info("لا توجد تقييمات مسجلة حالياً.")