import pandas as pd

class AttendanceEngine:

    def __init__(self, employees, attendance):
        # Work on copies to avoid modifying original data
        self.employees = employees.copy()
        self.attendance = attendance.copy()

    # -------------------------------
    # STEP 1: VALIDATION
    # -------------------------------
    def validate_data(self):
        # Ensure required columns exist
        required_emp_cols = {'employee_id', 'employee_name', 'monthly_salary'}
        required_att_cols = {'employee_id', 'date', 'status'}

        if not required_emp_cols.issubset(self.employees.columns):
            raise ValueError("Employees file missing required columns")

        if not required_att_cols.issubset(self.attendance.columns):
            raise ValueError("Attendance file missing required columns")

        # Filter valid employee IDs
        valid_ids = set(self.employees['employee_id'])

        self.attendance = self.attendance[
            self.attendance['employee_id'].isin(valid_ids)
        ].copy()

        # Convert date safely
        self.attendance['date'] = pd.to_datetime(
            self.attendance['date'], errors='coerce'
        )

        # Drop invalid dates
        self.attendance = self.attendance.dropna(subset=['date'])

        # Normalize status (important for consistency)
        self.attendance['status'] = self.attendance['status'].str.upper().str.strip()

        # Keep only valid status values
        self.attendance = self.attendance[
            self.attendance['status'].isin(['P', 'A'])
        ]

        return self.attendance

    # -------------------------------
    # STEP 2: ATTENDANCE COUNT
    # -------------------------------
    def calculate_attendance(self):
        summary = (
            self.attendance
            .groupby(['employee_id', 'status'])
            .size()
            .unstack(fill_value=0)
        )

        # Rename columns safely
        summary = summary.rename(columns={
            'P': 'present_days',
            'A': 'absent_days'
        })

        # Ensure both columns exist
        for col in ['present_days', 'absent_days']:
            if col not in summary:
                summary[col] = 0

        summary = summary.reset_index()

        return summary

    # -------------------------------
    # STEP 3: PAYROLL CALCULATION
    # -------------------------------
    def calculate_payroll(self, summary):
        df = pd.merge(
            self.employees,
            summary,
            on='employee_id',
            how='left'
        )

        # Fill missing attendance with 0
        df['present_days'] = df['present_days'].fillna(0)
        df['absent_days'] = df['absent_days'].fillna(0)

        # Convert to int (clean output)
        df['present_days'] = df['present_days'].astype(int)
        df['absent_days'] = df['absent_days'].astype(int)

        # Deduction per day
        df['deduction_per_day'] = df['monthly_salary'] / 30

        # Total deduction
        df['total_deduction'] = df['absent_days'] * df['deduction_per_day']

        # Final salary (never negative safeguard)
        df['final_salary'] = (df['monthly_salary'] - df['total_deduction']).clip(lower=0)

        # Round values for clean UI
        df['deduction_per_day'] = df['deduction_per_day'].round(2)
        df['total_deduction'] = df['total_deduction'].round(2)
        df['final_salary'] = df['final_salary'].round(2)

        return df