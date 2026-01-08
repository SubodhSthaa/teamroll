# Payroll MVP - Quick Start Guide

## 🚀 Launch in 30 seconds

```bash
python3 simple_server.py
```

Then open: **http://localhost:8080**

## 🎯 2-Minute Demo Script

### Step 1: Login as Admin (15 seconds)
- Email: `admin@payroll.com`
- Password: `admin123`

### Step 2: Add Employees (30 seconds)
Add 2-3 employees quickly:

| Name | Email | Salary |
|------|-------|--------|
| Alice Johnson | alice@company.com | 5000 |
| Bob Smith | bob@company.com | 6000 |
| Carol Lee | carol@company.com | 5500 |

Click "Add Employee" for each.

### Step 3: Run Payroll (30 seconds)
- Select current month
- Click "Generate Payslips"
- See instant calculation: **Gross → 25% deductions → Net**

### Step 4: View Results (30 seconds)
- Scroll to "All Payslips" table
- See all generated payslips with calculations

### Step 5: Employee View (15 seconds)
- Logout
- Login as: `alice@company.com` / `password123`
- See personalized payslip view

**Demo complete!** ✅

## 📊 Core Features

### Admin Functions
1. **Add Employee**: Name, Email, Salary
2. **Run Payroll**: Generate monthly payslips for all employees
3. **View All**: Employees and payslips in one dashboard

### Employee Functions
1. **View Payslips**: Clean card view of all payslips
2. **See Breakdown**: Gross pay, deductions, net pay

## 💡 Payroll Logic

Simple 25% deduction model:
- **Tax**: 20% of gross
- **Insurance**: 5% of gross
- **Net Pay**: Gross - Total Deductions

Example:
```
Gross: $5,000
Tax (20%): -$1,000
Insurance (5%): -$250
─────────────────
Net Pay: $3,750
```

## 🗄️ Database Schema

### employees
- id, name, email, monthly_salary, role, password_hash

### payslips
- id, employee_id, month, year, gross_pay, deductions, net_pay
- Unique constraint: (employee_id, month, year)

### sessions
- id, session_id, employee_id

## 🔑 Default Credentials

**Admin Account**
- Email: admin@payroll.com
- Password: admin123

**New Employees**
- Default password: password123
- Use their email to login

## 📁 File Structure

```
simple_server.py         # Main server (HTTP routes, auth)
simple_database.py       # SQLite setup & queries
payroll_engine.py        # Payroll calculation logic
simple_templates/
  ├── login.html         # Login page
  ├── admin.html         # Admin dashboard
  └── employee.html      # Employee payslip view
```

## 🎨 Design Philosophy

✅ **DO**
- Single file server
- Minimal dependencies (stdlib only)
- Inline styles (no external CSS)
- Clear separation: DB → Logic → Server → UI

❌ **DON'T**
- Complex frameworks
- Multiple config files
- Build processes
- Advanced auth flows

## 🚀 API Endpoints

### Authentication
- `POST /api/login` - Login with email/password
- `POST /api/logout` - Clear session
- `GET /api/me` - Get current user

### Admin Endpoints
- `GET /api/employees` - List all employees
- `POST /api/employees` - Create new employee
- `POST /api/payroll/run` - Generate payslips for month/year

### Employee Endpoints
- `GET /api/payslips` - Get payslips (filtered by role)

## 💭 What's NOT Included

This is intentionally minimal:
- ❌ No attendance tracking
- ❌ No leave management
- ❌ No tax automation
- ❌ No email notifications
- ❌ No PDF generation
- ❌ No audit logs
- ❌ No multi-company
- ❌ No role permissions beyond admin/employee

## 🔧 Troubleshooting

**Port already in use?**
```bash
# Kill existing process
pkill -f simple_server.py

# Or use different port
# Edit simple_server.py: run_server(port=8081)
```

**Database issues?**
```bash
# Delete and recreate
rm payroll_mvp.db
python3 simple_server.py
```

## 📈 Next Steps

If you need to expand:
1. Add PDF payslip export
2. Email notifications on payroll run
3. More complex tax calculations
4. Bonus/deduction customization
5. Attendance integration

But for MVP demo - **you're done!** 🎉
