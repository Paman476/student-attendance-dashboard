import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
from streamlit_lottie import st_lottie  # For Lottie animation

# ---------------- Page config & styling ----------------
st.set_page_config(page_title="Attendance Dashboard", page_icon="🎓", layout="wide")

# ---------------- Modern CSS Styling ----------------
st.markdown(
    """
    <style>
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .stApp {
        background: radial-gradient(circle at top left, #090d18, #0c1222, #11182b);
        color: #E6EEF3;
        animation: fadeIn 0.8s ease-in;
    }

    h1, h2, h3 {
        color: #E6EEF3;
        animation: fadeIn 1s ease-in-out;
    }

    [data-testid="stMetric"] {
        border-radius: 18px;
        padding: 16px;
        text-align: center;
        color: #fff;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 0 20px rgba(0,0,0,0.2);
        transition: all 0.4s ease;
        animation: fadeIn 1s ease-in-out;
    }

    div[data-testid="stMetric"]:nth-child(1) {
        background: linear-gradient(135deg, #ff7b00, #ffb347);
        box-shadow: 0 0 20px rgba(255,140,0,0.25);
    }
    div[data-testid="stMetric"]:nth-child(2) {
        background: linear-gradient(135deg, #00bfa6, #00e0b8);
        box-shadow: 0 0 20px rgba(0,255,200,0.25);
    }
    div[data-testid="stMetric"]:nth-child(3) {
        background: linear-gradient(135deg, #7b2ff7, #9d4edd);
        box-shadow: 0 0 20px rgba(155,0,255,0.25);
    }
    div[data-testid="stMetric"]:nth-child(4) {
        background: linear-gradient(135deg, #007bff, #33b0ff);
        box-shadow: 0 0 20px rgba(0,120,255,0.25);
    }

    [data-testid="stMetric"]:hover {
        transform: scale(1.06);
        box-shadow: 0 0 35px rgba(255,255,255,0.25);
    }

    .stButton>button {
        background-color:#ff8c42;
        color:#0f1720;
        border:none;
        border-radius:12px;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color:#ffa75c;
        box-shadow: 0 0 15px #ff8c42aa;
        transform: scale(1.05);
    }

    .stDataFrame tbody tr:hover {
        background-color: rgba(255,255,255,0.05) !important;
        transition: all 0.2s ease-in-out;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Lottie animation ----------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://lottie.host/f5bb03e5-1a48-4f0e-a03a-839423f05e72/8WBsciw1bL.json"
lottie_json = load_lottieurl(lottie_url)

st_lottie(lottie_json, speed=1, reverse=False, loop=True, quality="high", height=180, key="dashboard_anim")

# ---------------- Logo and Title ----------------
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

st.markdown("Search a student to view their **attendance percentage**.")

# ---------------- Load and clean data ----------------
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

# ---------------- Subjects ----------------
preferred_subjects = [
    "Web Technologies",
    "IT Infrastructure",
    "Data Mining",
    "Routing and Switching",
    "Modeling and Simulations"
]
available_subjects = [s for s in preferred_subjects if s in data['Subject'].unique()]
if not available_subjects:
    available_subjects = sorted(data['Subject'].unique())

# ---------------- Sidebar Controls ----------------
st.sidebar.header("Filters & Search")
student_input = st.sidebar.text_input("Search student name (exact):", "")
subject_filter = st.sidebar.selectbox("Subject filter (All subjects shown by default):", ["All"] + available_subjects)
date_min = data['Date'].min()
date_max = data['Date'].max()
date_range = st.sidebar.date_input(
    "Date range:",
    value=(date_min.date(), date_max.date()),
    min_value=date_min.date(),
    max_value=date_max.date()
)

# ---------------- Dashboard Top KPIs ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(data))
col2.metric("Students", data['Name'].nunique())
col3.metric("Subjects (in file)", data['Subject'].nunique())
col4.metric("Date Range", f"{date_min.date()} → {date_max.date()}")

st.markdown("---")

# ---------------- Data filtering ----------------
start_date, end_date = date_range
df_filtered = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]
if subject_filter != "All":
    df_filtered = df_filtered[df_filtered['Subject'] == subject_filter]

# ---------------- If a student is selected ----------------
if student_input.strip():
    student_name = student_input.strip()
    matches = [n for n in df_filtered['Name'].unique() if n.lower() == student_name.lower()]
    if not matches:
        st.error("❌ No record found for that student (check exact spelling).")
    else:
        student_name_matched = matches[0]
        sdata = df_filtered[df_filtered['Name'] == student_name_matched].sort_values('Date')
        if sdata.empty:
            st.warning("No records for this student in the selected date range / subject filter.")
        else:
            # ---------------- 📘 Aggregated Subject Attendance (bar chart) ----------------
            st.subheader("📘 Aggregated Subject Attendance (Filtered)")
            agg = sdata.groupby('Subject')['Attendance_Binary'].mean() * 100
            st.bar_chart(agg.sort_values(ascending=False))

            st.markdown("---")

            # ---------------- 🟣 Pie Chart ----------------
            st.subheader("🟣 Subject-wise Attendance Distribution")
            subject_counts = sdata.groupby('Subject')['Attendance_Binary'].sum()
            fig2, ax2 = plt.subplots(figsize=(6,6))
            ax2.pie(
                subject_counts,
                labels=subject_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=['#FF5733','#33FF57','#3357FF','#FF33A6','#FFC300'],
                textprops={'color':'white', 'fontsize':12}
            )
            ax2.axis('equal')
            st.pyplot(fig2)

            st.markdown("---")

            # ---------------- Student Summary ----------------
            total_classes = len(sdata)
            present_count = int(sdata['Attendance_Binary'].sum())
            absent_count = int(total_classes - present_count)
            attendance_pct = present_count / total_classes * 100
            avg_marks = sdata['Marks'].mean() if pd.notna(sdata['Marks']).any() else None

            st.header(f"👤 {student_name_matched} — Summary")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Classes", total_classes)
            c2.metric("Present", present_count)
            c3.metric("Absent", absent_count)
            c4.metric("Attendance %", f"{attendance_pct:.2f}%")
            if avg_marks is not None and not pd.isna(avg_marks):
                st.write(f"**Average Marks:** {avg_marks:.2f}")

            st.markdown("---")

            # ---------------- Subject-wise Summary Table ----------------
            st.subheader("📄 Subject-wise Summary")
            subj_summary = sdata.groupby('Subject').agg(
                Present=('Attendance_Binary', 'sum'),
                Total=('Attendance_Binary', 'count')
            )
            subj_summary['Attendance %'] = (subj_summary['Present'] / subj_summary['Total'] * 100).round(2)
            st.dataframe(subj_summary.sort_values('Attendance %', ascending=False))

            st.markdown("---")

            # ---------------- Download Button ----------------
            csv_bytes = sdata.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Student CSV",
                csv_bytes,
                file_name=f"{student_name_matched}_attendance.csv",
                mime="text/csv"
            )

else:
    st.info("Type a student's exact name in the sidebar search box to view their personal attendance dashboard.")
    st.subheader("📘 Aggregated Subject Attendance (Filtered)")
    agg = df_filtered.groupby('Subject')['Attendance_Binary'].mean() * 100
    st.bar_chart(agg.sort_values(ascending=False))

# ---------------- Footer ----------------
st.markdown("---")
st.caption("Dashboard built for presentation — modern dark theme, animated cards, and glowing visuals ✨")
