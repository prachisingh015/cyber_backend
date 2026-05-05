🛡️ Cyber Backend — USB Threat Detection & Secure Vault System

🚀 Overview
A Windows-based cybersecurity backend system that detects USB device insertions in real-time, enforces password-based authentication, and protects sensitive data through system-level access control.
It combines system programming + cybersecurity + backend engineering to simulate enterprise-grade endpoint protection.

🧠 Built With
Python 3.8+
Flask (REST APIs)
MySQL (Event logging & authentication data)
WMI (Windows hardware event monitoring)
bcrypt (Secure password hashing)
Windows ACL (icacls) for folder protection
Multithreading (session management)

🎯 Objective
To design a real-time USB threat detection system that:
Prevents unauthorized access to sensitive folders
Logs all USB activities for audit purposes
Implements session-based secure access control
Demonstrates OS-level security enforcement on Windows

✨ Key Features
🔌 Real-time USB device detection using WMI
🔐 Password-protected SecureVault access system
🧠 Session-based authentication with auto-expiry
🚫 Auto-lock after multiple failed login attempts
🗂️ MySQL-based security event logging
🛡️ Folder-level protection using Windows icacls
📊 Full audit trail of system activity

🏗️ System Architecture

USB Device Inserted
        │
        ▼
usb_listener.py (WMI Event Detector)
        │
        ▼
Flask API (/verify)
        │
        ▼
security_core.py
   ├── Password verification (bcrypt)
   ├── Lock/Unlock folder (icacls)
   ├── Session management
   └── Attempt tracking
        │
        ▼
MySQL Database (Logs + Admin Data)

📁 Project Structure

cyber_backend/
├── app.py                  # Main API (USB logs)
├── database_schema.sql     # Database setup
├── .env.example            # Environment config template
│
└── usb_guard/
    ├── app.py              # Authentication API
    ├── config.py           # System configuration
    ├── database.py         # DB connection handler
    ├── security_core.py    # Core security logic
    ├── usb_listener.py     # USB event monitoring
    ├── create_admin.py     # Admin setup script
    └── requirements.txt    # Dependencies
    
⚙️ Installation & Setup
1️⃣ Clone repository
Bash
git clone https://github.com/prachisingh015/cyber_backend.git
cd cyber_backend
2️⃣ Install dependencies
Bash
pip install -r usb_guard/requirements.txt
3️⃣ Setup database
Bash
mysql -u root -p < database_schema.sql
4️⃣ Configure environment
Bash
cp .env.example .env
Set values:
Environment
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=cyber_threat_detection
5️⃣ Create Secure Folder
Bash
mkdir C:\SecureVault
6️⃣ Create Admin Account
Bash
python usb_guard/create_admin.py

▶️ Run System
Terminal 1 — Main API
Bash
python app.py
Terminal 2 — Security API
Bash
cd usb_guard
python app.py
Terminal 3 — USB Monitor
Bash
cd usb_guard
python usb_listener.py

🔌 API Endpoints
📌 USB Log API
POST /api/usb-log
JSON
{
  "usb_device_id": "USB\\VID_1234",
  "device_name": "SanDisk",
  "action_taken": "Inserted"
}
📌 Authentication API
POST /verify
JSON
{
  "password": "your_password"
}

🗄️ Database Tables
usb_logs → Tracks USB insert/remove events
file_access_logs → Logs SecureVault access
admin_users → Stores admin credentials (bcrypt hashed)

🔐 Security Highlights
🔒 bcrypt password hashing (no plaintext storage)
🚫 Auto lock after failed attempts
🧠 Session-based access control
🛑 System-level folder protection (Windows ACL)
🔐 Environment variable-based secrets

⚠️ Limitations
Windows-only (WMI + icacls dependency)
Single admin user system
In-memory session tracking (not persistent across restart)

🏆 Why This Project Matters
This project demonstrates:
Real-world cybersecurity system design
OS-level access control implementation
Backend API development (Flask)
Database integration (MySQL)
Event-driven system architecture
Secure authentication systems

📌 Future Improvements
Multi-user role system (Admin/User)
Web dashboard for logs
Cloud deployment (AWS / Azure)
AI-based anomaly detection
Cross-platform support (Linux/macOS)

📄 License
Educational use only
