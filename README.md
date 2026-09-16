# VaultCLI

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-CLI-lightgrey)

A secure, multi-user, terminal-based password manager written in Python. Each user's vault is protected by their own master password — passwords are never stored in plain text.

## Table of Contents

- [Features](#features)
- [Screenshot](#screenshot)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)
- [Contributing](#contributing)
- [License](#license)

## Features

- Multi-user support (separate encrypted vault per user)
- Master password required to unlock a user's vault
- AES-based encryption (via `Fernet`) for every stored password
- PBKDF2-HMAC-SHA256 key derivation (600,000 iterations) for both password hashing and encryption keys
- Random salt generated per encryption operation
- Built-in strong password generator
- Password strength checker
- Add / view / delete vault entries
- Vault and user files locked to owner-only permissions on Unix systems (`chmod 600`)

## Screenshot

_Add a screenshot or terminal recording here showing the app in action._

```
=== Multi-User Password Manager ===

1. Sign Up
2. Log In
3. Exit
```

## Requirements

- Python 3.8+
- See [`requirements.txt`](requirements.txt)

## Setup

```bash
git clone https://github.com/Arjunvs-ACE/VaultCLI.git
cd VaultCLI
pip install -r requirements.txt
```

## Usage

```bash
python password_manager.py
```

You'll be prompted to sign up or log in. Once logged in, you can:

1. Add a new password (typed manually or auto-generated)
2. View saved passwords (decrypted with your master password)
3. Delete a password
4. Generate a strong random password
5. Check the strength of a password
6. Log out

## How It Works

- **Signup:** your master password is hashed with PBKDF2 (salted) and stored in `users.json`. The raw password itself is never saved.
- **Vault:** each user gets a `<username>_vault.json` file. Each entry's password is encrypted individually with a key derived from your master password and a random salt.
- **Login:** your master password is verified against the stored hash using a timing-safe comparison.

## Project Structure

```
VaultCLI/
├── password_manager.py    # Main application
├── requirements.txt       # Python dependencies
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── .gitignore
```

## Security Notes

- Your master password exists in memory only for the duration of your session — it is never written to disk.
- File permission locking (`chmod 600`) is enforced only on Unix-like systems (Linux/macOS); it has no effect on Windows.
- This project is intended as a learning/demo project. For real-world password management, use an audited, actively maintained tool.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

This is a personal/educational project. Use at your own risk — always keep backups of anything important.