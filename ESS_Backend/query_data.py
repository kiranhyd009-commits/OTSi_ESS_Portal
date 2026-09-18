import urllib.request
import json
import os
import dotenv

dotenv.load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}'
}

def fetch(table):
    req = urllib.request.Request(f"{url}/rest/v1/{table}?select=*", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())

try:
    employees = fetch('employees')
    print(f"Fetched {len(employees)} employees")
    
    try:
        timesheet_entries = fetch('timesheet_entries')
        print(f"Fetched {len(timesheet_entries)} timesheet_entries")
    except Exception as e:
        timesheet_entries = []
        print(f"timesheet_entries failed: {e}")
        
    try:
        timesheets = fetch('timesheets')
        print(f"Fetched {len(timesheets)} timesheets")
    except Exception as e:
        timesheets = []
        print(f"timesheets failed: {e}")

    with open('full_org_data.json', 'w', encoding='utf-8') as f:
        json.dump({
            'employees': employees,
            'timesheet_entries': timesheet_entries,
            'timesheets': timesheets
        }, f, indent=2)
    print("SAVED full_org_data.json")
except Exception as e:
    print(f"ERROR: {e}")
