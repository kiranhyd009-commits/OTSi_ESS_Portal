import json

with open('full_org_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

employees = data['employees']
emp_by_id = {e['employee_id']: e for e in employees}

mgr_ids = sorted(list(set(e.get('manager_id') for e in employees if e.get('manager_id'))))

hierarchy_report = []

for m_id in mgr_ids:
    m_emp = emp_by_id.get(m_id, {})
    subs = [e for e in employees if e.get('manager_id') == m_id]
    hierarchy_report.append({
        'manager_id': m_id,
        'manager_name': m_emp.get('full_name', 'Unknown'),
        'manager_designation': m_emp.get('designation', '-'),
        'manager_department': m_emp.get('department', '-'),
        'manager_role': m_emp.get('role', '-'),
        'total_reports': len(subs),
        'reports': [
            {
                'employee_id': s['employee_id'],
                'full_name': s['full_name'],
                'role': s.get('role'),
                'designation': s.get('designation'),
                'department': s.get('department'),
                'status': s.get('status'),
                'email': s.get('email')
            }
            for s in subs
        ]
    })

with open('hierarchy_structured.json', 'w', encoding='utf-8') as f:
    json.dump(hierarchy_report, f, indent=2)

print("Saved hierarchy_structured.json")
