import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load dataset ---
data = pd.read_csv('attendance.csv')

# --- Clean column names to avoid KeyError ---
data.columns = data.columns.str.strip()  # Remove any extra spaces

# --- Clean and prepare data ---
data['Attendance'] = data['Attendance'].str.strip().str.title()
data['Attendance_Binary'] = data['Attendance'].map({'Present': 1, 'Absent': 0})

st.title("🎓 Student Attendance Dashboard")
st.write("View individual student attendance percentages and trends.")

# --- Individual Student Attendance Percentage ---
st.subheader("🧍‍♂️ Individual Student Attendance (%)")
student_attendance = data.groupby('Name')['Attendance_Binary'].mean() * 100
student_attendance = student_attendance.round(2)
student_attendance = student_attendance.sort_values(ascending=False)

# Show bar chart with student names
st.bar_chart(student_attendance)

# --- Individual Student Search & Trend ---
st.subheader("🔍 Check Student Details")
name = st.text_input("Enter student name:")
if name:
    name_cap = name.strip().capitalize()
    if name_cap in data['Name'].unique():
        student_data = data[data['Name'] == name_cap]
        total = len(student_data)
        present = student_data['Attendance_Percentage'].sum()
        percent = (present / total) * 100
        avg_marks = student_data['Marks'].mean()

        st.success(f"**{name_cap}** - Attendance: {percent:.2f}%, Avg Marks: {avg_marks:.2f}")

        # Attendance trend visualization for selected student
        st.subheader(f"📈 Attendance Trend for {name_cap}")
        st.line_chart(student_data.set_index('Date')['Attendance_Percentage'])
    else:
        st.error("❌ No record found.")
