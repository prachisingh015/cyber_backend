import bcrypt
import getpass as get_input
from database import connect_db

# Prompt for password securely at runtime — never hardcode it
print("=== Admin Account Setup ===")
password = get_input.getpass("Enter the admin password to set: ")
confirm  = get_input.getpass("Confirm password: ")

if password != confirm:
    print("Passwords do not match. Aborting.")
    exit(1)

if len(password) < 8:
    print("Password must be at least 8 characters. Aborting.")
    exit(1)

hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

conn = connect_db()
cursor = conn.cursor()

# Check if admin already exists
cursor.execute("SELECT * FROM admin_users WHERE username=%s", ("admin",))
existing = cursor.fetchone()

if existing:
    print("Admin already exists.")
else:
    cursor.execute(
        "INSERT INTO admin_users (username, password_hash) VALUES (%s, %s)",
        ("admin", hashed.decode())
    )
    conn.commit()
    print("Admin created successfully.")

conn.close()
