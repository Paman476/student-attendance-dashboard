import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load dataset ---
data = pd.read_csv('attendance.csv')

# --- Clean columns ---
data.columns = data.columns.str.strip()
data['Attendance'] = data['Attendance'].str.strip().str.title()
data['Attendance_Binary'] = data['Attendance'].map({'Present': 1, 'Absent': 0})
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)

# --- Page Title ---
st.title("🎓 Student Attendance Tracker")
st.write("Search for a student and see their subject-wise attendance chart.")

# --- Sidebar: Student Selection ---
student_name = st.text_input("Enter Student Name:")

if student_name:
    student_name_cap = student_name.strip().capitalize()
    if student_name_cap in data['Name'].unique():
        student_data = data[data['Name'] == student_name_cap].copy()
        student_data = student_data.sort_values('Date')

        # --- Attendance Overview ---
        total_days = len(student_data)
        present_days = student_data['Attendance_Binary'].sum()
        attendance_percent = (present_days / total_days) * 100
        st.subheader(f"{student_name_cap} Attendance Overview")
        st.metric("Overall Attendance %", f"{attendance_percent:.2f}%")

        # --- Subject-wise Attendance Table ---
        st.subheader("📄 Subject-wise Attendance Summary")
        subject_summary = student_data.groupby('Subject')['Attendance_Binary'].agg(['sum', 'count'])
        subject_summary['Attendance %'] = (subject_summary['sum'] / subject_summary['count'] * 100).round(2)
        st.dataframe(subject_summary[['sum', 'count', 'Attendance %']].rename(columns={'sum':'Present', 'count':'Total'}))

        # --- Color-coded Attendance Chart by Subject ---
        st.subheader("📊 Attendance Chart by Subject")
        subjects = student_data['Subject'].unique()
        fig, ax = plt.subplots(figsize=(12, 5))

        for subj in subjects:
            subj_data = student_data[student_data['Subject'] == subj]
            colors = ['green' if x == 'Present' else 'red' for x in subj_data['Attendance']]
            ax.bar(subj_data['Date'], subj_data['Attendance_Binary'], color=colors, label=subj, alpha=0.7)

        ax.set_ylim(0, 1.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Absent', 'Present'])
        ax.set_xlabel("Date")
        ax.set_ylabel("Attendance")
        ax.set_title(f"{student_name_cap} Subject-wise Attendance")
        ax.legend(title="Subject")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    else:
        st.error("❌ No record found for this student.")
