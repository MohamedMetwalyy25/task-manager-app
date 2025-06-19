import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
# ✅ تفعيل العرض العريض
st.set_page_config(layout="wide", page_title="إدارة المهام")

import base64

def set_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
        }}

        section[data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.8); /* شفاف علشان يظهر */
            z-index: 999;
            position: relative;
        }}

        header, footer {{
            visibility: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# استدعاء الدالة



@st.cache_data
def load_tasks():
    return pd.read_excel("tasks_data.xlsx")

@st.cache_data
def load_employees():
    return pd.read_excel("employees_data.xlsx")

def login():
    set_bg_from_local("purple_background.png")
    col1, col2, col3 = st.columns([2, 1, 2])  # العمود الأوسط هو اللي هيظهر فيه الحقول

    with col2:
        st.markdown("### تسجيل الدخول")
        username = st.text_input("اسم المستخدم", key="login_username")
        password = st.text_input("كلمة المرور", type="password", key="login_password")
        login_btn = st.button("تسجيل الدخول")

        if login_btn:
            users = {"admin": "admin123", "manager1": "mgr123", "employee1": "emp123"}
            if username in users and users[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيح")

def dashboard_tab(tasks_df, emp_df):
    st.header("📊 لوحة التحكم")

    # إحصائيات عامة
    total_tasks = len(tasks_df)
    completed = len(tasks_df[tasks_df["الحالة"] == "مكتملة"])
    in_progress = len(tasks_df[tasks_df["الحالة"] == "قيد العمل"])
    late = len(tasks_df[tasks_df["الحالة"] == "متأخرة"])
    total_employees = len(emp_df)
    try:
        completion_rate = round((completed / total_tasks) * 100, 1)
    except:
        completion_rate = 0

    # ✅ تصميم الكروت الإحصائية الحديثة
    st.markdown(f"""
    <style>
    .stat-container {{
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 30px;
    }}

    .stat-card {{
        background-color: #f9f9f9;
        border-radius: 20px;
        padding: 25px;
        flex: 1;
        min-width: 180px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        transition: 0.3s ease-in-out;
    }}
    .stat-card:hover {{
        transform: scale(1.03);
    }}

    .stat-card .icon {{
        font-size: 30px;
        margin-bottom: 10px;
    }}

    .stat-card .label {{
        font-size: 16px;
        color: #888;
        margin-bottom: 5px;
    }}

    .stat-card .value {{
        font-size: 28px;
        font-weight: bold;
        color: #333;
    }}
    </style>

    <div class="stat-container">
        <div class="stat-card"><div class="icon">📋</div><div class="label">إجمالي المهام</div><div class="value">{total_tasks}</div></div>
        <div class="stat-card"><div class="icon">✅</div><div class="label">المهام المكتملة</div><div class="value">{completed}</div></div>
        <div class="stat-card"><div class="icon">🕒</div><div class="label">قيد العمل</div><div class="value">{in_progress}</div></div>
        <div class="stat-card"><div class="icon">⚠️</div><div class="label">المهام المتأخرة</div><div class="value">{late}</div></div>
        <div class="stat-card"><div class="icon">👥</div><div class="label">عدد الموظفين</div><div class="value">{total_employees}</div></div>
        <div class="stat-card"><div class="icon">📈</div><div class="label">معدل الإنجاز</div><div class="value">{completion_rate}%</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ رسم بياني شهري
    months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"]
    completed_tasks = [15, 20, 18, 22, 25, 28]
    total_tasks_data = [18, 25, 22, 26, 28, 30]
    df_chart = pd.DataFrame({
        "الشهر": months * 2,
        "عدد المهام": completed_tasks + total_tasks_data,
        "النوع": ["تم إنجازه"] * 6 + ["إجمالي المهام"] * 6
    })
    bar_fig = px.bar(df_chart, x="الشهر", y="عدد المهام", color="النوع", barmode="group", title="معدل الإنجاز الشهري")
    pie_fig = px.pie(tasks_df, names="الحالة", title="توزيع المهام حسب الحالة", hole=0.4)
    col7, col8 = st.columns(2)
    col7.plotly_chart(bar_fig, use_container_width=True)
    col8.plotly_chart(pie_fig, use_container_width=True)

    st.markdown("---")

    # ✅ المهام الحرجة
    st.subheader("🛑 المهام الحرجة")
    critical_df = tasks_df.tail(3).copy()
    critical_df.reset_index(drop=True, inplace=True)
    critical_df.index += 1
    critical_df["#"] = critical_df.index
    cols = ["#", "عنوان المهمه", "المخصص له ", "الحالة", "الأولوية", "تاريخ الاستحقاق"]
    st.dataframe(critical_df[cols], use_container_width=True)


def tasks_tab(tasks_df):
    st.header("📝 إدارة المهام")
    top_row = st.columns([6, 1])
    with top_row[0]:
        st.subheader("قائمة المهام")
    with top_row[1]:
        if "show_add_task_form" not in st.session_state:
            st.session_state["show_add_task_form"] = False
        if st.button("➕ إضافة مهمة جديدة"):
            st.session_state["show_add_task_form"] = True
    if st.session_state["show_add_task_form"]:
        with st.form("add_task_form", clear_on_submit=True):
            st.subheader("🆕 إضافة مهمة جديدة")
            title = st.text_input("عنوان المهمة:")
            description = st.text_area("الوصف:")
            emp_df = pd.read_excel("employees_data.xlsx")
            employees = emp_df["الاسم الكامل"].tolist()
            assigned_to = st.selectbox("المخصص له:", options=employees)
            priority = st.selectbox("الأولوية:", options=["عالي", "متوسط", "منخفض"])
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("تاريخ البداية:")
            with col2:
                due_date = st.date_input("تاريخ الاستحقاق:")
            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button("💾 حفظ")
            with col_cancel:
                cancel = st.form_submit_button("❌ إلغاء")
            if submitted:
                df = pd.read_excel("tasks_data.xlsx")
                new_id = len(df) + 1
                new_task = {
                    "الإجراءات": "✏️ 🗑️",
                    "عنوان المهمه": title,
                    "الوصف": description,
                    "المخصص له ": assigned_to,
                    "الحالة": "قيد العمل",
                    "الأولوية": priority,
                    "تاريخ البداية": start_date,
                    "تاريخ الاستحقاق": due_date,
                    "ID": new_id
                }
                df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
                df.to_excel("tasks_data.xlsx", index=False)
                st.cache_data.clear()

                st.success("✅ تم حفظ المهمة بنجاح")
                st.session_state["show_add_task_form"] = False
                st.rerun()
            if cancel:
                st.session_state["show_add_task_form"] = False
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("⚙️ الحالة", ["جميع الحالات", "قيد العمل", "مكتملة", "متأخرة"])
    with col2:
        priority_filter = st.selectbox("📌 الأولوية", ["جميع الأولويات", "عالي", "متوسط", "منخفض"])
    with col3:
        search_text = st.text_input("🔍 بحث (في العنوان أو الوصف)")
    filtered_df = tasks_df.copy()
    if status_filter != "جميع الحالات":
        filtered_df = filtered_df[filtered_df["الحالة"] == status_filter]
    if priority_filter != "جميع الأولويات":
        filtered_df = filtered_df[filtered_df["الأولوية"] == priority_filter]
    if search_text.strip() != "":
        filtered_df = filtered_df[
            filtered_df["عنوان المهمه"].str.contains(search_text, na=False) |
            filtered_df["الوصف"].str.contains(search_text, na=False)
        ]
    filtered_df.reset_index(drop=True, inplace=True)
    filtered_df.index += 1
    filtered_df["#"] = filtered_df.index
    columns = ["#", "عنوان المهمه", "الوصف", "المخصص له ", "الحالة", "الأولوية", "تاريخ البداية", "تاريخ الاستحقاق"]
    st.dataframe(filtered_df[columns], use_container_width=True)

# ✅ التعديل هنا
def employees_tab(emp_df):
    st.header("👥 إدارة الموظفين")
    top_row = st.columns([6, 1])
    with top_row[0]:
        st.subheader("قائمة الموظفين")
    with top_row[1]:
        if "show_add_employee_form" not in st.session_state:
            st.session_state["show_add_employee_form"] = False
        if st.button("➕ إضافة موظف جديد"):
            st.session_state["show_add_employee_form"] = True

    if st.session_state["show_add_employee_form"]:
        with st.form("add_employee_form", clear_on_submit=True):
            st.subheader("🆕 إضافة موظف")
            full_name = st.text_input("الاسم الكامل:")
            username = st.text_input("اسم المستخدم:")
            email = st.text_input("البريد الإلكتروني:")
            role = st.selectbox("الدور:", ["موظف", "مدير", "مدير النظام"])
            status = st.selectbox("الحالة:", ["نشط", "غير نشط"])
            join_date = st.date_input("تاريخ الإنضمام:")
            col1, col2 = st.columns(2)
            with col1:
                save = st.form_submit_button("💾 حفظ")
            with col2:
                cancel = st.form_submit_button("❌ إلغاء")
            if save:
                df = pd.read_excel("employees_data.xlsx")
                new_id = len(df) + 1
                new_employee = {
                    "#": new_id,
                    "الاسم الكامل": full_name,
                    "اسم المستخدم": username,
                    "البريد الإلكتروني": email,
                    "الدور": role,
                    "الحالة": status,
                    "تاريخ الإنضمام": join_date
                }
                df = pd.concat([df, pd.DataFrame([new_employee])], ignore_index=True)
                df.to_excel("employees_data.xlsx", index=False)
                st.cache_data.clear()

                new_emp_df = pd.read_excel("employees_data.xlsx")
                st.session_state["show_add_employee_form"] = False
                st.success("✅ تم إضافة الموظف بنجاح")
                st.dataframe(new_emp_df, use_container_width=True)
                return
            if cancel:
                st.session_state["show_add_employee_form"] = False

    st.markdown("---")
# ترتيب الأعمدة يدويًا للتأكد من ظهورها كاملة وبالترتيب
    columns = ["#", "الاسم الكامل", "اسم المستخدم", "البريد الإلكتروني", "الدور", "الحالة", "تاريخ الإنضمام"]
    st.dataframe(emp_df[columns], use_container_width=True)



def generate_pdf(title_text, filtered_df, chart_title, chart_data, filename):
    from matplotlib import pyplot as plt
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import arabic_reshaper
    from bidi.algorithm import get_display
    import tempfile
    import os
    from io import BytesIO

    font_path = "C:/Windows/Fonts/arial.ttf"
    pdfmetrics.registerFont(TTFont("Arabic", font_path))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    reshaped_title = get_display(arabic_reshaper.reshape(title_text))
    elements.append(Paragraph(f"<font name='Arabic' size=16>{reshaped_title}</font>", styles["Title"]))
    elements.append(Spacer(1, 20))

    fig, ax = plt.subplots()
    reshaped_chart_title = get_display(arabic_reshaper.reshape(chart_title))
    chart_data.plot(kind="pie", autopct="%1.1f%%", startangle=90, ax=ax)
    ax.set_title(reshaped_chart_title, fontsize=14)
    ax.set_ylabel("")
    chart_buf = BytesIO()
    fig.savefig(chart_buf, format="png", bbox_inches="tight")
    plt.close()

    chart_path = os.path.join(tempfile.gettempdir(), f"{filename}_chart.png")
    with open(chart_path, "wb") as f:
        f.write(chart_buf.getvalue())
    elements.append(Image(chart_path, width=400, height=300))
    elements.append(Spacer(1, 20))

    headers = ["عنوان المهمه", "المخصص له ", "الحالة", "الأولوية", "تاريخ البداية", "تاريخ الاستحقاق"]
    table_data = [[get_display(arabic_reshaper.reshape(col)) for col in headers]]
    for _, row in filtered_df.iterrows():
        table_data.append([
            get_display(arabic_reshaper.reshape(str(row["عنوان المهمه"]))),
            get_display(arabic_reshaper.reshape(str(row["المخصص له "]))),
            get_display(arabic_reshaper.reshape(str(row["الحالة"]))),
            get_display(arabic_reshaper.reshape(str(row["الأولوية"]))),
            str(row["تاريخ البداية"]),
            str(row["تاريخ الاستحقاق"]),
        ])

    table = Table(table_data, colWidths=[90, 70, 50, 50, 60, 60])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arabic"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    doc.build(elements)
    return buffer



def reports_tab(tasks_df):
    st.header("📊 التقارير والإحصائيات")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📗 تقرير الأسبوع الحالي")
        if st.button("📄 عرض التقرير", key="weekly"):
            pdf_buffer = generate_pdf(
                "تقرير الأسبوع الحالي",
                tasks_df,
                "توزيع المهام حسب الحالة",
                tasks_df["الحالة"].value_counts(),
                "weekly"
            )
            st.download_button("📥 تحميل PDF", data=pdf_buffer.getvalue(), file_name="weekly_report.pdf")

        st.subheader("🕑 تقرير المهام المتأخرة")
        late_df = tasks_df[tasks_df["الحالة"] == "متأخرة"]
        if st.button("📄 عرض التقرير", key="late"):
            pdf_buffer = generate_pdf(
                "تقرير المهام المتأخرة",
                late_df,
                "توزيع المهام المتأخرة حسب الأولوية",
                late_df["الأولوية"].value_counts(),
                "late_tasks"
            )
            st.download_button("📥 تحميل PDF", data=pdf_buffer.getvalue(), file_name="late_tasks_report.pdf")

    with col2:
        st.subheader("📈 تقرير الإنتاجية")
        done_df = tasks_df[tasks_df["الحالة"] == "مكتملة"]
        if st.button("📄 عرض التقرير", key="productivity"):
            pdf_buffer = generate_pdf(
                "تقرير الإنتاجية",
                done_df,
                "توزيع المهام المكتملة حسب الموظف",
                done_df["المخصص له "].value_counts(),
                "productivity"
            )
            st.download_button("📥 تحميل PDF", data=pdf_buffer.getvalue(), file_name="productivity_report.pdf")

        st.subheader("🧾 تقرير الأداء الشهري")
        if st.button("📄 عرض التقرير", key="monthly"):
            pdf_buffer = generate_pdf(
                "تقرير الأداء الشهري",
                tasks_df,
                "توزيع المهام لكل الموظفين",
                tasks_df["المخصص له "].value_counts(),
                "monthly"
            )
            st.download_button("📥 تحميل PDF", data=pdf_buffer.getvalue(), file_name="monthly_performance.pdf")

    st.header("📄 التقارير")
    st.write("تقرير المهام حسب الحالة:")
    st.bar_chart(tasks_df["الحالة"].value_counts())

def email_tab():
    st.header("✉️ استيراد الإيميل")
    st.info("سيتم إضافة هذه الميزة لاحقًا.")

def main():
    st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
        margin: 0;
        padding: 0;
    }
    .main .block-container {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    .element-container {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stApp {
        padding: 0;
        margin: 0;
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
        width: 280px !important;
    }
</style>
    """,
    unsafe_allow_html=True
)


    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    ...

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False
    if st.session_state["refresh"]:
        st.session_state["refresh"] = False
        st.rerun()
    if not st.session_state["logged_in"]:
        login()
        return

    col1, col2 = st.columns([1, 1])

    with col1:
       if st.button("🔁 تحديث البيانات"):
        st.session_state["refresh"] = True

    with col2:
       if st.button("🚪 خروج"):
        st.session_state["logged_in"] = False
        st.success("👋 تم تسجيل الخروج بنجاح")
        st.rerun()


    

    tasks_df = load_tasks()
    emp_df = load_employees()

    tabs = {
        "📊 لوحة التحكم": lambda: dashboard_tab(tasks_df, emp_df),
        "📝 المهام": lambda: tasks_tab(tasks_df),
        "👥 الموظفين": lambda: employees_tab(emp_df),
        "📄 التقارير": lambda: reports_tab(tasks_df),
        "✉️ استيراد الإيميل": email_tab
    }

    st.sidebar.title("القائمة")
    selection = st.sidebar.radio("انتقل إلى:", list(tabs.keys()))
    tabs[selection]()

if __name__ == "__main__":
    main()
