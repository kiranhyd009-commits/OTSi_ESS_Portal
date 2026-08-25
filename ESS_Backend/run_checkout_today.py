import sys
import os
import random
from datetime import datetime, date, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from database import SupabaseDB

# TARGET_DATE defaults to None (dynamically resolves to today's date).
# You can set it here or pass via CLI:
#   python run_checkout_today.py              -> runs for today
#   python run_checkout_today.py yesterday    -> runs for yesterday
#   python run_checkout_today.py 2026-08-17   -> runs for specific past date
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
    today_str = target_date.isoformat()
    is_today = (target_date == date.today())
    
    print(f"=== Starting Check-out Simulation for {today_str} ===")
    
    # 1. Get all logs for the target date
    logs = SupabaseDB.select('attendance_logs', '*', {'attendance_date': today_str})
    
    # 2. Filter for those with check-in but no check-out
    pending_checkouts = [log for log in logs if log.get('check_in_time') and not log.get('check_out_time')]
    print(f'Found {len(pending_checkouts)} employees checked-in without check-out.')
    
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC for comparison
    
    updated_count = 0
    skipped_count = 0
    for log in pending_checkouts:
        log_id = log['id']
        check_in_str = log['check_in_time'].replace('Z', '')
        
        try:
            check_in_dt = datetime.fromisoformat(check_in_str.split('+')[0].split('.')[0])
        except ValueError:
            check_in_dt = datetime.strptime(check_in_str.split('+')[0].split('.')[0], "%Y-%m-%dT%H:%M:%S")
            
        # Random checkout time: 8.5 to 9.5 hours after check_in
        co_hours_add = random.choice([8, 9])
        co_minutes_add = random.randint(10, 50)
        check_out_dt = check_in_dt + timedelta(hours=co_hours_add, minutes=co_minutes_add)
        
        # Only cap checkout if simulating for today and time would be in the future
        if is_today and check_out_dt > now_utc:
            print(f"  Skipping {log['employee_id']}: calculated checkout {check_out_dt.isoformat()}Z is in the future.")
            skipped_count += 1
            continue
        
        # Calculate working hours
        delta = check_out_dt - check_in_dt
        working_hours = round(delta.total_seconds() / 3600.0, 2)
        
        update_data = {
            'check_out_time': check_out_dt.isoformat() + 'Z',
            'working_hours': working_hours
        }
        
        SupabaseDB.update('attendance_logs', {'id': log_id}, update_data)
        updated_count += 1
        
    print(f'Successfully checked out {updated_count} employees.')
    if skipped_count > 0:
        print(f'Skipped {skipped_count} employees (checkout would be in the future — run again later).')
    print("=== Finished Check-out Simulation ===")

if __name__ == '__main__':
    main()
