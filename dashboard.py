import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Student Attendance Pattern Analysis", layout="wide")

st.title("🎓 Student Attendance Pattern Analysis Dashboard")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("attendance.csv")
    df['Attendance_Binary'] = df['Status'].apply(lambda x: 1 if x == 'Present' else 0)
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.header("🔍 Search Student")
student_list = sorted(df['Student_Name'].unique())
selected_student = st.sidebar.selectbox("Select a student", ["All Students"] + student_list)

st.sidebar.image(
    "https://media.licdn.com/dms/image/v2/D4D0BAQFBgbK2g1w9kw/company-logo_200_200/company-logo_200_200/0/1693174200475?e=2147483647&v=beta&t=1xcMKKhtsRau_CUs3EUsOpnGXsQe6e5qAfQbJ5GxA6g",
    width=120,
)

# --- Main Dashboard ---
if selected_student == "All Students":
    st.subheader("📘 Aggregated Subject Attendance (All Students)")
    summary = df.groupby('Subject').agg(
        Present=('Attendance_Binary', 'sum'),
        Total=('Attendance_Binary', 'count')
    )
    summary['Attendance %'] = (summary['Present'] / summary['Total'] * 100).round(2)
    st.bar_chart(summary['Attendance %'])
else:
    st.subheader(f"📋 Attendance Report for {selected_student}")

    sdata = df[df['Student_Name'] == selected_student]

    # --- Combined Pie Chart for All Subjects ---
    st.subheader("📊 Overall Attendance Percentage by Subject")

    subj_summary = sdata.groupby('Subject').agg(
        Present=('Attendance_Binary', 'sum'),
        Total=('Attendance_Binary', 'count')
    )
    subj_summary['Attendance %'] = (subj_summary['Present'] / subj_summary['Total'] * 100).round(2)

    labels = subj_summary.index.tolist()
    sizes = subj_summary['Attendance %'].tolist()

    # --- Color coding ---
    def get_color(p):
        if p >= 80:
            return 'green'
        elif p >= 60:
            return 'gold'
        else:
            return 'red'

    colors = [get_color(p) for p in sizes]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'color': 'white', 'fontsize': 11}
    )
    ax.axis('equal')
    st.pyplot(fig)

    # --- Bar Chart Below Pie Chart ---
    st.subheader("📘 Aggregated Subject Attendance (Filtered)")
    st.bar_chart(subj_summary['Attendance %'])

    # --- Data Table ---
    st.subheader("📅 Detailed Attendance Records")
    st.dataframe(sdata[['Date', 'Subject', 'Status']].reset_index(drop=True))

    # --- Overall Summary ---
    overall = (sdata['Attendance_Binary'].mean() * 100).round(2)
    st.success(f"✅ Overall Attendance Percentage: {overall}%")

