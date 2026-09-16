import json 
import os 
import string 
import getpass 
import secrets 
import base64
import hashlib
from cryptography.fernet import Fernet

USERS_FILE = "data/users.json"
PBKDF2_ITERATIONS = 600_000 

def _derive_key(password: str, salt: bytes):
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS, 32)
    return base64.urlsafe_b64encode(key)

def simple_encrypt(plain: str, pwd: str):
    salt = secrets.token_bytes(16)
    key  = _derive_key(pwd, salt)
    token = Fernet(key).encrypt(plain.encode())
    return base64.urlsafe_b64encode(salt + token).decode()

def simple_decrypt(blob: str, pwd: str):
    try:
        raw = base64.urlsafe_b64decode(blob.encode())
        if len(raw) < 16:
            return "<decryption failed: invalid data>"
        salt, tok = raw[:16], raw[16:]
        key = _derive_key(pwd, salt)
        return Fernet(key).decrypt(tok).decode()
    except Exception:
        return "<decryption failed>"

#user management
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    os.chmod(USERS_FILE, 0o600)

def _hash_master(password: str):
    salt = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS)
    return base64.b64encode(salt).decode() + ':' + base64.b64encode(h).decode()

def _verify_master(password: str, store: str):
    try:
        salt_b64, h_b64 = store.split(':')
        salt = base64.b64decode(salt_b64)
        h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS)
        return secrets.compare_digest(base64.b64encode(h).decode(), h_b64)
    except Exception:
        return False

def signup():
    users = load_users()
    print("\n--- Sign Up ---")
    username = input("Enter a new username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return None
    if username in users:
        print("Username already exists.")
        return None
        
    vault_file = f"data/{username}_vault.json"
    if os.path.exists(vault_file):
        print("A vault file for this user already exists locally. Signup aborted to protect data.")
        return None

    pwd = getpass.getpass("Enter a password: ")
    if pwd != getpass.getpass("Confirm password: "):
        print("Passwords do not match.")
        return None
        
    users[username] = {"password_hash": _hash_master(pwd)}
    save_users(users)
    
    with open(vault_file, "w") as f:
        json.dump([], f)
    os.chmod(vault_file, 0o600)
    print("Account created!")
    return username, pwd

def login():
    users = load_users()
    print("\n--- Log In ---")
    username = input("Username: ").strip()
    if username not in users:
        print("User not found.")
        return None
    pwd = getpass.getpass("Password: ")
    if _verify_master(pwd, users[username]["password_hash"]):
        print(f"Welcome back, {username}!")
        return username, pwd
    print("Incorrect password.")
    return None

#password tools
def generate_password(length: int = 12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

def check_strength(pwd: str):
    score = 0
    if len(pwd) >= 8: score += 1
    if any(c.isupper() for c in pwd): score += 1
    if any(c.isdigit() for c in pwd): score += 1
    if any(c in string.punctuation for c in pwd): score += 1
    return ["Weak","Weak","Moderate","Strong","Strong"][score]

#vault
def load_vault(username: str):
    fname = f"data/{username}_vault.json"
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            return json.load(f)
    return []

def save_vault(username: str, vault: list):
    fname = f"data/{username}_vault.json"
    with open(fname, 'w') as f:
        json.dump(vault, f, indent=2)
    os.chmod(fname, 0o600)

def add_entry(username: str, master_pwd: str):
    app = input("App / Website name: ").strip()
    user = input("Username / Email: ").strip()
    choice = input("1. Type password  2. Generate password: ")
    if choice == '2':
        try:
            length = int(input("Password length (default 12): ") or 12)
            if length < 4: length = 12
        except ValueError:
            length = 12
        pwd = generate_password(length) 
    else:
        pwd = getpass.getpass("Enter password: ")
        
    print("Password Strength:", check_strength(pwd))
    vault = load_vault(username)
    vault.append({"app": app, "username": user, "password": simple_encrypt(pwd, master_pwd)})
    save_vault(username, vault)
    print("Entry saved.")

def view_vault(username: str, master_pwd: str):
    vault = load_vault(username)
    if not vault:
        print("No passwords saved yet.")
        return
    print(f"\n--- {username}'s Password Vault ---")
    for idx, entry in enumerate(vault, 1):
        dec = simple_decrypt(entry["password"], master_pwd)
        print(f"{idx}. {entry['app']} | {entry['username']} | {dec}")

def delete_entry(username: str):
    vault = load_vault(username)
    if not vault:
        print("Vault is empty.")
        return
    for idx, entry in enumerate(vault, 1):
        print(f"{idx}. {entry['app']} ({entry['username']})")
    try:
        choice = int(input("Enter number to delete: ")) - 1
        if choice < 0 or choice >= len(vault):
            print("Invalid choice.")
            return
        vault.pop(choice)
        save_vault(username, vault)
        print("Deleted.")
    except ValueError:
        print("Invalid choice. Please enter a valid number.")

#menu
def main_menu(username: str, master_pwd: str):
    while True:
        print(f"\n--- Password Manager ({username}) ---")
        print("1. Add new password\n2. View saved passwords\n3. Delete a password")
        print("4. Generate strong password\n5. Check password strength\n6. Logout")
        ch = input("Enter choice: ")
        if ch == '1':
            add_entry(username, master_pwd)
        elif ch == '2':
            view_vault(username, master_pwd)
        elif ch == '3':
            delete_entry(username)
        elif ch == '4':
            print("Generated password:", generate_password())
        elif ch == '5':
            print("Strength:", check_strength(getpass.getpass("Enter password: ")))
        elif ch == '6':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")

def main():
    print("=== Multi-User Password Manager ===")
    while True:
        print("\n1. Sign Up\n2. Log In\n3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            user = signup()
            if user:
                main_menu(*user)
        elif choice == '2':
            user = login()
            if user:
                main_menu(*user)
        elif choice == '3':
            print("Goodbye! Stay safe online.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
