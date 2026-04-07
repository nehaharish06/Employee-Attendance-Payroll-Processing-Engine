import unittest
import pandas as pd
from engine import AttendanceEngine


class TestAttendanceEngine(unittest.TestCase):

    def setUp(self):
        # Sample Employees Data
        self.employees = pd.DataFrame({
            'employee_id': [1, 2],
            'employee_name': ['Alice', 'Bob'],
            'monthly_salary': [3000, 3000]
        })

        # Sample Attendance Data
        self.attendance = pd.DataFrame({
            'employee_id': [1, 1, 2, 3],  # 3 is invalid employee
            'date': ['2026-04-01', 'invalid_date', '2026-04-01', '2026-04-01'],
            'status': ['P', 'A', 'A', 'P']
        })

        self.engine = AttendanceEngine(self.employees, self.attendance)

    # -----------------------------------
    # TEST 1: Invalid employee removed
    # -----------------------------------
    def test_invalid_employee_rejected(self):
        validated = self.engine.validate_data()

        # Employee ID 3 should be removed
        self.assertNotIn(3, validated['employee_id'].values)

    # -----------------------------------
    # TEST 2: Invalid date ignored
    # -----------------------------------
    def test_invalid_date_ignored(self):
        validated = self.engine.validate_data()

        # Ensure no NaT values in date column
        self.assertFalse(validated['date'].isnull().any())

    # -----------------------------------
    # TEST 3: Attendance count correct
    # -----------------------------------
    def test_attendance_count(self):
        validated = self.engine.validate_data()
        summary = self.engine.calculate_attendance()

        emp1 = summary[summary['employee_id'] == 1]

        # Only one valid record (invalid date removed)
        self.assertEqual(int(emp1['present_days'].iloc[0]), 1)
        self.assertEqual(int(emp1['absent_days'].iloc[0]), 0)

    # -----------------------------------
    # TEST 4: Salary deduction
    # -----------------------------------
    def test_salary_deduction(self):
        validated = self.engine.validate_data()
        summary = self.engine.calculate_attendance()
        payroll = self.engine.calculate_payroll(summary)

        emp2 = payroll[payroll['employee_id'] == 2]

        # 1 absent day → deduction = 3000 / 30 = 100
        self.assertEqual(float(emp2['deduction_per_day'].iloc[0]), 100.00)
        self.assertEqual(float(emp2['total_deduction'].iloc[0]), 100.00)

    # -----------------------------------
    # TEST 5: Final salary calculation
    # -----------------------------------
    def test_final_salary_calculation(self):
        validated = self.engine.validate_data()
        summary = self.engine.calculate_attendance()
        payroll = self.engine.calculate_payroll(summary)

        emp2 = payroll[payroll['employee_id'] == 2]

        # Final salary = 3000 - 100 = 2900
        self.assertEqual(float(emp2['final_salary'].iloc[0]), 2900.00)


if __name__ == '__main__':
    unittest.main()