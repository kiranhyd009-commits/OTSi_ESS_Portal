import sys
import os
import random
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

from database import SupabaseDB

# TARGET_DATE defaults to None (dynamically resolves to today's date).
# You can set it here or pass via CLI:
#   python run_checkin_today.py              -> runs for today
#   python run_checkin_today.py yesterday    -> runs for yesterday
#   python run_checkin_today.py 2026-08-17   -> runs for specific past date
TARGET_DATE = None

def parse_and_validate_date(input_val):
    today = date.today()
    if not input_val:
        return today
        
    s = str(input_val).strip().lower()
    if s in ('today', 'none'):
        resolved = today
    elif s == 'yesterday':
        resolved = today - timedelta(days=1)
    elif s.startswith('-') and s[1:].isdigit():
        resolved = today - timedelta(days=int(s[1:]))
    else:
        try:
            resolved = datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Error: Invalid date format '{input_val}'. Please use YYYY-MM-DD, 'yesterday', or 'today'.")
            sys.exit(1)
            
    # Disallow future dates
    if resolved > today:
        print(f"❌ Error: Future date '{resolved}' is not allowed! Please specify today ({today}) or a past date.")
        sys.exit(1)
        
    return resolved

def main():
    cli_date = sys.argv[1] if len(sys.argv) > 1 else None
    raw_date = cli_date or globals().get('TARGET_DATE')
    
    target_date = parse_and_validate_date(raw_date)
    today = target_date.isoformat()
    print(f"=== Starting Check-in Simulation for {today} ===")
    
    # 1. Get active employees
    employees = SupabaseDB.select('employees', 'employee_id, status')
    active_employees = [e for e in employees if e.get('status') == 'active']
    print(f'Found {len(active_employees)} active employees in system.')
    
    # 2. Check who already has an attendance log for today
    existing_logs = SupabaseDB.select('attendance_logs', 'employee_id', {'attendance_date': today})
    existing_emp_ids = {log['employee_id'] for log in existing_logs}
    
    # 3. Create check-in entries
    attendance_batch = []
    locations = ['OTSi Office', 'Client Site', 'WFH']
    
    for emp in active_employees:
        emp_id = emp['employee_id']
        
        if emp_id in existing_emp_ids:
            continue
            
        # Simulating a 90% attendance rate
        if random.random() < 0.90:
            loc = random.choices(locations, weights=[70, 15, 15], k=1)[0]
            is_wfh = (loc == 'WFH')
            
            # Check-in time: morning check-in (between 03:00 UTC/08:30 IST and 04:30 UTC/10:00 IST)
            ci_hour = random.choice([3, 4])
            if ci_hour == 3:
                ci_minute = random.randint(0, 59)
            else:
                ci_minute = random.randint(0, 30) # up to 10:00 AM IST
            
            check_in_dt = datetime(target_date.year, target_date.month, target_date.day, ci_hour, ci_minute)
            is_late = (ci_hour == 4 and ci_minute > 0)
            
            status = 'wfh' if is_wfh else ('late' if is_late else 'present')
            
            attendance_batch.append({
                'employee_id': emp_id,
                'attendance_date': today,
                'check_in_time': check_in_dt.isoformat() + 'Z',
                'check_out_time': None,
                'check_in_location': loc,
                'is_wfh': is_wfh,
                'working_hours': 0.0,
                'status': status,
                'is_late': is_late,
                'location_verified': True
            })
            
    if attendance_batch:
        chunk_size = 50
        for i in range(0, len(attendance_batch), chunk_size):
            chunk = attendance_batch[i:i + chunk_size]
            SupabaseDB.insert_many('attendance_logs', chunk)
        print(f'Successfully checked in {len(attendance_batch)} employees.')
    else:
        print('All employees are already checked in for today or no new check-ins generated.')
    print("=== Finished Check-in Simulation ===")

if __name__ == '__main__':
    main()
