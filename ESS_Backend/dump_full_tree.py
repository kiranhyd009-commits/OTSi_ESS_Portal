import json

with open('full_org_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

employees = data['employees']
emp_by_id = {e['employee_id']: e for e in employees}

# Sort by hierarchy
# 1. Top level (No manager or self-managed or Director)
# 2. Managers
# 3. Direct reports

print("Total employees loaded:", len(employees))

# Check employees without manager or top level
top_level = [e for e in employees if not e.get('manager_id') or e.get('manager_id') == e.get('employee_id')]
print("Top level / No manager:", [f"{e['employee_id']} - {e['full_name']} ({e.get('designation')}, Dept: {e.get('department')})" for e in top_level])

# Check all managers
mgr_ids = set(e.get('manager_id') for e in employees if e.get('manager_id'))
print("Unique Manager IDs in dataset:", mgr_ids)

# Let's inspect who reports to whom
for m_id in sorted(mgr_ids):
    m_emp = emp_by_id.get(m_id)
    m_name = f"{m_emp['full_name']} ({m_emp.get('designation')}, Dept: {m_emp.get('department')}, Role: {m_emp.get('role')})" if m_emp else "Unknown/External"
    subs = [e for e in employees if e.get('manager_id') == m_id]
    print(f"\n▶ Manager [{m_id}] {m_name} (Total Reports: {len(subs)}):")
    for s in subs:
        print(f"   └── [{s['employee_id']}] {s['full_name']} | {s.get('designation')} | Dept: {s.get('department')} | Role: {s.get('role')} | Status: {s.get('status')}")
