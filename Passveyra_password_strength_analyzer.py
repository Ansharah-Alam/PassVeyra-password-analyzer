"""PassVeyra — Password Strength Analyzer
A Tkinter dashboard that checks password strength live, generates
strong passwords, and lets you save passwords locally with a label. Saved passwords are stored in passveyra_vault.json."""

import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import string
import json
import os

VAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passveyra_vault.json")

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "letmein",
    "admin", "welcome", "password1", "iloveyou", "abc123",
    "monkey", "dragon", "111111", "123123", "football","pass1234",
    "1q2w3e4r", "sunshine", "princess", "qwertyuiop", "654321"
}


def has_sequential_pattern(password, run_length=3):
    lower = password.lower()
    for i in range(len(lower) - run_length + 1):
        chunk = lower[i:i + run_length]
        if all(ord(chunk[j + 1]) - ord(chunk[j]) == 1 for j in range(len(chunk) - 1)):
            return True
    return False


def check_password_strength(password):
    criteria = {
        "Length \u2265 8": len(password) >= 8,
        "Upper + lower case": (
            any(c.isupper() for c in password) and any(c.islower() for c in password)
        ),
        "Has a number": any(c.isdigit() for c in password),
        "Has a symbol": any(not c.isalnum() for c in password),
        "Not commonly leaked": password.lower() not in COMMON_PASSWORDS,
        "No sequences (123/abc)": not has_sequential_pattern(password),
    }

    recommendations = []
    if not criteria["Length \u2265 8"]:
        recommendations.append("Use at least 8 characters.")
    if not criteria["Upper + lower case"]:
        recommendations.append("Use a mix of uppercase and lowercase letters.")
    if not criteria["Has a number"]:
        recommendations.append("Add at least one number.")
    if not criteria["Has a symbol"]:
        recommendations.append("Add at least one symbol (e.g. !, @, #, $, %, ^, &, *).")
    if not criteria["Not commonly leaked"]:
        recommendations.append("This password is commonly leaked \u2014 avoid it.")
    if not criteria["No sequences (123/abc)"]:
        recommendations.append("Avoid common sequences like '123' or 'abc'.")
    if not recommendations:
        recommendations.append("All checks passed. Password looks strong!.")

    passed = sum(criteria.values())
    total = len(criteria)

    if not criteria["Length \u2265 8"] or not criteria["Not commonly leaked"]:
        strength = "Weak"
    elif passed == total:
        strength = "Strong"
    elif passed >= total - 2:
        strength = "Medium"
    else:
        strength = "Weak"

    return strength, criteria, recommendations, passed, total


def generate_strong_password(length=14):
    pool = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
    while True:
        pwd = "".join(random.choice(pool) for _ in range(length))
        strength, _, _, _, _ = check_password_strength(pwd)
        if strength == "Strong":
            return pwd


def load_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_vault(entries):
    with open(VAULT_FILE, "w") as f:
        json.dump(entries, f, indent=2)


STRENGTH_COLORS = {"Weak": "#ff5c5c", "Medium": "#ffb84d", "Strong": "#3ddc84"}

BG = "#0d1117"
CARD = "#161b22"
CARD_BORDER = "#21262d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#3ddc84"

vault_entries = load_vault()
mode = {"value": "create"}  # "create" or "generate"


def refresh(*_):
    password = entry.get()
    strength, criteria, recommendations, passed, total = check_password_strength(password)

    score_label.config(text=f"{passed}/{total}", fg=STRENGTH_COLORS[strength])
    strength_label.config(text=strength.upper(), fg=STRENGTH_COLORS[strength])

    for name, card in criterion_cards.items():
        ok = criteria[name]
        dot, lbl = card
        dot.config(fg=STRENGTH_COLORS["Strong"] if ok else "#484f58")
        lbl.config(fg=TEXT if ok else MUTED)

    rec_text.config(state="normal")
    rec_text.delete("1.0", tk.END)
    for msg in recommendations:
        rec_text.insert(tk.END, f"\u2192 {msg}\n")
    rec_text.config(state="disabled")


def toggle_visibility():
    if entry.cget("show") == "*":
        entry.config(show="")
        toggle_btn.config(text="Hide")
    else:
        entry.config(show="*")
        toggle_btn.config(text="Show")


