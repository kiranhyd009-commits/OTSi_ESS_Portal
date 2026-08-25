import os
import random
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()
from database import SupabaseDB

def get_random_checkin_checkout(att_date):
    # Check-in between 08:30 IST (03:00 UTC) and 10:00 IST (04:30 UTC)
    ci_hour = random.choice([3, 4])
    ci_minute = random.randint(0, 59) if ci_hour == 3 else random.randint(0, 30)
    check_in_dt = datetime(att_date.year, att_date.month, att_date.day, ci_hour, ci_minute)
    
    # Work duration: 8.5 to 9.5 hours
    work_mins = random.randint(510, 570)
    check_out_dt = check_in_dt + timedelta(minutes=work_mins)
    
    working_hours = round(work_mins / 60.0, 2)
    is_late = (ci_hour == 4 and ci_minute > 0)
    is_wfh = random.random() < 0.20
    status = 'wfh' if is_wfh else ('late' if is_late else 'present')
    loc = 'WFH' if is_wfh else random.choice(['OTSi Office', 'Client Site'])
    
    return {
        'check_in_time': check_in_dt.isoformat() + 'Z',
        'check_out_time': check_out_dt.isoformat() + 'Z',
        'working_hours': working_hours,
        'status': status,
        'is_late': is_late,
        'is_wfh': is_wfh,
        'check_in_location': loc,
        'location_verified': True
    }

