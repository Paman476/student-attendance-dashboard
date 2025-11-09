import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
data = pd.read_csv('attendance.csv')

# --- Clean and prepare data ---
data['Attendance'] = data['Attendance'].str.strip().str.title()
data['Attendance_Binary'] = data['Attendance'].map({'Present': 1, 'Absent': 0})

st.title("🎓 Student Attendance Pattern Dashboard")
st.write("Analyze attendance trends and student performance using data mining insights.")

# --- Overall Attendance ---
st.subheader("📊 Overall Attendance Rate")
overall = data['Attendance'].value_counts(normalize=True) * 100
st.bar_chart(overall)

# --- Attendance per Subject ---
st.subheader("📘 Subject-wise Attendance (%)")
subject_attendance = data.groupby('Subject')['Attendance_Binary'].mean() * 100
st.bar_chart(subject_attendance)

# --- Attendance per Student ---
st.subheader("🧍‍♂️ Student-wise Attendance (%)")
student_attendance = data.groupby('Name')['Attendance_Binary'].mean() * 100
st.bar_chart(student_attendance)

# --- Attendance Summary Table ---
st.subheader("📄 Attendance Summary (Present / Absent Count)")
summary = data.groupby(['Name', 'Attendance']).size().unstack(fill_value=0)
summary['Total'] = summary.sum(axis=1)
summary['Attendance %'] = (summary.get('Present', 0) / summary['Total']) * 100
st.dataframe(summary)

# --- ✅ Day-wise Attendance Summary ---
st.subheader("🗓️ Day-wise Attendance Summary")
TOTAL_CLASSES = 16  # Assume total classes per day = 16
day_summary = data.groupby(['Date', 'Attendance']).size().unstack(fill_value=0)
day_summary['Total'] = day_summary.sum(axis=1)
day_summary['Attendance_%'] = (day_summary.get('Present', 0) / TOTAL_CLASSES) * 100
day_summary['Attendance_%'] = day_summary['Attendance_%'].round(2)
st.dataframe(day_summary)

# Optional: Line chart for day-wise attendance trend
st.line_chart(day_summary['Attendance_%'])

# --- Correlation ---
st.subheader("📈 Correlation: Attendance vs Marks")
fig, ax = plt.subplots()
sns.heatmap(data[['Attendance_Binary', 'Marks']].corr(), annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# --- Individual Student Search ---
st.subheader("🔍 Check Student Details")
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

        # Attendance trend visualization
        st.line_chart(student_data.set_index('Date')['Attendance_Binary'])
    else:
        st.error("❌ No record found.")