def set_mode(new_mode):
    mode["value"] = new_mode
    if new_mode == "create":
        create_btn.config(bg=ACCENT, fg="#0d1117")
        generate_btn.config(bg=CARD, fg=TEXT)
        entry.delete(0, tk.END)
    else:
        generate_btn.config(bg=ACCENT, fg="#0d1117")
        create_btn.config(bg=CARD, fg=TEXT)
        pwd = generate_strong_password()
        entry.config(show="")
        toggle_btn.config(text="Hide")
        entry.delete(0, tk.END)
        entry.insert(0, pwd)
    refresh()


def on_copy():
    password = entry.get()
    if not password:
        return
    root.clipboard_clear()
    root.clipboard_append(password)
    copy_btn.config(text="Copied!")
    root.after(1500, lambda: copy_btn.config(text="Copy"))


def refresh_vault_list():
    vault_list.delete(0, tk.END)
    for item in vault_entries:
        vault_list.insert(tk.END, f"  {item['label']}   \u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022")


def on_save():
    password = entry.get()
    if not password:
        messagebox.showinfo("PassVeyra", "Enter or generate a password first.")
        return
    label = simpledialog.askstring("Save Password", "Label this password (e.g. 'Gmail', 'University Portal'):")
    if not label:
        return
    vault_entries.append({"label": label, "password": password})
    save_vault(vault_entries)
    refresh_vault_list()


def on_vault_select(_event):
    selection = vault_list.curselection()
    if not selection:
        return
    item = vault_entries[selection[0]]
    entry.delete(0, tk.END)
    entry.insert(0, item["password"])
    entry.config(show="")
    toggle_btn.config(text="Hide")
    refresh()


def on_delete_selected():
    selection = vault_list.curselection()
    if not selection:
        return
    del vault_entries[selection[0]]
    save_vault(vault_entries)
    refresh_vault_list()


