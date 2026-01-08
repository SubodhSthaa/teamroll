# TeamRoll Authentication System

## Overview

TeamRoll now features a complete authentication system with role-based access control, supporting both administrators and employees with separate dashboards and an employee registration approval workflow.

## Key Features

1. **Default Admin Account** - Created automatically on first initialization
2. **Employee Registration with Approval** - Employees must be approved by admins
3. **Role-Based Access Control** - Separate dashboards for admins and employees
4. **Session Management** - Secure cookie-based sessions (24-hour expiration)
5. **Password Hashing** - SHA-256 password hashing for security

## Getting Started

### 1. Initialize the Database

Run the server for the first time to create the database and default admin account:

```bash
python3 server.py
```

You will see output like this:

```
============================================================
DEFAULT ADMIN ACCOUNT CREATED
============================================================
Username: admin
Password: admin123
Email: admin@teamroll.local
============================================================
IMPORTANT: Change the default password after first login!
============================================================

Database initialized successfully!
TeamRoll server running on http://localhost:8080
```

### 2. Login as Admin

1. Open your browser to `http://localhost:8080`
2. Click "Login"
3. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
4. You'll be redirected to the admin dashboard

## User Roles

### Administrator

**Access:**
- Full system access
- Employee management
- Payroll processing
- Attendance tracking
- **Registration approvals** (NEW!)

**Can Access:**
- `/dashboard` - Admin dashboard with metrics
- `/employees` - Add/edit employee records
- `/payroll` - Process payroll
- `/attendance` - View all attendance
- `/admin/registrations` - Approve/reject employee registrations

### Employee

**Access:**
- Personal information
- Own payroll history
- Attendance check-in/out
- Own attendance records

**Can Access:**
- `/dashboard` - Employee dashboard
- `/payroll` - Personal payslips only
- `/attendance` - Own attendance

## Registration Workflow

### For Administrators

Admins can register directly without approval:

1. Go to `/register`
2. Select "Administrator" role
3. Fill in username, email, password
4. Submit - account is created immediately

### For Employees

Employees must be approved by an admin:

1. **Admin creates employee record first**
   - Login as admin
   - Go to "Employees"
   - Add new employee with Employee ID, name, position, etc.

2. **Employee registers using Employee ID**
   - Go to `/register`
   - Select "Employee" role
   - Enter Employee ID (from admin)
   - Fill in username, email, password
   - Submit registration request

3. **Admin approves registration**
   - Admin receives notification (badge on Registrations link)
   - Go to `/admin/registrations`
   - Review employee details
   - Add optional notes
   - Click "Approve Registration" or "Reject Registration"

4. **Employee can login**
   - After approval, employee can login at `/login`
   - Redirected to employee dashboard

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user info

### Admin Only

- `GET /api/admin/pending-registrations` - Get pending registrations
- `POST /api/admin/approve-registration` - Approve registration
  ```json
  {
    "registration_id": 1,
    "notes": "Approved by HR"
  }
  ```
- `POST /api/admin/reject-registration` - Reject registration
  ```json
  {
    "registration_id": 1,
    "notes": "Invalid employee ID"
  }
  ```

## Database Schema

### New Tables

#### `users`
- Stores authentication credentials
- Links to employee records via `employee_id`
- Role-based access (`admin` or `employee`)

#### `sessions`
- Manages user sessions
- 24-hour expiration
- Secure session IDs

#### `pending_registrations`
- Stores employee registration requests
- Tracks approval status (`pending`, `approved`, `rejected`)
- Admin notes for audit trail

## Security Features

1. **Password Hashing** - SHA-256 (consider upgrading to bcrypt for production)
2. **HttpOnly Cookies** - Prevents XSS attacks on session tokens
3. **Session Expiration** - 24-hour session timeout
4. **Role-Based Access** - Routes protected by role checks
5. **Employee ID Validation** - Prevents unauthorized registrations

## Workflow Example

### Scenario: New Employee Onboarding

1. **HR/Admin creates employee record**
   ```
   Employee ID: EMP001
   Name: John Doe
   Position: Software Engineer
   Department: Engineering
   ```

2. **Employee receives Employee ID and registers**
   ```
   Username: johndoe
   Employee ID: EMP001
   Email: john.doe@company.com
   Password: ********
   ```

3. **System creates pending registration**
   - Status: pending
   - Linked to EMP001

4. **Admin reviews and approves**
   - Views pending registration
   - Verifies John Doe details match employee record
   - Adds note: "Approved - starting Monday"
   - Clicks "Approve Registration"

5. **User account created**
   - Status changed to: approved
   - User record created with role: employee
   - John can now login

6. **John logs in**
   - Goes to employee dashboard
   - Can check in/out
   - View payslips
   - Track attendance

## File Structure

```
project/
├── modules/
│   ├── auth_service.py         # Authentication logic
│   ├── database.py              # Database setup with default admin
│   ├── hr_service.py
│   ├── payroll_service.py
│   └── attendance_service.py
├── templates/
│   ├── index.html               # Landing page
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   ├── admin_dashboard.html     # Admin dashboard
│   ├── employee_dashboard.html  # Employee dashboard
│   ├── employee_payroll.html    # Employee payroll view
│   ├── admin_registrations.html # Registration approval page
│   ├── employees.html
│   ├── payroll.html
│   └── attendance.html
└── server.py                    # Main server with auth routes
```

## Important Notes

1. **Change Default Password**
   - The default admin password (`admin123`) should be changed immediately
   - Currently, password change feature is not implemented
   - Consider adding this feature for production

2. **Production Considerations**
   - Use stronger password hashing (bcrypt, argon2)
   - Implement HTTPS
   - Add rate limiting for login attempts
   - Add password reset functionality
   - Add email verification
   - Use environment variables for secrets
   - Implement audit logging

3. **Employee Registration Flow**
   - Employees MUST exist in the employees table before registration
   - One employee record = one user account
   - Duplicate registrations are prevented

4. **Session Management**
   - Sessions expire after 24 hours
   - Expired sessions are automatically cleaned up
   - No concurrent session limit (multiple logins allowed)

## Troubleshooting

### Can't Login

- Verify username and password
- Check database for user account
- Clear browser cookies
- Check server logs

### Employee Can't Register

- Verify Employee ID exists in employees table
- Check for pending registration request
- Ensure no existing user account for that Employee ID

### Admin Can't See Pending Registrations

- Check user role is 'admin'
- Verify pending_registrations table has records with status='pending'
- Check browser console for errors

## Next Steps

Consider adding:
- Password change functionality
- Password reset via email
- Two-factor authentication
- Email notifications for approvals
- Bulk approval/rejection
- Registration request history
- User activity logging
- Password strength requirements
- Account lockout after failed attempts