def run_population():
    print("=== STARTING DUMMY DATA POPULATION ===")
    
    # 1. Get employees
    employees = SupabaseDB.select('employees', '*')
    print(f"Loaded {len(employees)} employees.")
    
    emp_map = {e['employee_id']: e for e in employees}
    active_emp_ids = [e['employee_id'] for e in employees if e.get('status') == 'active']
    
    managers = [e['employee_id'] for e in employees if e.get('role') in ['admin', 'hr'] or e.get('designation') in ['Manager', 'Lead', 'Executive Director']]
    if not managers:
        managers = ['EMP1000', 'EMP1004', 'OTSI0001', 'EMP1022']
    
    # 2. Update existing attendance logs missing check_in or check_out
    print("\n--- Updating Existing Incomplete Attendance Logs ---")
    logs = SupabaseDB.select('attendance_logs', '*')
    updated_logs_count = 0
    
    for log in logs:
        if not log.get('check_in_time') or not log.get('check_out_time') or log.get('status') == 'absent':
            try:
                dt_parts = [int(x) for x in log['attendance_date'].split('-')]
                att_date = date(dt_parts[0], dt_parts[1], dt_parts[2])
            except Exception:
                continue
                
            if att_date <= date.today():
                timing = get_random_checkin_checkout(att_date)
                SupabaseDB.update('attendance_logs', {'id': log['id']}, timing)
                updated_logs_count += 1
                
    print(f"Updated {updated_logs_count} existing attendance logs with check-in and check-out times.")
    
    # Re-fetch existing logs to get up-to-date set of (employee_id, attendance_date)
    all_logs = SupabaseDB.select('attendance_logs', 'employee_id, attendance_date')
    existing_set = {(l['employee_id'], l['attendance_date']) for l in all_logs}
    
    # 3. Generate attendance logs for recent dates (July 1 to Aug 17, 2026) for active employees missing logs
    print("\n--- Generating Missing Attendance Logs for July-Aug 2026 ---")
    start_dt = date(2026, 7, 1)
    end_dt = date(2026, 8, 17)
    
    new_att_batch = []
    curr = start_dt
    while curr <= end_dt:
        if curr.weekday() < 5: # Monday to Friday
            date_str = curr.isoformat()
            for emp_id in active_emp_ids:
                if (emp_id, date_str) not in existing_set:
                    # 90% present rate
                    if random.random() < 0.90:
                        timing = get_random_checkin_checkout(curr)
                        new_att_batch.append({
                            'employee_id': emp_id,
                            'attendance_date': date_str,
                            'check_in_time': timing['check_in_time'],
                            'check_out_time': timing['check_out_time'],
                            'working_hours': timing['working_hours'],
                            'status': timing['status'],
                            'is_late': timing['is_late'],
                            'is_wfh': timing['is_wfh'],
                            'check_in_location': timing['check_in_location'],
                            'location_verified': True
                        })
                        existing_set.add((emp_id, date_str))
        curr += timedelta(days=1)
        
    print(f"Prepared {len(new_att_batch)} new attendance log entries.")
    if new_att_batch:
        chunk_size = 50
        inserted_count = 0
        for i in range(0, len(new_att_batch), chunk_size):
            chunk = new_att_batch[i:i+chunk_size]
            try:
                SupabaseDB.insert_many('attendance_logs', chunk)
                inserted_count += len(chunk)
            except Exception as e:
                # If batch insert hits any constraint, insert one by one
                for item in chunk:
                    try:
                        SupabaseDB.insert('attendance_logs', item)
                        inserted_count += 1
                    except Exception:
                        pass
        print(f"Successfully inserted {inserted_count} new attendance logs.")

    # 4. Insert dummy Leave Applications (Pending, Approved, Rejected by Manager/HR/Admin)
    print("\n--- Inserting Leave Applications ---")
    leave_types = ['casual', 'sick', 'earned', 'bereavement']
    reasons = [
        "Family function & travel to hometown",
        "Feeling unwell with fever and headache",
        "Personal emergency work at bank/govt office",
        "Medical checkup for parents",
        "Attending urgent personal matter",
        "Scheduled home maintenance & repair"
    ]
    
    new_leaves = []
    # Create 35 leave applications
    for i in range(35):
        emp_id = random.choice(active_emp_ids)
        emp_info = emp_map.get(emp_id, {})
        mgr_id = emp_info.get('manager_id') or random.choice(['EMP1000', 'EMP1004', 'EMP1022', 'OTSI0001'])
        
        offset_days = random.randint(-30, 10)
        s_date = date.today() + timedelta(days=offset_days)
        num_days = random.choice([1.0, 2.0, 3.0])
        e_date = s_date + timedelta(days=int(num_days - 1))
        
        st_choice = random.choices(['pending', 'approved', 'rejected'], weights=[35, 50, 15], k=1)[0]
        
        leave_entry = {
            'employee_id': emp_id,
            'leave_type': random.choice(leave_types),
            'start_date': s_date.isoformat(),
            'end_date': e_date.isoformat(),
            'number_of_days': num_days,
            'reason': random.choice(reasons),
            'status': st_choice,
            'created_at': (s_date - timedelta(days=random.randint(2, 5))).isoformat() + 'T09:00:00Z',
            'updated_at': datetime.now().isoformat()
        }
        
        if st_choice in ['approved', 'rejected']:
            leave_entry['approved_by'] = mgr_id
            leave_entry['approval_date'] = (s_date - timedelta(days=1)).isoformat() + 'T14:30:00Z'
            leave_entry['approval_comments'] = f"{'Approved' if st_choice=='approved' else 'Rejected'} by manager ({mgr_id})."
        else:
            leave_entry['approved_by'] = None
            leave_entry['approval_date'] = None
            leave_entry['approval_comments'] = None
            
        new_leaves.append(leave_entry)

    if new_leaves:
        try:
            inserted_leaves = SupabaseDB.insert_many('leave_applications', new_leaves)
            print(f"Successfully inserted {len(inserted_leaves)} leave applications.")
        except Exception:
            count = 0
            for l in new_leaves:
                try:
                    SupabaseDB.insert('leave_applications', l)
                    count += 1
                except Exception:
                    pass
            print(f"Successfully inserted {count} leave applications.")

    # 5. Insert Attendance Corrections (Pending, Approved, Rejected)
    print("\n--- Inserting Attendance Correction Requests ---")
    corr_reasons = [
        "Forgot to check in/out due to morning rush meeting",
        "Biometric device glitch at reception",
        "System check-out timeout error while working late",
        "WFH connection issue prevented timely checkout",
        "Client site arrival punch failed due to network outage"
    ]
    
    new_corrections = []
    for i in range(25):
        emp_id = random.choice(active_emp_ids)
        emp_info = emp_map.get(emp_id, {})
        mgr_id = emp_info.get('manager_id') or random.choice(['EMP1000', 'EMP1004', 'EMP1022', 'OTSI0001'])
        
        c_date = date.today() - timedelta(days=random.randint(1, 30))
        c_date_str = c_date.isoformat()
        
        ci_dt = datetime(c_date.year, c_date.month, c_date.day, 3, 30) # 9:00 AM IST
        co_dt = datetime(c_date.year, c_date.month, c_date.day, 12, 30) # 6:00 PM IST
        
        st_choice = random.choices(['pending', 'approved', 'rejected'], weights=[40, 45, 15], k=1)[0]
        
        corr_entry = {
            'employee_id': emp_id,
            'attendance_date': c_date_str,
            'actual_check_in': ci_dt.isoformat(),
            'actual_check_out': co_dt.isoformat(),
            'reason': random.choice(corr_reasons),
            'status': st_choice,
            'created_at': (c_date + timedelta(days=1)).isoformat() + 'T10:15:00Z',
            'updated_at': datetime.now().isoformat()
        }
        
        if st_choice in ['approved', 'rejected']:
            corr_entry['reviewed_by'] = mgr_id
            corr_entry['review_date'] = (c_date + timedelta(days=2)).isoformat() + 'T11:00:00Z'
            corr_entry['comments'] = f"Regularization {'approved' if st_choice=='approved' else 'rejected'} by manager ({mgr_id})."
            
            if st_choice == 'approved':
                att_log = SupabaseDB.select_one('attendance_logs', {'employee_id': emp_id, 'attendance_date': c_date_str})
                if att_log:
                    SupabaseDB.update('attendance_logs', {'id': att_log['id']}, {
                        'check_in_time': ci_dt.isoformat() + 'Z',
                        'check_out_time': co_dt.isoformat() + 'Z',
                        'working_hours': 9.0,
                        'status': 'present'
                    })
                else:
                    try:
                        SupabaseDB.insert('attendance_logs', {
                            'employee_id': emp_id,
                            'attendance_date': c_date_str,
                            'check_in_time': ci_dt.isoformat() + 'Z',
                            'check_out_time': co_dt.isoformat() + 'Z',
                            'working_hours': 9.0,
                            'status': 'present',
                            'location_verified': True
                        })
                    except Exception:
                        pass
        else:
            corr_entry['reviewed_by'] = None
            corr_entry['review_date'] = None
            corr_entry['comments'] = None
            
        new_corrections.append(corr_entry)

    if new_corrections:
        count = 0
        for c in new_corrections:
            try:
                SupabaseDB.insert('attendance_correction_requests', c)
                count += 1
            except Exception:
                pass
        print(f"Successfully inserted {count} attendance correction requests.")

    print("\n=== FINISHED DUMMY DATA POPULATION ===")

if __name__ == '__main__':
    run_population()
