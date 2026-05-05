import requests
import wmi
from security_core import verify_user, log_action

FLASK_BASE_URL = "http://127.0.0.1:5000"

c = wmi.WMI()

print("USB Guard Running... Monitoring USB devices 🔌")

# Create watcher object once
usb_watcher = c.watch_for(notification_type="Creation", wmi_class="Win32_USBHub")


def check_lock_status():
    try:
        response = requests.get(f"{FLASK_BASE_URL}/status")
        data = response.json()
        return data["locked"], data["lock_until"]
    except:
        return True, None


def verify_password(password):
    try:
        response = requests.post(
            f"{FLASK_BASE_URL}/verify",
            json={"password": password}
        )
        return response.json()
    except:
        return {"status": "error"}


while True:
    try:
        event = usb_watcher()
        print("\n🔌 USB Device Inserted")

        # ✅ Log USB insertion
        log_action("USB Device Inserted")

        locked, lock_until = check_lock_status()

        if locked:
            print(f"🚫 SYSTEM LOCKED until {lock_until}")
            continue

        # Keep asking until granted or locked
        while True:
            password = input("Enter password: ")
            result = verify_password(password)

            if result["status"] == "granted":
                print("✅ Access Granted")
                break

            elif result["status"] == "denied":
                print(f"❌ Wrong Password. Attempts left: {result['attempts_left']}")

            elif result["status"] == "locked":
                print(f"🚫 System Locked until {result['lock_until']}")
                break

            else:
                print("⚠️ Error communicating with server")
                break

    except Exception as e:
        print("Error:", e)