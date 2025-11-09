import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Student Attendance Dashboard", layout="wide")

# -------- Load Data --------
@st.cache_data
def load_data():
    df = pd.read_csv("attendance.csv")
    df['Attendance_Binary'] = df['Attendance'].apply(lambda x: 1 if x.strip().lower() == 'present' else 0)
    return df

df = load_data()

st.title("🎓 Student Attendance Dashboard")

# -------- Student Filter --------
students = df['Name'].unique()
selected_student = st.selectbox("Select a student:", students)

filtered_df = df[df['Name'] == selected_student]

# -------- Aggregated Subject Attendance (Top Section) --------
st.subheader("📘 Aggregated Subject Attendance (Filtered)")

subject_summary = (
    filtered_df.groupby('Subject')['Attendance_Binary']
    .mean()
    .reset_index()
)
subject_summary['Attendance_%'] = subject_summary['Attendance_Binary'] * 100

# Bar Chart
fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
ax_bar.bar(subject_summary['Subject'], subject_summary['Attendance_%'], color='skyblue')
ax_bar.set_ylabel('Attendance %')
ax_bar.set_ylim(0, 100)
ax_bar.set_title(f"{selected_student}'s Attendance % per Subject")
st.pyplot(fig_bar)

# -------- Combined Pie Chart (All Subjects) --------
st.subheader("🟢🔴 Overall Attendance Ratio (All Subjects Combined)")

present_count = filtered_df['Attendance_Binary'].sum()
total_count = len(filtered_df)
absent_count = total_count - present_count

fig_pie, ax_pie = plt.subplots(figsize=(4, 4))
ax_pie.pie(
    [present_count, absent_count],
    labels=[f'Present ({present_count})', f'Absent ({absent_count})'],
    autopct='%1.1f%%',
    colors=['#4CAF50', '#E74C3C'],
    startangle=90
)
ax_pie.set_title(f"{selected_student}'s Overall Attendance")
st.pyplot(fig_pie)

# -------- Raw Data (Optional) --------
with st.expander("📄 View Raw Attendance Data"):
    st.dataframe(filtered_df)
