# 🛡️ Cyber Backend — USB Threat Detection System
                                                                                 
A Windows-based cybersecurity backend that monitors USB device insertions in real time, enforces password-gated access to a protected folder (`SecureVault`), and logs all security events to a MySQL database.

---
                                                                                
## 📌 Overview

When a USB device is plugged into a monitored Windows machine, the system:

1. Detects the insertion via WMI (Windows Management Instrumentation)
2. Prompts the user for a password before granting access
3. Unlocks `SecureVault` (a protected folder) only on successful authentication
4. Locks the system after repeated failed attempts
5. Automatically revokes access when the session expires
6. Logs every event — insertions, access grants, denials, and locks — to MySQL

---

## 🏗️ Architecture

```
cyber_backend/
├── app.py                  # Main API — receives and stores USB log entries
└── usb_guard/
    ├── app.py              # USB Guard API — handles password verification & lock status
    ├── config.py           # Settings: folder path, max attempts, session/lock durations
    ├── database.py         # MySQL connection factory (env-var-based credentials)
    ├── security_core.py    # Core logic: verify password, lock/unlock folder, session timer
    ├── usb_listener.py     # WMI-based USB event watcher (entry point on target machine)
    ├── create_admin.py     # One-time script to create the admin account
    └── requirements.txt    # Python dependencies
```

### Component Interaction

```
USB Device Inserted
        │
        ▼
  usb_listener.py  ──── WMI event ────▶  Detects insertion
        │
        ▼
  POST /verify  ──────────────────────▶  usb_guard/app.py
                                                │
                                         security_core.py
                                         ├── Checks lock status (MySQL)
                                         ├── Verifies bcrypt password hash
                                         ├── Grants/revokes folder ACLs (icacls)
                                         └── Starts session timer thread
        │
        ▼
  POST /api/usb-log  ─────────────────▶  app.py  ──▶  MySQL (usb_logs table)
```

---

## ⚙️ Prerequisites

- **OS**: Windows 10/11 (required for WMI and `icacls`)
- **Python**: 3.8 or higher
- **MySQL**: 5.7+ or MariaDB 10.3+
- The `SecureVault` folder must exist at the path configured in `config.py`

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone (https://github.com/prachisingh015/cyber_backend.git)
cd cyber_backend
```

### 2. Install dependencies

```bash
pip install -r usb_guard/requirements.txt
```

### 3. Configure the database

Create the database and tables using the provided schema:

```bash
mysql -u root -p < database_schema.sql
```

### 4. Set environment variables
                 
Copy `.env.example` to `.env` and fill in your MySQL credentials:
                               
```bash
cp .env.example .env
```
                                 
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=cyber_threat_detection
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.
                                      
Set the variables in your shell before running (Windows):
                                
```cmd
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=your_password_here
set DB_NAME=cyber_threat_detection
```

Or on PowerShell:

```powershell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password_here"
$env:DB_NAME="cyber_threat_detection"
```

### 5. Configure the protected folder

Edit `usb_guard/config.py` to match your setup:

```python
SECURE_FOLDER = r"C:\SecureVault"   # Path to the folder to protect

MAX_ATTEMPTS           = 3           # Failed attempts before lockout
LOCK_DURATION_MINUTES  = 5           # How long the lockout lasts
SESSION_DURATION_MINUTES = 10        # How long an authenticated session lasts
```

Create the `SecureVault` folder if it doesn't exist:

```cmd
mkdir C:\SecureVault
```

### 6. Create the admin account

Run this **once** to register the admin password in the database:

```bash
python usb_guard/create_admin.py
```

You will be prompted to enter and confirm a password. The hash is stored securely using bcrypt — the plaintext password is never saved.

---

## ▶️ Running the System

Start both Flask servers, then launch the USB listener. Open three terminals:

**Terminal 1 — Main log API** (default port 5000):

```bash
python app.py
```

**Terminal 2 — USB Guard API** (port 5000, run from `usb_guard/`):

```bash
cd usb_guard
python app.py
```

> If both servers conflict on port 5000, change one — update `FLASK_BASE_URL` in `usb_listener.py` accordingly.

**Terminal 3 — USB listener** (run from `usb_guard/`):

```bash
cd usb_guard
python usb_listener.py
```

The listener will print `USB Guard Running... Monitoring USB devices 🔌` and begin watching for hardware events.

---

## 🔌 API Reference

### Main API (`app.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/usb-log` | Store a USB event log entry |

**POST `/api/usb-log` — Request body:**

```json
{
  "usb_device_id": "USB\\VID_1234&PID_5678",
  "device_name": "SanDisk Ultra",
  "vendor_name": "SanDisk",
  "action_taken": "USB Device Inserted",
  "session_start": "2024-01-15 10:30:00",
  "session_end": null,
  "system_user": "DESKTOP-ABC\\John"
}
```

---

### USB Guard API (`usb_guard/app.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check API status |
| `GET` | `/status` | Check if the system is currently locked |
| `POST` | `/verify` | Submit a password for verification |

**GET `/status` — Response:**

```json
{
  "locked": true,
  "lock_until": "2024-01-15 10:35:00"
}
```

**POST `/verify` — Request body:**

```json
{ "password": "your_password" }
```

**Possible responses:**

```json
{ "status": "granted", "message": "Access granted. Session started." }
{ "status": "denied",  "attempts_left": 2 }
{ "status": "locked",  "lock_until": "2024-01-15 10:35:00" }
```

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| `usb_logs` | Records every USB event: insertions, access decisions, lock/unlock actions |
| `file_access_logs` | Tracks individual file access within `SecureVault` |
| `admin_users` | Stores the admin username and bcrypt-hashed password |

---

## 🔐 Security Design

- **Passwords** are hashed with [bcrypt](https://pypi.org/project/bcrypt/) and never stored in plaintext
- **Folder permissions** are enforced via Windows `icacls` — deny rules block all users during lockout
- **Fail-safe locking** — if the database is unreachable, the system defaults to locked
- **Session expiry** — access is automatically revoked after the configured session duration
- **Credentials via environment variables** — no secrets are hardcoded anywhere in the codebase

---

## 🧪 Testing the Flow Manually

You can simulate the full flow without physical hardware using `curl` or a REST client:

```bash
# Check lock status
curl http://localhost:5000/status

# Attempt password verification
curl -X POST http://localhost:5000/verify \
  -H "Content-Type: application/json" \
  -d "{\"password\": \"your_password\"}"

# Log a USB event
curl -X POST http://localhost:5001/api/usb-log \
  -H "Content-Type: application/json" \
  -d "{\"device_name\": \"Test Drive\", \"action_taken\": \"USB Device Inserted\", \"system_user\": \"testuser\"}"
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | REST API framework |
| `mysql-connector-python` | MySQL database driver |
| `bcrypt` | Password hashing |
| `wmi` | Windows USB event monitoring |
| `flask-cors` | Cross-origin request support (main API) |
| `requests` | HTTP client used by the USB listener |

---

## ⚠️ Known Limitations

- **Windows only** — WMI and `icacls` are Windows-specific; this will not run on Linux/macOS
- **Single admin account** — the current schema supports one admin user (`username = "admin"`)
- **In-memory attempt counter** — `attempts_remaining` in `security_core.py` resets if the process restarts; a production system should persist this in the database

---

## 📄 License

This project is intended for educational and internal security tooling purposes.
