# dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

# ---------------- Page config & styling ----------------
st.set_page_config(page_title="Professional Attendance Dashboard", page_icon="🎓", layout="wide")

# Simple dark theme CSS
st.markdown(
    """
    <style>
    .css-1d391kg { background-color: #0f1720; }  /* body background in some Streamlit versions */
    .stApp { background: linear-gradient(180deg,#0b1220 0%, #0f1720 100%); color: #E6EEF3; }
    .block-container { padding: 1.2rem 1.5rem; }
    h1, h2, h3, .css-1v0mbdj { color: #E6EEF3; }
    .stMetric { color: #E6EEF3; }
    .stButton>button { background-color:#ff8c42; color: #0f1720; border: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Logo Section ----------------
logo_url = "https://media.licdn.com/dms/image/v2/D4D0BAQFBgbK2g1w9kw/company-logo_200_200/company-logo_200_200/0/1693174200475?e=2147483647&v=beta&t=1xcMKKhtsRau_CUs3EUsOpnGXsQe6e5qAfQbJ5GxA6g"

try:
    response = requests.get(logo_url, timeout=5)
    logo_img = Image.open(BytesIO(response.content))
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image(logo_img, use_column_width=True)
    with col_title:
        st.title("🎓 Professional Student Attendance Dashboard")
except Exception as e:
    st.title("🎓 Professional Student Attendance Dashboard")

st.markdown("Search a student to view their **subject-wise attendance** (green = Present, red = Absent).")

# ---------------- Load and clean data ----------------
@st.cache_data
def load_data(path='attendance.csv'):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df['Attendance'] = df['Attendance'].astype(str).str.strip().str.title()
    df['Name'] = df['Name'].astype(str).str.strip()
    df['Subject'] = df['Subject'].astype(str).str.strip()
    df['Date'] = df['Date'].astype(str).str.strip()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Attendance_Binary'] = df['Attendance'].map({'Present': 1, 'Absent': 0})
    if 'Marks' in df.columns:
        df['Marks'] = pd.to_numeric(df['Marks'], errors='coerce')
    else:
        df['Marks'] = pd.NA
    return df

data = load_data('attendance.csv')

# ---------------- Subjects (limit to 5 requested) ----------------
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
student_list = sorted(data['Name'].unique())
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
total_records = len(data)
unique_students = data['Name'].nunique()
unique_subjects = data['Subject'].nunique()
col1.metric("Total Records", total_records)
col2.metric("Students", unique_students)
col3.metric("Subjects (in file)", unique_subjects)
col4.metric("Date Range", f"{date_min.date()} → {date_max.date()}")

st.markdown("---")

# ---------------- Data filtering according to sidebar ----------------
start_date, end_date = date_range
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date)
df_filtered = data[(data['Date'] >= start_dt) & (data['Date'] <= end_dt)]

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
            # ---------------- Student summary cards ----------------
            total_classes = len(sdata)
            present_count = int(sdata['Attendance_Binary'].sum())
            absent_count = int(total_classes - present_count)
            attendance_pct = present_count / total_classes * 100
            avg_marks = sdata['Marks'].mean() if pd.notna(sdata['Marks']).any() else None

            st.header(f"👤 {student_name_matched} — Summary")
            c1, c2, c3, c4 = st.columns([1,1,1,1])
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

            # ---------------- Color-coded Attendance Plot ----------------
            st.subheader("📊 Subject-wise Attendance over Time (Green = Present, Red = Absent)")
            subjects_for_student = sorted(sdata['Subject'].unique())
            y_positions = {subj: idx for idx, subj in enumerate(subjects_for_student)}

            fig, ax = plt.subplots(figsize=(12, 3 + 0.6*len(subjects_for_student)))
            for subj in subjects_for_student:
                subj_df = sdata[sdata['Subject'] == subj].sort_values('Date')
                dates = subj_df['Date']
                vals = subj_df['Attendance_Binary']
                colors = ['green' if v==1 else 'red' for v in vals]
                y = [y_positions[subj]] * len(dates)
                ax.scatter(dates, y, c=colors, s=140, edgecolors='k')
                ax.text(dates.min() - pd.Timedelta(days=0.6), y_positions[subj], subj, va='center', ha='right', color='#E6EEF3', fontsize=10)

            ax.set_yticks(list(y_positions.values()))
            ax.set_yticklabels([])
            ax.set_ylim(-1, len(subjects_for_student))
            ax.set_xlabel("Date")
            ax.set_title(f"{student_name_matched} — Attendance by Subject & Date", color='#E6EEF3')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            st.markdown("---")

            # ---------------- Attendance Trend Line Chart ----------------
            st.subheader("📈 Attendance Trend (per Subject)")
            pivot = sdata.pivot(index='Date', columns='Subject', values='Attendance_Binary').fillna(0)
            st.line_chart(pivot)

            st.markdown("---")

            # ---------------- Download Button ----------------
            csv_bytes = sdata.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Student CSV", csv_bytes, file_name=f"{student_name_matched}_attendance.csv", mime="text/csv")

else:
    # ---------------- No student selected ----------------
    st.info("Type a student's exact name in the sidebar search box to view their personal attendance dashboard.")
    st.subheader("📘 Aggregated Subject Attendance (filtered)")
    agg = df_filtered.groupby('Subject')['Attendance_Binary'].mean() * 100
    st.bar_chart(agg.sort_values(ascending=False))

# ---------------- Footer ----------------
st.markdown("---")
st.caption("Dashboard built for presentation — modern dark theme, subject-wise student view with university logo.")
