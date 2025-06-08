import os
import shutil
import json
import subprocess
from tkinter import *
from tkinter import messagebox, simpledialog, filedialog
from time import sleep

CONFIG = "config.json"
PATCH_COUNT_FILE = "patch_count.json"
LOCK_FILE = ".patch_lock"
VIDEO_FILE = "start.mp4"
PATCH_FILE = "patch_file.txt"
PASSWORD = "6742911Aa@"

MAX_PATCHES_DEFAULT = 2
MAX_PATCHES_EXTENDED = 4

selected_program = None
selected_program_var = None
status_text = None

def play_video():
    if os.path.exists(VIDEO_FILE):
        try:
            subprocess.run(['start', VIDEO_FILE], shell=True)
            sleep(5)
        except Exception as e:
            print(f"Video error: {e}")
    else:
        messagebox.showerror("Missing Video", f"Required video file '{VIDEO_FILE}' not found.")
        exit()

def create_lock():
    with open(LOCK_FILE, 'w') as file:
        file.write("locked")

def check_lock():
    if os.path.exists(LOCK_FILE):
        if not os.path.exists(PATCH_COUNT_FILE):
            messagebox.showerror("Access Denied", "Patch data tampered. Program is blocked.")
            exit()
    else:
        with open(PATCH_COUNT_FILE, 'w') as f:
            json.dump({"patches": 0, "unlocked": False}, f)
        create_lock()

def load_patch_data():
    check_lock()
    with open(PATCH_COUNT_FILE, 'r') as file:
        return json.load(file)

def save_patch_data(data):
    with open(PATCH_COUNT_FILE, 'w') as file:
        json.dump(data, file)

def check_patch_limit():
    data = load_patch_data()
    limit = MAX_PATCHES_EXTENDED if data.get("unlocked") else MAX_PATCHES_DEFAULT

    if data["patches"] >= limit:
        if not data.get("unlocked"):
            ask_password(data)
        return data["patches"] < MAX_PATCHES_EXTENDED
    return True

def ask_password(data):
    for _ in range(2):
        pwd = simpledialog.askstring("Password Required", "Patch limit reached.\nEnter password to unlock more patches:", show='*')
        if pwd == PASSWORD:
            data["unlocked"] = True
            save_patch_data(data)
            messagebox.showinfo("Unlocked", "✅ Additional patch slots unlocked.")
            return
        else:
            messagebox.showerror("Incorrect", "❌ Incorrect password.")
    exit()

def increment_patch_count():
    data = load_patch_data()
    data["patches"] += 1
    save_patch_data(data)

def select_program():
    global selected_program
    path = filedialog.askopenfilename(title="Select an EXE program", filetypes=[("Executable Files", "*.exe")])
    if path:
        selected_program = path
        selected_program_var.set(path)
        status_text.set("✅ Program selected.")

def run_selected_program():
    if selected_program and os.path.exists(selected_program):
        try:
            subprocess.run(f'"{selected_program}"', shell=True)
            status_text.set("🚀 Program executed.")
        except Exception as e:
            status_text.set(f"Error running: {e}")
    else:
        status_text.set("❌ No valid program selected.")

def apply_patch():
    if not check_patch_limit():
        return

    if not selected_program or not os.path.exists(selected_program):
        status_text.set("❌ Select a program first.")
        return

    if not os.path.exists(PATCH_FILE):
        status_text.set("❌ Patch file not found.")
        return

    try:
        shutil.copy(PATCH_FILE, os.path.dirname(selected_program))
        increment_patch_count()
        status_text.set("✅ Patch applied successfully.")
        webbrowser.open("https://nexusgamestudio.weebly.com/")
    except Exception as e:
        status_text.set(f"Patch error: {e}")

def patch_known_games():
    if not os.path.exists(CONFIG):
        messagebox.showerror("Error", "Missing config.json file!")
        return

    with open(CONFIG, 'r') as f:
        games = json.load(f)

    for key, game in games.items():
        answer = messagebox.askyesno("Game Found", f"Do you want to scan/patch save for {game['name']}?")
        if answer:
            patch_save(game)

def patch_save(game):
    save_path = os.path.expandvars(f"%USERPROFILE%\\{game['save_dir']}")
    os.makedirs(save_path, exist_ok=True)

    saves = [f for f in os.listdir(save_path) if f.endswith(game['file_ext'])] if os.path.exists(save_path) else []

    if not saves:
        try:
            shutil.copy(game['modded_save'], os.path.join(save_path, f"Modded{game['file_ext']}"))
            messagebox.showinfo("Patched", f"No save found.\nCreated modded save for {game['name']}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy modded save: {e}")
    else:
        choice = simpledialog.askstring("Choose Save", f"Saves found: {', '.join(saves)}\nEnter save file name to patch:")
        if choice and choice in saves:
            try:
                shutil.copy(game['modded_save'], os.path.join(save_path, choice))
                messagebox.showinfo("Patched", f"{choice} patched successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to patch save: {e}")
        else:
            messagebox.showerror("Invalid", "Save file not selected or invalid.")

def create_gui():
    global selected_program_var, status_text
    root = Tk()
    root.title("Universal Game Patcher")
    root.geometry("400x360")
    root.resizable(False, False)

    selected_program_var = StringVar()
    status_text = StringVar()

    Label(root, text="Universal Game Patcher", font=("Arial", 14, "bold")).pack(pady=10)
    Button(root, text="🎮 Select Program", width=25, command=select_program).pack(pady=5)
    Button(root, text="🚀 Run Program", width=25, command=run_selected_program).pack(pady=5)
    Button(root, text="🛠 Apply EXE Patch", width=25, command=apply_patch).pack(pady=5)
    Button(root, text="💾 Patch Known Game Saves", width=25, command=patch_known_games).pack(pady=5)

    Label(root, textvariable=selected_program_var, wraplength=350, fg="blue").pack(pady=10)
    Label(root, textvariable=status_text, fg="green").pack(pady=10)
    Label(root, text="Made by Nexus Studio", fg="gray").pack(pady=10)

    play_video()
    root.mainloop()

if __name__ == "__main__":
    create_gui()
