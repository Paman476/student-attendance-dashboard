# 🎓 Animated Attendance Dashboard (Modern Version)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
from streamlit_lottie import st_lottie

# ---------------- Page config ----------------
st.set_page_config(page_title="Attendance Dashboard", page_icon="🎓", layout="wide")

# ---------------- CSS Animations ----------------
st.markdown("""
<style>
@keyframes fadeInUp {
  from {opacity: 0; transform: translateY(20px);}
  to {opacity: 1; transform: translateY(0);}
}
div[data-testid="stMetricValue"], .stDataFrame, .stPlotlyChart, .stBarChart, .stImage {
  animation: fadeInUp 0.8s ease-out;
}
h1, h2, h3 {
  animation: fadeInUp 0.8s ease-out;
}
.stButton>button {
  background-color:#ff8c42; color: #0f1720; border: none;
  transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
  transform: scale(1.05);
  box-shadow: 0 0 12px #ff8c42;
}
.css-1d391kg { background-color: #0f1720; }
.stApp {
  background: linear-gradient(180deg,#0b1220 0%, #0f1720 100%);
  color: #E6EEF3;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Load Lottie Animation ----------------
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_graduation = load_lottie_url("https://assets8.lottiefiles.com/packages/lf20_rsaqf1by.json")

# ---------------- Logo + Title ----------------
logo_url = "https://media.licdn.com/dms/image/v2/D4D0BAQFBgbK2g1w9kw/company-logo_200_200/company-logo_200_200/0/1693174200475?e=2147483647&v=beta&t=1xcMKKhtsRau_CUs3EUsOpnGXsQe6e5qAfQbJ5GxA6g"
try:
    response = requests.get(logo_url, timeout=5)
    logo_img = Image.open(BytesIO(response.content))
    col_logo, col_title, col_anim = st.columns([1, 3, 1])
    with col_logo:
        st.image(logo_img, use_column_width=True)
    with col_title:
        st.title("🎓 Student Attendance Dashboard")
        st.write("Search a student to view their **attendance performance**.")
    with col_anim:
        st_lottie(lottie_graduation, speed=1, width=120, key="grad")
except:
    st.title("🎓 Student Attendance Dashboard")

# ---------------- Load Data ----------------
@st.cache_data
def load_data(path='attendance.csv'):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df['Attendance'] = df['Attendance'].astype(str).str.strip().str.title()
    df['Name'] = df['Name'].astype(str).str.strip()
    df['Subject'] = df['Subject'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Attendance_Binary'] = df['Attendance'].map({'Present': 1, 'Absent': 0})
    if 'Marks' in df.columns:
        df['Marks'] = pd.to_numeric(df['Marks'], errors='coerce')
    else:
        df['Marks'] = pd.NA
    return df

data = load_data('attendance.csv')

# ---------------- Sidebar ----------------
st.sidebar.header("Filters & Search")
student_input = st.sidebar.text_input("Search student name (exact):", "")
subject_filter = st.sidebar.selectbox(
    "Subject filter (All subjects shown by default):",
    ["All"] + sorted(data['Subject'].unique())
)
date_min, date_max = data['Date'].min(), data['Date'].max()
date_range = st.sidebar.date_input(
    "Date range:",
    value=(date_min.date(), date_max.date()),
    min_value=date_min.date(),
    max_value=date_max.date()
)

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(data))
col2.metric("Students", data['Name'].nunique())
col3.metric("Subjects", data['Subject'].nunique())
col4.metric("Date Range", f"{date_min.date()} → {date_max.date()}")

st.markdown("---")

# ---------------- Filter Data ----------------
start_date, end_date = date_range
df_filtered = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]
if subject_filter != "All":
    df_filtered = df_filtered[df_filtered['Subject'] == subject_filter]

# ---------------- Student Search Logic ----------------
if student_input.strip():
    student_name = student_input.strip()
    matches = [n for n in df_filtered['Name'].unique() if n.lower() == student_name.lower()]
    if not matches:
        st.error("❌ No record found for that student.")
    else:
        student = matches[0]
        sdata = df_filtered[df_filtered['Name'] == student]
        if sdata.empty:
            st.warning("No records for this student in selected filters.")
        else:
            # -------- Bar Chart --------
            st.subheader("📘 Aggregated Subject Attendance (Filtered)")
            agg = sdata.groupby('Subject')['Attendance_Binary'].mean() * 100
            st.bar_chart(agg.sort_values(ascending=False))

            st.markdown("---")

            # -------- Combined Pie (All Subjects in One Circle) --------
            st.subheader("🟢🔴 Overall Attendance Ratio (All Subjects Combined)")
            total_classes = len(sdata)
            present_count = int(sdata['Attendance_Binary'].sum())
            absent_count = total_classes - present_count

            fig, ax = plt.subplots(figsize=(5,5))
            ax.pie(
                [present_count, absent_count],
                labels=['Present', 'Absent'],
                colors=['#00C853', '#E74C3C'],
                autopct='%1.1f%%',
                startangle=90,
                textprops={'color':'white', 'fontsize':12}
            )
            ax.axis('equal')
            st.pyplot(fig)

            st.markdown("---")

            # -------- Summary Metrics --------
            st.header(f"👤 {student} — Summary")
            attendance_pct = (present_count / total_classes * 100) if total_classes else 0
            avg_marks = sdata['Marks'].mean() if pd.notna(sdata['Marks']).any() else None

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Classes", total_classes)
            c2.metric("Present", present_count)
            c3.metric("Absent", absent_count)
            c4.metric("Attendance %", f"{attendance_pct:.2f}%")

            if avg_marks and not pd.isna(avg_marks):
                st.write(f"**Average Marks:** {avg_marks:.2f}")

            st.markdown("---")

            # -------- Subject-wise Summary --------
            st.subheader("📄 Subject-wise Summary")
            subj_summary = sdata.groupby('Subject').agg(
                Present=('Attendance_Binary', 'sum'),
                Total=('Attendance_Binary', 'count')
            )
            subj_summary['Attendance %'] = (subj_summary['Present'] / subj_summary['Total'] * 100).round(2)
            st.dataframe(subj_summary.sort_values('Attendance %', ascending=False))

            st.markdown("---")

            # -------- Download Button --------
            csv_bytes = sdata.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Student CSV",
                csv_bytes,
                file_name=f"{student}_attendance.csv",
                mime="text/csv"
            )

else:
    st.info("Type a student's name in sidebar to view their dashboard.")
    st.subheader("📘 Aggregated Subject Attendance (Filtered)")
    agg = df_filtered.groupby('Subject')['Attendance_Binary'].mean() * 100
    st.bar_chart(agg.sort_values(ascending=False))

# ---------------- Footer ----------------
st.markdown("---")
st.caption("✨ Animated Attendance Dashboard — Dark theme with smooth fade-in effects, built for presentation.")
