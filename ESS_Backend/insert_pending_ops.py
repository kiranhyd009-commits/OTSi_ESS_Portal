import random
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()
from database import SupabaseDB

def insert_ops():
    print("=== INSERTING PENDING & APPROVED OPERATIONS ===")
    
    employees = SupabaseDB.select('employees', '*')
    emp_map = {e['employee_id']: e for e in employees}
    active_emp_ids = [e['employee_id'] for e in employees if e.get('status') == 'active']
    
    managers_hr_admin = [
        e['employee_id'] for e in employees 
        if e.get('role') in ['admin', 'hr'] or e.get('designation') in ['Manager', 'Lead', 'Executive Director'] or e.get('manager_id') == 'EMP1000'
    ]
    if not managers_hr_admin:
        managers_hr_admin = ['EMP1000', 'EMP1004', 'EMP1022', 'OTSI0001', 'EMP1003', 'EMP1006']
        
    leave_types = ['casual', 'sick', 'earned', 'bereavement']
    leave_reasons = [
        "Personal family commitment",
        "Viral fever & medical rest recommended by doctor",
        "Bank & government documentation work",
        "Family function out of town",
        "Parental medical checkup and assistance",
        "Home maintenance & electrical repairs"
    ]
    
    # 1. Leave Applications (Pending & Approved)
    leave_entries = []
    
    # Pending Leaves (15)
    for _ in range(15):
        emp_id = random.choice(active_emp_ids)
        s_date = date.today() + timedelta(days=random.randint(1, 14))
        num_days = random.choice([1.0, 2.0, 3.0])
        e_date = s_date + timedelta(days=int(num_days - 1))
        
        leave_entries.append({
            'employee_id': emp_id,
            'leave_type': random.choice(leave_types),
            'start_date': s_date.isoformat(),
            'end_date': e_date.isoformat(),
            'number_of_days': num_days,
            'reason': random.choice(leave_reasons),
            'status': 'pending',
            'approved_by': None,
            'approval_date': None,
            'approval_comments': None,
            'created_at': datetime.now().isoformat()
        })
        
    # Approved Leaves (15)
    for _ in range(15):
        emp_id = random.choice(active_emp_ids)
        emp_info = emp_map.get(emp_id, {})
        approver_id = emp_info.get('manager_id') or random.choice(managers_hr_admin)
        
        s_date = date.today() - timedelta(days=random.randint(1, 20))
        num_days = random.choice([1.0, 2.0])
        e_date = s_date + timedelta(days=int(num_days - 1))
        
        approver_info = emp_map.get(approver_id, {})
        approver_name = approver_info.get('full_name', 'Manager/HR')
        
        leave_entries.append({
            'employee_id': emp_id,
            'leave_type': random.choice(leave_types),
            'start_date': s_date.isoformat(),
            'end_date': e_date.isoformat(),
            'number_of_days': num_days,
            'reason': random.choice(leave_reasons),
            'status': 'approved',
            'approved_by': approver_id,
            'approval_date': (s_date - timedelta(days=1)).isoformat() + 'T14:00:00Z',
            'approval_comments': f"Approved by {approver_name} ({approver_id}) - Leave granted.",
            'created_at': (s_date - timedelta(days=3)).isoformat() + 'T09:30:00Z'
        })
        
    inserted_leaves = 0
    for l in leave_entries:
        try:
            SupabaseDB.insert('leave_applications', l)
            inserted_leaves += 1
        except Exception as e:
            print(f"Error inserting leave: {e}")
            
    print(f"Inserted {inserted_leaves} new Leave Applications (Pending & Approved).")
    
    # 2. Attendance Correction Requests (Pending & Approved)
    corr_reasons = [
        "Forgot check-out timing due to late client call",
        "Biometric system connectivity issue at entrance",
        "WFH portal check-in failure due to ISP outage",
        "Forgot check-in timing while attending morning standup",
        "System maintenance during checkout hours"
    ]
    
    corr_entries = []
    
    # Pending Corrections (15)
    for _ in range(15):
        emp_id = random.choice(active_emp_ids)
        c_date = date.today() - timedelta(days=random.randint(1, 10))
        ci_dt = datetime(c_date.year, c_date.month, c_date.day, 3, 30) # 9:00 AM IST
        co_dt = datetime(c_date.year, c_date.month, c_date.day, 12, 30) # 6:00 PM IST
        
        corr_entries.append({
            'employee_id': emp_id,
            'attendance_date': c_date.isoformat(),
            'actual_check_in': ci_dt.isoformat(),
            'actual_check_out': co_dt.isoformat(),
            'reason': random.choice(corr_reasons),
            'status': 'pending',
            'reviewed_by': None,
            'review_date': None,
            'comments': None,
            'created_at': datetime.now().isoformat()
        })
        
    # Approved Corrections (15)
    for _ in range(15):
        emp_id = random.choice(active_emp_ids)
        emp_info = emp_map.get(emp_id, {})
        reviewer_id = emp_info.get('manager_id') or random.choice(managers_hr_admin)
        reviewer_info = emp_map.get(reviewer_id, {})
        reviewer_name = reviewer_info.get('full_name', 'Manager/HR/Admin')
        
        c_date = date.today() - timedelta(days=random.randint(5, 25))
        ci_dt = datetime(c_date.year, c_date.month, c_date.day, 3, 20)
        co_dt = datetime(c_date.year, c_date.month, c_date.day, 12, 45)
        
        corr_entries.append({
            'employee_id': emp_id,
            'attendance_date': c_date.isoformat(),
            'actual_check_in': ci_dt.isoformat(),
            'actual_check_out': co_dt.isoformat(),
            'reason': random.choice(corr_reasons),
            'status': 'approved',
            'reviewed_by': reviewer_id,
            'review_date': (c_date + timedelta(days=1)).isoformat() + 'T10:30:00Z',
            'comments': f"Correction verified & approved by {reviewer_name} ({reviewer_id}).",
            'created_at': c_date.isoformat() + 'T18:00:00Z'
        })
        
    inserted_corrs = 0
    for c in corr_entries:
        try:
            SupabaseDB.insert('attendance_correction_requests', c)
            inserted_corrs += 1
            
            # Sync attendance log for approved ones
            if c['status'] == 'approved':
                att_log = SupabaseDB.select_one('attendance_logs', {'employee_id': c['employee_id'], 'attendance_date': c['attendance_date']})
                if att_log:
                    SupabaseDB.update('attendance_logs', {'id': att_log['id']}, {
                        'check_in_time': c['actual_check_in'] + 'Z',
                        'check_out_time': c['actual_check_out'] + 'Z',
                        'working_hours': 9.42,
                        'status': 'present'
                    })
        except Exception as e:
            print(f"Error inserting correction: {e}")
            
    print(f"Inserted {inserted_corrs} new Attendance Correction Requests (Pending & Approved).")
    print("=== FINISHED INSERTING OPERATIONS ===")

if __name__ == '__main__':
    insert_ops()
