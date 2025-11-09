import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Title
st.title("📊 Student Attendance Dashboard")

# Load data
df = pd.read_csv("attendance.csv")

# Show raw data
st.subheader("Attendance Data")
st.dataframe(df)

# Summary by student
st.subheader("📋 Attendance Summary")
summary = df.groupby(['Name', 'Status']).size().unstack(fill_value=0)
summary['Total'] = summary.sum(axis=1)
summary['Attendance %'] = (summary.get('Present', 0) / summary['Total']) * 100
st.dataframe(summary)

# Select student
st.subheader("👩‍🎓 Individual Student Analysis")
students = df['Name'].unique()
selected_student = st.selectbox("Select Student:", students)

student_data = df[df['Name'] == selected_student]
st.write(f"### {selected_student}'s Attendance Details")
st.write(student_data)

# Count present/absent
present_count = (student_data['Status'] == 'Present').sum()
absent_count = (student_data['Status'] == 'Absent').sum()

st.metric("Total Presents", present_count)
st.metric("Total Absents", absent_count)

# Pie Chart
fig, ax = plt.subplots()
ax.pie(
    [present_count, absent_count],
    labels=['Present', 'Absent'],
    autopct='%1.1f%%',
    colors=['#4CAF50', '#FF5252']
)
st.pyplot(fig)

# Overall Heatmap
st.subheader("📅 Overall Attendance Heatmap")
pivot_table = df.pivot_table(index='Name', columns='Date', values='Status', aggfunc=lambda x: 1 if 'Present' in x.values else 0)
sns.heatmap(pivot_table, cmap='Greens', cbar=True)
st.pyplot()
