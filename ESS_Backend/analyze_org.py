import os
import sys
import json
import dotenv

dotenv.load_dotenv()

from database import SupabaseDB

employees = SupabaseDB.select('employees', '*')
sys.stdout.flush()

try:
    timesheets = SupabaseDB.select('timesheet_entries', '*')
except Exception as e:
    timesheets = []

projects_set = set()
emp_projects = {}
for t in timesheets:
    p = t.get('project_name')
    e = t.get('employee_id')
    if p:
        projects_set.add(p)
        if e:
            emp_projects.setdefault(e, set()).add(p)

# Clean and sort employees
clean_emps = []
for emp in employees:
    e_id = emp.get('employee_id')
    clean_emps.append({
        'employee_id': e_id,
        'full_name': emp.get('full_name'),
        'email': emp.get('email'),
        'role': emp.get('role'),
        'designation': emp.get('designation'),
        'department': emp.get('department'),
        'manager_id': emp.get('manager_id'),
        'manager_name': emp.get('manager_name'),
        'status': emp.get('status'),
        'projects': list(emp_projects.get(e_id, []))
    })

clean_emps.sort(key=lambda x: (x.get('department') or '', x.get('role') or '', x.get('employee_id') or ''))

with open('clean_employees.json', 'w', encoding='utf-8') as f:
    json.dump(clean_emps, f, indent=2)

print(f"EXPORTED {len(clean_emps)} EMPLOYEES SUCCESSFULLY", flush=True)
