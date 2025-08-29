# TeamRoll

**TeamRoll** is an integrated online platform designed for teams and small to medium-sized businesses (SMBs).  
It provides a simple, cost-effective, and powerful solution for managing payroll, employee information, and tax compliance — all in one place.  

---

## 🚀 Features
- Automated payroll processing (base salary, bonuses, deductions)
- Leave & attendance tracking with payroll integration
- Payslip generation and reporting
- Centralized HR database for employee management
- Tax & compliance support
- Role-based access (Admin, Manager, Employee)

---

## 🛠 Tech Stack
- **Backend:** Python (no frameworks, built on `http.server`)
- **Frontend:** HTML + CSS (lightweight, no frameworks)
- **Database:** SQLite (built-in, optional for HR/Payroll data)

---

## 📂 Project Structure
```
teamroll/
 ├── server.py        # Backend server (Python)
 ├── modules/         # Core services
 │   ├── hr_service.py
 │   ├── payroll_service.py
 │   ├── accounting_service.py
 ├── static/          # CSS, JS, assets
 │   └── styles.css
 └── templates/       # HTML files
     └── index.html
```

---

## ⚙️ Installation & Setup
### Prerequisites
- Python 3.8+
- (Optional) SQLite for database storage

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/teamroll.git
   cd teamroll
   ```
2. Run the server:
   ```bash
   python server.py
   ```
3. Open your browser and visit:
   ```
   http://localhost:8080
   ```

---

## 📖 Usage
- Employees can view payslips and update profiles.  
- Admins can add employees, approve payroll, and generate reports.  
- System automatically calculates net salary, deductions, and compliance.  

---

## ✅ Roadmap
- [ ] Add authentication (login for admin, manager, employee)  
- [ ] Build reporting dashboards (charts & exports)  
- [ ] Integrate tax filing automation  
- [ ] Multi-language & regional compliance support  

---

## 🤝 Contributing
Contributions are welcome! Please fork the repo and submit a pull request.  

---

## 📜 License
This project is licensed under the MIT License.  
