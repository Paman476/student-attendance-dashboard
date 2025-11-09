import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load dataset ---
data = pd.read_csv('attendance.csv')
data.columns = data.columns.str.strip()  # Clean column names
data['Attendance'] = data['Attendance'].str.strip().str.title()
data['Attendance_Binary'] = data['Attendance'].map({'Present': 1, 'Absent': 0})
data['Date'] = pd.to_datetime(data['Date'], dayfirst=True)

# --- Page Config ---
st.set_page_config(page_title="Student Attendance Dashboard", page_icon="🎓", layout="wide")

# --- Title ---
st.title("🎓 Student Attendance Dashboard")
st.markdown("Explore individual student attendance and subject-wise performance with trends and insights.")

# --- Sidebar: Select Student ---
st.sidebar.header("Student Selector")
student_list = data['Name'].unique()
selected_student = st.sidebar.selectbox("Choose a student:", student_list)

# --- Metrics for Selected Student ---
student_data = data[data['Name'] == selected_student]
total_classes = len(student_data)
present_count = student_data['Attendance_Binary'].sum()
absent_count = total_classes - present_count
attendance_percent = (present_count / total_classes) * 100
average_marks = student_data['Marks'].mean()

st.subheader(f"🧍‍♂️ {selected_student} - Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Classes", total_classes)
col2.metric("Present", present_count)
col3.metric("Absent", absent_count)
col4.metric("Attendance %", f"{attendance_percent:.2f}%")

st.metric("Average Marks", f"{average_marks:.2f}")

# --- Attendance Trend Line Chart ---
st.subheader("📈 Attendance Trend Over Time")
fig, ax = plt.subplots(figsize=(10, 3))
sns.lineplot(
    x='Date', y='Attendance_Binary', data=student_data,
    marker='o', linewidth=2, color='teal', ax=ax
)
ax.set_ylim(-0.1, 1.1)
ax.set_yticks([0, 1])
ax.set_yticklabels(["Absent", "Present"])
ax.set_xlabel("Date")
ax.set_ylabel("Attendance")
ax.set_title(f"{selected_student}'s Attendance Trend")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# --- Subject-wise Attendance ---
st.subheader("📘 Subject-wise Attendance (%)")
subject_attendance = student_data.groupby('Subject')['Attendance_Binary'].mean() * 100
fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.barplot(x=subject_attendance.index, y=subject_attendance.values, palette="coolwarm", ax=ax2)
ax2.set_ylim(0, 100)
ax2.set_ylabel("Attendance %")
ax2.set_title(f"{selected_student}'s Subject-wise Attendance")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2)

# --- Detailed Table ---
st.subheader("📄 Detailed Attendance Records")
st.dataframe(student_data.sort_values('Date').reset_index(drop=True))

# --- Download CSV ---
st.subheader("💾 Download Student Data")
csv = student_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download as CSV",
    data=csv,
    file_name=f'{selected_student}_attendance.csv',
    mime='text/csv'
)
