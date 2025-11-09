import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page configuration ---
st.set_page_config(page_title="Student Attendance Dashboard", layout="wide", page_icon="🎓")

# --- Load dataset ---
data = pd.read_csv('attendance.csv')

# --- Clean column names ---
data.columns = data.columns.str.strip()

# --- Clean Date column ---
data['Date'] = data['Date'].astype(str).str.strip()
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
data = data.dropna(subset=['Date'])

# --- Prepare data ---
data['Attendance'] = data['Attendance'].str.strip().str.title()
data['Attendance_Binary'] = data['Attendance'].map({'Present': 1, 'Absent': 0})

# --- Dashboard title ---
st.markdown("<h1 style='text-align: center; color: #FFA500;'>🎓 Student Attendance Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #FFFFFF;'>View individual student attendance percentages and trends per subject.</p>", unsafe_allow_html=True)

st.markdown("---")

# --- Individual Student Attendance Percentage ---
st.subheader("🧍‍♂️ Individual Student Attendance (%)")
student_attendance = data.groupby('Name')['Attendance_Binary'].mean() * 100
student_attendance = student_attendance.round(2).sort_values(ascending=False)

st.bar_chart(student_attendance, use_container_width=True)

st.markdown("---")

# --- Subject-wise Attendance ---
st.subheader("📘 Subject-wise Attendance (%)")
subject_attendance = data.groupby('Subject')['Attendance_Binary'].mean() * 100
subject_attendance = subject_attendance.round(2)

st.bar_chart(subject_attendance, use_container_width=True)

st.markdown("---")

# --- Attendance Summary Table ---
st.subheader("📄 Attendance Summary (Present / Absent Count)")
summary = data.groupby(['Name', 'Attendance']).size().unstack(fill_value=0)
summary['Total'] = summary.sum(axis=1)
summary['Attendance %'] = (summary.get('Present', 0) / summary['Total']) * 100
summary = summary.round(2)
st.dataframe(summary, use_container_width=True)

st.markdown("---")

# --- Day-wise Attendance Trend ---
st.subheader("🗓️ Day-wise Attendance Trend")
day_summary = data.groupby(['Date', 'Attendance']).size().unstack(fill_value=0)
day_summary['Total'] = day_summary.sum(axis=1)
day_summary['Attendance_%'] = (day_summary.get('Present', 0) / day_summary['Total']) * 100
day_summary['Attendance_%'] = day_summary['Attendance_%'].round(2)

st.line_chart(day_summary['Attendance_%'])

st.markdown("---")

# --- Individual Student Search & Trend ---
st.subheader("🔍 Check Individual Student Details")
name = st.text_input("Enter student name:")
if name:
    name_cap = name.strip().capitalize()
    if name_cap in data['Name'].unique():
        student_data = data[data['Name'] == name_cap]
        total = len(student_data)
        present = student_data['Attendance_Binary'].sum()
        percent = (present / total) * 100
        avg_marks = student_data['Marks'].mean()

        st.success(f"**{name_cap}** - Attendance: {percent:.2f}%, Avg Marks: {avg_marks:.2f}")

        st.subheader(f"📈 Attendance Trend for {name_cap}")
        st.line_chart(student_data.set_index('Date')['Attendance_Binary'])
    else:
        st.error("❌ No record found.")

# --- Apply custom dark theme styles ---
st.markdown(
    """
    <style>
    body {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #FFA500;
        color: white;
    }
    .stTextInput>div>input {
        background-color: #333333;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)
