import getpass
import subprocess
import threading
import bcrypt
from datetime import datetime, timedelta
from config import *
from database import connect_db

attempts_remaining = MAX_ATTEMPTS


# ==========================
# DATABASE LOGGING
# ==========================
def log_action(action, lock_until=None, file_path=None):
    """
    Logs actions to MySQL database.
    - action: Description of action (Access Granted, Wrong Password, USB Inserted, System Locked, etc.)
    - lock_until: datetime if system is locked
    - file_path: optional, if logging file access
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Log USB/folder/system actions
        cursor.execute("""
            INSERT INTO usb_logs (action_taken, system_user, lock_until)
            VALUES (%s, %s, %s)
        """, (action, getpass.getuser(), lock_until))

        # Log file access if provided
        if file_path:
            cursor.execute("""
                INSERT INTO file_access_logs (system_user, file_path, action)
                VALUES (%s, %s, %s)
            """, (getpass.getuser(), file_path, action))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging to database: {e}")


# ==========================
# CHECK LOCK STATUS
# ==========================
def is_system_locked():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT lock_until FROM usb_logs ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            if datetime.now() < result[0]:
                return True, result[0]

        return False, None
    except Exception as e:
        print(f"Error checking lock status: {e}")
        return True, None  # Fail safe: treat as locked if error


# ==========================
# VERIFY PASSWORD FROM DB
# ==========================
def verify_password_from_db(password_input):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT password_hash FROM admin_users WHERE username=%s", ("admin",))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return False

        stored_hash = result[0].encode()
        return bcrypt.checkpw(password_input.encode(), stored_hash)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


# ==========================
# FOLDER PERMISSION CONTROL
# ==========================
def grant_access():
    username = getpass.getuser()
    subprocess.run(f'icacls "{SECURE_FOLDER}" /grant {username}:(OI)(CI)F /T /C', shell=True)


def revoke_access():
    username = getpass.getuser()
    subprocess.run(f'icacls "{SECURE_FOLDER}" /remove {username} /T /C', shell=True)


# ==========================
# SYSTEM-LEVEL LOCK/UNLOCK
# ==========================
def lock_secure_folder():
    """
    Deny all access to SecureVault for everyone.
    """
    subprocess.run(f'icacls "{SECURE_FOLDER}" /deny Everyone:(F) /T /C', shell=True)
    log_action("SecureVault Locked")
    print(f"SecureVault locked for all users.")


def unlock_secure_folder():
    """
    Fully unlock SecureVault for the current user,
    removing any previous deny permissions to avoid UAC prompts.
    """
    username = getpass.getuser()
    
    # Reset all ACLs on folder and subfolders
    subprocess.run(f'icacls "{SECURE_FOLDER}" /reset /T /C', shell=True)
    
    # Grant full control to current user recursively
    subprocess.run(f'icacls "{SECURE_FOLDER}" /grant {username}:(OI)(CI)F /T /C', shell=True)
    
    log_action("SecureVault Unlocked")
    print(f"SecureVault fully unlocked for user {username}. No UAC prompt.")


# ==========================
# SESSION TIMER
# ==========================
def start_session_timer():
    def session_thread():
        expiry = datetime.now() + timedelta(minutes=SESSION_DURATION_MINUTES)
        while datetime.now() < expiry:
            pass
        revoke_access()
        lock_secure_folder()  # Automatically lock folder after session ends
        log_action("Session Expired - Access Revoked")
    thread = threading.Thread(target=session_thread)
    thread.start()


# ==========================
# MAIN VERIFY FUNCTION
# ==========================
def verify_user(password_input):
    global attempts_remaining

    locked, lock_until = is_system_locked()

    if locked:
        log_action("Blocked - Lock Active", lock_until)
        return {
            "status": "locked",
            "lock_until": str(lock_until)
        }

    if verify_password_from_db(password_input):
        log_action("Access Granted")
        unlock_secure_folder()   # Unlock folder fully, no UAC prompt
        grant_access()
        start_session_timer()
        attempts_remaining = MAX_ATTEMPTS

        return {
            "status": "granted",
            "message": "Access granted. Session started."
        }

    else:
        attempts_remaining -= 1
        log_action(f"Wrong Password - Attempts left: {attempts_remaining}")

        if attempts_remaining == 0:
            lock_until = datetime.now() + timedelta(minutes=LOCK_DURATION_MINUTES)
            lock_secure_folder()   # Lock folder fully
            log_action("System Locked", lock_until)
            attempts_remaining = MAX_ATTEMPTS

            return {
                "status": "locked",
                "lock_until": str(lock_until)
            }

        return {
            "status": "denied",
            "attempts_left": attempts_remaining
        }