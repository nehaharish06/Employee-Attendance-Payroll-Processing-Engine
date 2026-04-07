import streamlit as st
import pandas as pd
from engine import AttendanceEngine
import matplotlib.pyplot as plt

st.set_page_config(page_title="Attendance Dashboard", layout="wide")

st.title("📊 Employee Attendance & Payroll Dashboard")

emp_file = st.file_uploader("Upload Employees CSV", type=["csv"])
att_file = st.file_uploader("Upload Attendance CSV", type=["csv"])

if emp_file and att_file:
    employees = pd.read_csv(emp_file)
    attendance = pd.read_csv(att_file)

    engine = AttendanceEngine(employees, attendance)

    # Processing
    clean_data = engine.validate_data()
    summary = engine.calculate_attendance()
    payroll = engine.calculate_payroll(summary)

    payroll['loss'] = payroll['total_deduction']

    st.success("Processing Complete ✅")

    # -------------------------------
    # KPI CARDS
    # -------------------------------
    total_employees = len(employees)
    total_absents = summary['absent_days'].sum()
    total_salary_paid = payroll['final_salary'].sum()

    c1, c2, c3 = st.columns(3)

    c1.metric("👥 Total Employees", total_employees)
    c2.metric("❌ Total Absent Days", int(total_absents))
    c3.metric("💰 Total Salary Paid", f"₹ {total_salary_paid:,.2f}")

    st.divider()

    # -------------------------------
    # FIXED HEIGHT
    # -------------------------------
    CHART_HEIGHT = 350

    # -------------------------------
    # DASHBOARD
    # -------------------------------
    st.subheader("📊 Analytics Dashboard")

    display_data = payroll.copy()

    present_total = summary['present_days'].sum()
    absent_total = summary['absent_days'].sum()

    row1_col1, row1_col2 = st.columns(2)

    # 🥧 PIE CHART
    with row1_col1:
        st.write("### 🥧 Attendance")

        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie(
            [present_total, absent_total],
            labels=["Present", "Absent"],
            autopct='%1.1f%%',
            colors=["#2E86C1", "#E74C3C"]
        )

        st.pyplot(fig1, width='stretch')

    # 💸 SALARY LOSS
    with row1_col2:
        st.write("### 💸 Salary Loss")

        fig2, ax2 = plt.subplots(figsize=(6, 3.5))

        ax2.bar(
            display_data['employee_name'],
            display_data['loss'],
            color="#E74C3C"
        )

        plt.xticks(rotation=25, ha='right', fontsize=8)
        ax2.set_ylabel("₹ Loss")

        st.pyplot(fig2, width='stretch')

    # -------------------------------
    # SECOND ROW
    # -------------------------------
    row2_col1, row2_col2 = st.columns(2)

   # 💰 SALARY COMPARISON
    with row2_col1:
        st.write("### 💰 Salary Compare")

        fig3, ax3 = plt.subplots(figsize=(6, 3.5))

        x = range(len(display_data))

        ax3.bar(
            x,
            display_data['monthly_salary'],
            width=0.4,
            label="Monthly",
            color="#2E86C1"
        )

        ax3.bar(
            [i + 0.4 for i in x],
            display_data['final_salary'],
            width=0.4,
            label="Final",
            color="#27AE60"
        )

        # ✅ FIX: define ticks FIRST, then labels
        ax3.set_xticks([i + 0.2 for i in x])
        ax3.set_xticklabels(
            display_data['employee_name'],
            rotation=25,
            ha='right',
            fontsize=8
        )

        ax3.legend()

        # ✅ FIX: new Streamlit parameter
        st.pyplot(fig3, width='stretch')

    # 📋 QUICK TABLE (MATCH HEIGHT)
    with row2_col2:
        st.write("### 📋 Quick View")

        st.dataframe(
            display_data[['employee_name', 'present_days', 'absent_days', 'final_salary']],
            height=CHART_HEIGHT,
            width='stretch'
        )

    st.divider()

    # -------------------------------
    # FULL TABLES
    # -------------------------------
    st.subheader("📋 Attendance Summary")
    st.dataframe(summary, width='stretch')

    st.subheader("💰 Payroll Report")
    st.dataframe(payroll, width='stretch')

    # -------------------------------
    # DOWNLOAD BUTTONS
    # -------------------------------
    st.download_button(
        label="📥 Download Attendance Summary",
        data=summary.to_csv(index=False),
        file_name="attendance_summary.csv",
        mime="text/csv"
    )

    st.download_button(
        label="📥 Download Payroll Report",
        data=payroll.to_csv(index=False),
        file_name="payroll_report.csv",
        mime="text/csv"
    )