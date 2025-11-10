import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
import time

# ---------------- Page config & styling ----------------
st.set_page_config(page_title="Animated Attendance Dashboard", page_icon="🎓", layout="wide")

# ---------------- CSS Animations & Theme ----------------
st.markdown("""
<style>
/* Background gradient and smooth transitions */
.stApp {
    background: linear-gradient(180deg,#0b1220 0%, #0f1720 100%);
    color: #E6EEF3;
    transition: all 0.5s ease-in-out;
}

/* Glow for headings */
h1, h2, h3 {
    color: #E6EEF3;
    text-shadow: 0 0 15px rgba(255, 140, 66, 0.5);
    animation: fadeInDown 1.2s ease;
}

/* Buttons */
.stButton>button {
    background-color:#ff8c42;
    color: #0f1720;
    border: none;
    border-radius:10px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color:#ffa45c;
    transform: scale(1.05);
}

/* Charts Fade-in */
[data-testid="stHorizontalBlock"] {
    animation: fadeIn 1.3s ease;
}

/* Custom animations */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
@keyframes fadeInDown {
    from {opacity: 0; transform: translateY(-10px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ---------------- Logo Section ----------------
logo_url = "https://media.licdn.com/dms/image/v2/D4D0BAQFBgbK2g1w9kw/company-logo_200_200/company-logo_200_200/0/1693174200475?e=2147483647&v=beta&t=1xcMKKhtsRau_CUs3EUsOpnGXsQe6e5qAfQbJ5GxA6g"
try:
    response = requests.get(logo_url, timeout=5)
    logo_img = Image.open(BytesIO(response.content))
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image(logo_img, use_column_width=True)
    with col_title:
        st.title("🎓 Student Attendance Dashboard")
except:
    st.title("🎓 Student Attendance Dashboard")

st.markdown("Search a student to view their **attendance percentage** month-wise with animated insights 💫")

# ---------------- Load Data ----------------
@st.cache_data
def load_data(path='attendance.csv'):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df['Attendance'] = df['Attendance'].astype(str).str.strip().str.title()
    df['Name'] = df['Name'].astype(str).str.strip()
    df['Subject'] = df['Subject'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Attendance_Binary'] = df['Attendance'].map({'Present': 1, 'Absent': 0})
    return df

data = load_data('attendance.csv')

# ---------------- Sidebar ----------------
st.sidebar.header("🎯 Filters & Search")
student_input = st.sidebar.text_input("Search student name (exact):", "")
month_select = st.sidebar.selectbox(
    "Select Month:",
    sorted(data['Date'].dt.strftime('%B %Y').unique())
)

# Month filter
month_dt = pd.to_datetime(month_select)
df_filtered = data[
    (data['Date'].dt.month == month_dt.month) & 
    (data['Date'].dt.year == month_dt.year)
]

# ---------------- Dashboard Top KPIs ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(df_filtered))
col2.metric("Students", df_filtered['Name'].nunique())
col3.metric("Subjects", df_filtered['Subject'].nunique())
col4.metric("Selected Month", month_select)
st.markdown("---")

# ---------------- Student Filter Logic ----------------
if student_input.strip():
    student_name = student_input.strip()
    matches = [n for n in df_filtered['Name'].unique() if n.lower() == student_name.lower()]
    if not matches:
        st.error("❌ No record found for that student in this month.")
    else:
        student_name_matched = matches[0]
        sdata = df_filtered[df_filtered['Name'] == student_name_matched]
        if sdata.empty:
            st.warning("No attendance for this student in selected month.")
        else:
            time.sleep(0.4)  # small delay for animation feel

            # 📘 Bar Chart
            st.subheader("📘 Aggregated Subject Attendance (Filtered)")
            agg = sdata.groupby('Subject')['Attendance_Binary'].mean() * 100
            st.bar_chart(agg.sort_values(ascending=False))
            st.markdown("---")

            # 🟢🔴 Animated Pie Chart
            st.subheader("🟢🔴 Overall Attendance Ratio (All Subjects Combined)")
            present = int(sdata['Attendance_Binary'].sum())
            absent = len(sdata) - present
            fig, ax = plt.subplots(figsize=(5,5))
            wedges, texts, autotexts = ax.pie(
                [present, absent],
                labels=["Present", "Absent"],
                colors=["#33FF57", "#FF3333"],
                autopct='%1.1f%%',
                startangle=time.time() * 20 % 360,  # rotation animation
                textprops={'color':'white', 'fontsize':12}
            )
            for w in wedges:
                w.set_edgecolor("white")
                w.set_linewidth(1.5)
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("---")

            # 👤 Summary
            st.header(f"👤 {student_name_matched} — Summary ({month_select})")
            total_classes = len(sdata)
            attendance_pct = (sdata['Attendance_Binary'].mean() * 100).round(2)
            colA, colB, colC = st.columns(3)
            colA.metric("Total Classes", total_classes)
            colB.metric("Present", present)
            colC.metric("Attendance %", f"{attendance_pct:.2f}%")

            st.markdown("---")

            # 📄 Table
            st.subheader("📄 Subject-wise Summary")
            summary = sdata.groupby('Subject').agg(
                Present=('Attendance_Binary', 'sum'),
                Total=('Attendance_Binary', 'count')
            )
            summary['Attendance %'] = (summary['Present']/summary['Total']*100).round(2)
            st.dataframe(summary.sort_values('Attendance %', ascending=False))
else:
    st.info("Type a student's exact name in sidebar to view month-wise animated analysis.")
    st.subheader("📘 Aggregated Subject Attendance (All Students)")
    agg = df_filtered.groupby('Subject')['Attendance_Binary'].mean() * 100
    st.bar_chart(agg.sort_values(ascending=False))

# ---------------- Footer ----------------
st.markdown("---")
st.caption("✨ Animated Dashboard | Built for Presentation — smooth transitions, glowing metrics, and modern charts.")