def on_exit():
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PassVeyra Dashboard")
    root.geometry("1000x800")
    root.state("zoomed")  
    root.resizable(True, True)
    root.configure(bg=BG)

    # ---- Top bar ----
    topbar = tk.Frame(root, bg=BG)
    topbar.pack(fill="x", padx=28, pady=(22, 14))

    tk.Label(topbar, text="PassVeyra", font=("Segoe UI", 18, "bold"), fg=ACCENT, bg=BG).pack(side="left")
    tk.Label(topbar, text="Password Strength Analyzer", font=("Segoe UI", 9), fg=MUTED, bg=BG).pack(side="left", padx=(10, 0), pady=(4, 0))

    exit_btn = tk.Button(topbar, text="Exit", command=on_exit, bg=CARD, fg="#ff5c5c", relief="flat", padx=12, bd=0)
    exit_btn.pack(side="right")

    # ---- Mode switch ----
    mode_row = tk.Frame(root, bg=BG)
    mode_row.pack(fill="x", padx=28, pady=(0, 12))

    create_btn = tk.Button(mode_row, text="Create Your Own", command=lambda: set_mode("create"),
                            bg=ACCENT, fg="#0d1117", font=("Segoe UI", 9, "bold"), relief="flat", padx=14, pady=6, bd=0)
    create_btn.pack(side="left", padx=(0, 8))

    generate_btn = tk.Button(mode_row, text="Generate Strong Password", command=lambda: set_mode("generate"),
                            bg=CARD, fg=TEXT, font=("Segoe UI", 9, "bold"), relief="flat", padx=14, pady=6, bd=0)
    generate_btn.pack(side="left")

    # ---- Score summary card ----
    summary = tk.Frame(root, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
    summary.pack(fill="x", padx=28, pady=(0, 16))

    summary_inner = tk.Frame(summary, bg=CARD)
    summary_inner.pack(fill="x", padx=20, pady=16)

    left_summary = tk.Frame(summary_inner, bg=CARD)
    left_summary.pack(side="left")
    tk.Label(left_summary, text="OVERALL STRENGTH", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="w")
    strength_label = tk.Label(left_summary, text="\u2014", font=("Segoe UI", 20, "bold"), fg=TEXT, bg=CARD)
    strength_label.pack(anchor="w")

    right_summary = tk.Frame(summary_inner, bg=CARD)
    right_summary.pack(side="right")
    tk.Label(right_summary, text="CRITERIA PASSED", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=CARD).pack(anchor="e")
    score_label = tk.Label(right_summary, text="0/6", font=("Segoe UI", 20, "bold"), fg=TEXT, bg=CARD)
    score_label.pack(anchor="e")

    # ---- Input row ----
    input_row = tk.Frame(root, bg=BG)
    input_row.pack(fill="x", padx=28, pady=(0, 8))

    entry = tk.Entry(input_row, show="*", font=("Segoe UI", 12), bg=CARD, fg=TEXT,
                    insertbackground=TEXT, relief="flat", highlightbackground=CARD_BORDER,
                    highlightthickness=1)
    entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
    entry.bind("<KeyRelease>", refresh)

    toggle_btn = tk.Button(input_row, text="Show", command=toggle_visibility, bg=CARD, fg=TEXT, relief="flat", padx=10, bd=0)
    toggle_btn.pack(side="left", padx=(0, 8))

    copy_btn = tk.Button(input_row, text="Copy", command=on_copy, bg=CARD, fg=TEXT, relief="flat", padx=10, bd=0)
    copy_btn.pack(side="left")

    # ---- Save row ----
    save_row = tk.Frame(root, bg=BG)
    save_row.pack(fill="x", padx=28, pady=(0, 20))

    save_btn = tk.Button(save_row, text="Save to Vault", command=on_save, bg=ACCENT, fg="#0d1117",
                        font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6, bd=0)
    save_btn.pack(side="left")

    # ---- Criteria grid (2 columns of cards) ----
    grid = tk.Frame(root, bg=BG)
    grid.pack(fill="x", padx=28)

    criterion_names = [
        "Length \u2265 8", "Upper + lower case", "Has a number",
        "Has a symbol", "Not commonly leaked", "No sequences (123/abc)",
    ]

    criterion_cards = {}
    for i, name in enumerate(criterion_names):
        row, col = divmod(i, 2)
        cell = tk.Frame(grid, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
        cell.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 6, 6 if col == 0 else 0), pady=6)
        grid.grid_columnconfigure(col, weight=1)

        inner = tk.Frame(cell, bg=CARD)
        inner.pack(fill="x", padx=14, pady=10)
        dot = tk.Label(inner, text="\u25cf", font=("Segoe UI", 10), fg="#484f58", bg=CARD)
        dot.pack(side="left", padx=(0, 8))
        lbl = tk.Label(inner, text=name, font=("Segoe UI", 9), fg=MUTED, bg=CARD)
        lbl.pack(side="left")
        criterion_cards[name] = (dot, lbl)

    # ---- Suggestions panel ----
    tk.Label(root, text="RECOMMENDATIONS", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=BG).pack(anchor="w", padx=28, pady=(20, 6))

    rec_frame = tk.Frame(root, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
    rec_frame.pack(fill="x", padx=28, pady=(0, 16))

    rec_text = tk.Text(rec_frame, height=4, font=("Segoe UI", 9), bg=CARD, fg=TEXT, relief="flat",
                        wrap="word", state="disabled", highlightthickness=0, padx=14, pady=10)
    rec_text.pack(fill="x")

    # ---- Vault panel ----
    vault_header = tk.Frame(root, bg=BG)
    vault_header.pack(fill="x", padx=28, pady=(0, 6))
    tk.Label(vault_header, text="MY VAULT", font=("Segoe UI", 8, "bold"), fg=MUTED, bg=BG).pack(side="left")
    tk.Button(vault_header, text="Delete Selected", command=on_delete_selected, bg=BG, fg="#ff5c5c",
            relief="flat", bd=0, font=("Segoe UI", 8)).pack(side="right")

    vault_frame = tk.Frame(root, bg=CARD, highlightbackground=CARD_BORDER, highlightthickness=1)
    vault_frame.pack(fill="both", expand=True, padx=28, pady=(0, 12))

    vault_list = tk.Listbox(vault_frame, font=("Segoe UI", 9), bg=CARD, fg=TEXT, relief="flat",
                            highlightthickness=0, selectbackground=ACCENT, selectforeground="#0d1117",
                            activestyle="none")
    vault_list.pack(fill="both", expand=True, padx=8, pady=8)
    vault_list.bind("<<ListboxSelect>>", on_vault_select)

    footer = tk.Label(root, text="Runs 100% locally \u2014 saved in passveyra_vault.json next to this script.",
                    font=("Segoe UI", 8), fg=MUTED, bg=BG)
    footer.pack(side="bottom", pady=(0, 14))

    refresh_vault_list()
    refresh()
    root.mainloop()