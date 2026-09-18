import json

with open('full_org_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

employees = data['employees']

# Map of employees
emp_by_id = {e['employee_id']: e for e in employees}

# Find roles
admins = [e for e in employees if e.get('role') == 'admin']
hrs = [e for e in employees if e.get('role') == 'hr']
managers = [e for e in employees if any(sub.get('manager_id') == e['employee_id'] for sub in employees)]
other_leads = [e for e in employees if 'Manager' in (e.get('designation') or '') or 'Lead' in (e.get('designation') or '') or 'Director' in (e.get('designation') or '')]

# Reporting structure
reports_to = {} # mgr_id -> list of direct reports
for e in employees:
    mgr_id = e.get('manager_id')
    if mgr_id:
        reports_to.setdefault(mgr_id, []).append(e)

# Departments
depts = {}
for e in employees:
    d = e.get('department') or 'Unassigned'
    depts.setdefault(d, []).append(e)

print(f"Total Employees: {len(employees)}")
print(f"Admins: {len(admins)} -> {[e['employee_id'] + ' (' + e['full_name'] + ')' for e in admins]}")
print(f"HRs: {len(hrs)} -> {[e['employee_id'] + ' (' + e['full_name'] + ')' for e in hrs]}")
print(f"Managers with direct reports: {len(reports_to)}")
for mgr_id, subs in reports_to.items():
    mgr = emp_by_id.get(mgr_id)
    mgr_name = mgr['full_name'] if mgr else "Unknown/External"
    mgr_desig = mgr['designation'] if mgr else "-"
    print(f"  Manager: {mgr_id} - {mgr_name} ({mgr_desig}) -> {len(subs)} direct reports")

print(f"\nDepartments count: {len(depts)}")
for d, emps in depts.items():
    print(f"  {d}: {len(emps)} employees")

