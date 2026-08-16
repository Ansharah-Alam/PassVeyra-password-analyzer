# PassVeyra — Password Strength Analyzer

A desktop app that checks how strong your password is in real time, suggests improvements, generates a strong one for you, and saves it for later.

## 🔐 Features

- **Live strength checking** — updates as you type, no button click needed
- **6 real security criteria checked**, not just a label:
  - Minimum length (8+ characters)
  - Mixed uppercase and lowercase
  - Contains a number
  - Contains a symbol
  - Not a commonly leaked password (checked against a known weak-password list)
  - No sequential patterns (e.g. `123`, `abc`)
- **Strong password generator** — creates a random password and verifies it actually passes all 6 checks before showing it
- **Show/Hide** toggle for password visibility
- **Copy to clipboard** with one click
- **Local password vault** — save a password with a label (e.g. "Gmail"), view saved entries, click to reload, delete when no longer needed
- Full-window dashboard layout with live status cards and recommendations panel

## ⚙️ How it works

The core logic (`check_password_strength`) is fully separated from the GUI code — it takes a password string and returns a strength label, a dictionary of pass/fail criteria, and a list of specific recommendations. This means the same function could be reused in a CLI tool, tested independently, or dropped into another project without any GUI code attached.

Symbol detection and character checks use Python's built-in Unicode-aware string methods (`.isalpha()`, `.isdigit()`, `.isupper()`), so the checker works correctly on non-English characters without extra code. All checks run in a single linear pass — O(n) — using `any()` with short-circuit evaluation instead of manual loops.

## 📦 Requirements

No external libraries — runs on the Python standard library only (`tkinter`, `random`, `string`, `json`, `os`).

Requires Python 3.x with Tkinter (included by default on most systems).

## 🚀 Usage

```
python Passveyra_password_strength_analyzer.py
```

## 🗂️ Project structure

```
passveyra/
├── Passveyra_password_strength_analyzer.py     # main application
├── README.md
└── .gitignore        
```

## 🛡️ Security note

This is a portfolio/learning project, not a production password manager. Saved passwords in `passveyra_vault.json` are stored as **plain, unencrypted JSON** for simplicity — a production version would encrypt the vault file (e.g. using a master password and a proper key-derivation function) before writing it to disk. This file is excluded from version control via `.gitignore` so no real saved passwords are ever pushed to GitHub.

## 👤 Author

Built by Ansharah.

If you found this useful, consider giving it a ⭐ — it helps a lot!
