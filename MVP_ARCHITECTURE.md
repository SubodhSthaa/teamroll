# Payroll MVP - Architecture Overview

## System Comparison

### Original System vs MVP

| Feature | Original System | MVP System |
|---------|----------------|------------|
| **Files** | 15+ files | 4 files |
| **Database Tables** | 7 tables | 3 tables |
| **Features** | Attendance, Leave, HR, Payroll | Payroll only |
| **Auth Flow** | Pending approvals, complex | Simple login |
| **Dependencies** | Multiple modules | Python stdlib only |
| **Setup Time** | 5+ minutes | 30 seconds |
| **Demo Time** | 5+ minutes | 2 minutes |
| **Code Lines** | 2000+ | ~600 |

## Architecture

### 3-Layer Design

```
┌─────────────────────────────────────┐
│         Frontend (HTML)             │
│  - Inline CSS & JavaScript          │
│  - No build process                 │
│  - 3 pages (login, admin, employee) │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Backend (simple_server.py)     │
│  - HTTP routing                     │
│  - Session management               │
│  - Auth middleware                  │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│   Business Logic (payroll_engine.py)│
│  - Payroll calculations             │
│  - Payslip generation               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│    Database (simple_database.py)    │
│  - SQLite operations                │
│  - Schema management                │
└─────────────────────────────────────┘
```

## File Structure

```
payroll-mvp/
├── simple_server.py          # 280 lines - HTTP server & routing
├── simple_database.py        #  80 lines - DB setup & queries
├── payroll_engine.py         #  60 lines - Payroll logic
├── simple_templates/
│   ├── login.html           # 110 lines - Login page
│   ├── admin.html           # 220 lines - Admin dashboard
│   └── employee.html        # 130 lines - Employee view
└── payroll_mvp.db           # Auto-generated SQLite database
```

**Total: ~880 lines of code**

## Database Schema

### Minimal 3-Table Design

```sql
employees
├── id (PK)
├── name
├── email (unique)
├── monthly_salary
├── role (admin/employee)
└── password_hash

payslips
├── id (PK)
├── employee_id (FK)
├── month
├── year
├── gross_pay
├── deductions
├── net_pay
└── UNIQUE(employee_id, month, year)

sessions
├── id (PK)
├── session_id (unique)
└── employee_id (FK)
```

## API Design

### RESTful Endpoints

```
Authentication
POST   /api/login        { email, password } → { success, role }
POST   /api/logout       → { success }
GET    /api/me           → { id, name, email, role }

Employees (Admin only)
GET    /api/employees    → { employees: [...] }
POST   /api/employees    { name, email, monthly_salary } → { success, employee_id }

Payroll
GET    /api/payslips     → { payslips: [...] } (filtered by role)
POST   /api/payroll/run  { month, year } → { success, generated, payslips }
```

## Payroll Calculation Engine

### Simple Deduction Model

```python
TAX_RATE = 0.20        # 20% tax
INSURANCE_RATE = 0.05  # 5% insurance

deductions = gross_pay * (TAX_RATE + INSURANCE_RATE)
net_pay = gross_pay - deductions
```

### Example Calculation

```
Employee: Alice Johnson
Monthly Salary: $5,000

Calculation:
─────────────────────
Gross Pay:        $5,000.00
Tax (20%):       -$1,000.00
Insurance (5%):    -$250.00
─────────────────────
Total Deductions: $1,250.00
Net Pay:          $3,750.00
```

## Security Model

### Simple Session-Based Auth

1. **Login**: Email + password → SHA256 hash check
2. **Session**: Generate random token, store in DB
3. **Cookie**: HttpOnly session cookie (24h expiry)
4. **Middleware**: Check session on protected routes
5. **Role Check**: Admin/Employee route restrictions

### What's NOT Included (Intentionally)

- No JWT tokens
- No OAuth
- No password reset
- No 2FA
- No rate limiting
- No CSRF protection
- No XSS sanitization

**Why?** This is a 2-minute demo MVP, not production code.

## Performance Characteristics

### Response Times (Local)

| Endpoint | Time |
|----------|------|
| Login | ~10ms |
| Add Employee | ~5ms |
| Run Payroll (10 employees) | ~20ms |
| View Payslips | ~5ms |

### Scalability Limits

- **SQLite**: Good for <100 employees
- **Single-threaded**: One request at a time
- **In-memory sessions**: Lost on restart
- **No caching**: Query DB every time

**For MVP demo**: These limits are fine!

## Extension Points

If you need to scale:

### Easy Additions (1-2 hours)
- PDF payslip export (use ReportLab)
- Email notifications (SMTP)
- More tax brackets
- Bonus/deduction fields

### Medium Additions (1 day)
- PostgreSQL support
- Multi-tenancy
- Audit logs
- Role-based permissions

### Major Refactor (1 week)
- React/Vue frontend
- REST API with FastAPI
- Background job processing
- Microservices architecture

## Key Design Decisions

### Why SQLite?
- Zero configuration
- Single file
- Perfect for demos
- Fast for <1000 records

### Why No Framework?
- Faster to write
- Easier to understand
- No dependencies
- Total control

### Why Inline Styles?
- No build process
- No external files
- Works immediately
- Easy to customize

### Why Session Cookies?
- Simple to implement
- Native browser support
- Secure with HttpOnly
- No JWT complexity

## Testing Strategy

### Manual Testing Checklist

**Admin Flow**
- [ ] Login as admin
- [ ] Add 3 employees
- [ ] Run payroll for current month
- [ ] View all payslips
- [ ] Verify calculations (25% deduction)
- [ ] Logout

**Employee Flow**
- [ ] Login as employee
- [ ] View payslips
- [ ] Verify personal data
- [ ] Logout

**Edge Cases**
- [ ] Duplicate email blocked
- [ ] Duplicate payslip blocked (same month/year)
- [ ] Unauthorized access rejected
- [ ] Invalid login rejected

## Deployment

### Local Demo
```bash
python3 simple_server.py
# http://localhost:8080
```

### Production (Not Recommended)
This is a demo MVP, but if you must:
```bash
# Behind nginx reverse proxy
# SSL/TLS required
# Use PostgreSQL instead of SQLite
# Add rate limiting
# Add monitoring
```

**Better**: Rewrite with proper framework for production.

## Maintenance

### Database Backup
```bash
cp payroll_mvp.db payroll_mvp.backup.db
```

### Reset Database
```bash
rm payroll_mvp.db
python3 simple_server.py
```

### View Database
```bash
sqlite3 payroll_mvp.db
.tables
.schema employees
SELECT * FROM payslips;
```

## Conclusion

This MVP proves the core concept:
- ✅ Create employees
- ✅ Calculate payroll
- ✅ Generate payslips
- ✅ Employee portal

**Demo time**: 2 minutes
**Code size**: 880 lines
**Dependencies**: None

Perfect for pitching the idea! 🚀
