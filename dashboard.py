import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Load dataset ---
data = pd.read_csv('attendance.csv')

# --- Clean column names ---
data.columns = data.columns.str.strip()

# --- Clean and prepare data ---
data['Attendance'] = data['Attendance'].str.strip().str.title()
data['Attendance_Binary'] = data['Attendance'].map({'Present': 1, 'Absent': 0})

# --- Fix invalid dates safely ---
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
data = data.dropna(subset=['Date'])

# --- Dashboard Header ---
st.set_page_config(page_title="Student Attendance Dashboard", layout="wide")
st.title("🎓 Student Attendance Dashboard")
st.markdown("""
This dashboard helps visualize **individual student attendance** across all subjects.  
You can search for a student below to view their detailed attendance trend.
""")

# --- Student Search Input ---
st.sidebar.header("🔍 Search Student")
name = st.sidebar.text_input("Enter student name:")

if name:
    name_cap = name.strip().capitalize()
    if name_cap in data['Name'].unique():
        student_data = data[data['Name'] == name_cap]
        total = len(student_data)
        present = student_data['Attendance_Binary'].sum()
        percent = (present / total) * 100
        avg_marks = student_data['Marks'].mean()

        st.success(f"### ✅ {name_cap}'s Attendance Summary")
        st.write(f"**Total Classes:** {total}")
        st.write(f"**Present:** {present}")
        st.write(f"**Absent:** {total - present}")
        st.write(f"**Attendance %:** {percent:.2f}%")
        st.write(f"**Average Marks:** {avg_marks:.2f}")

        # --- Subject-wise Attendance ---
        st.subheader("📘 Subject-wise Attendance (%)")
        subject_attendance = student_data.groupby('Subject')['Attendance_Binary'].mean() * 100
        st.bar_chart(subject_attendance)

        # --- Daily Attendance Visualization (Colored Chart) ---
        st.subheader("📅 Daily Attendance Record")
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = student_data['Attendance_Binary'].map({1: 'green', 0: 'red'})
        ax.bar(student_data['Date'], student_data['Attendance_Binary'], color=colors)
        ax.set_title(f"{name_cap}'s Attendance (Green = Present, Red = Absent)", fontsize=14)
        ax.set_xlabel("Date")
        ax.set_ylabel("Attendance (1=Present, 0=Absent)")
        ax.set_ylim(0, 1.2)
        plt.xticks(rotation=45)
        st.pyplot(fig)

    else:
        st.error("❌ No record found for this student.")
else:
    st.info("👈 Please enter a student name in the sidebar to view their details.")

# --- Footer ---
st.markdown("""
---
👨‍🏫 *Developed Interactive Attendance Dashboard*
""")
