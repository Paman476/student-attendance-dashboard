# ---------------- Subject-wise Attendance % Plot ----------------
st.subheader("📊 Subject-wise Attendance % Over Time")

subjects_for_student = sorted(sdata['Subject'].unique())
y_positions = {subj: idx for idx, subj in enumerate(subjects_for_student)}

fig, ax = plt.subplots(figsize=(12, 3 + 0.6*len(subjects_for_student)))

for subj in subjects_for_student:
    subj_df = sdata[sdata['Subject'] == subj].sort_values('Date')
    dates = subj_df['Date']
    
    # Compute cumulative attendance % up to each date
    cumulative_present = subj_df['Attendance_Binary'].cumsum()
    total_classes = range(1, len(subj_df)+1)
    attendance_pct = cumulative_present / total_classes * 100
    
    y = [y_positions[subj]] * len(dates)
    
    # Color: green if >=50%, red if <50%
    colors = ['green' if val >= 50 else 'red' for val in attendance_pct]
    
    # Plot markers
    ax.scatter(dates, y, c=colors, s=200, edgecolors='k', alpha=0.9)
    
    # Annotate cumulative % above each marker
    for d, p, yy in zip(dates, attendance_pct, y):
        ax.text(d, yy + 0.1, f"{p:.0f}%", color='#E6EEF3', fontsize=8, ha='center', va='bottom')

    # Subject label on the left
    ax.text(dates.min() - pd.Timedelta(days=0.6), y_positions[subj], subj,
            va='center', ha='right', color='#E6EEF3', fontsize=10, fontweight='bold')

# Formatting
ax.set_yticks(list(y_positions.values()))
ax.set_yticklabels([])
ax.set_ylim(-1, len(subjects_for_student))
ax.set_xlabel("Date")
ax.set_title(f"{student_name_matched} — Cumulative Attendance % by Subject", color='#E6EEF3', fontsize=14)
ax.grid(True, linestyle='--', alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
