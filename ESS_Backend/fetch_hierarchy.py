import os
import json
import dotenv

dotenv.load_dotenv()

from database import SupabaseDB

try:
    employees = SupabaseDB.select('employees', '*')
    print("Retrieved employees:", len(employees))
    
    # Try fetching timesheet_entries or any project references
    try:
        timesheet_entries = SupabaseDB.select('timesheet_entries', '*')
        print("Retrieved timesheet_entries:", len(timesheet_entries))
    except Exception as e:
        timesheet_entries = []
        print("timesheet_entries:", e)
        
    output = {
        'employees': employees,
        'timesheet_entries': timesheet_entries
    }
    
    with open('hierarchy_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
        
    print("DONE writing hierarchy_data.json")
except Exception as e:
    print("ERROR:", e)
