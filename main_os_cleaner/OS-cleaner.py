import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# === Funkcje pomocnicze ===
def is_spam_name(filename: str) -> bool:
    """Wykrywa pliki o losowych nazwach typu 'fdasmulvioiua'."""
    name, _ = os.path.splitext(filename)
    if len(name) > 8 and re.fullmatch(r'[a-zA-Z0-9]+', name):
        keywords = ["projekt", "raport", "dokument", "zdjecie", "photo", "plik", "test", "data"]
        if not any(k in name.lower() for k in keywords):
            return True
    return False


def os_cleaner_gui(start_path: str, target_path: str, log_box: tk.Text, delete_spam: bool, progress_bar: ttk.Progressbar, progress_label: tk.Label):
    if not os.path.exists(start_path):
        messagebox.showerror("Błąd", "Folder źródłowy nie istnieje!")
        return
    if not os.path.exists(target_path):
        os.makedirs(target_path)
        log_box.insert(tk.END, f"📁 Utworzono folder docelowy: {target_path}\n")

    # Zlicz wszystkie pliki
    all_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            all_files.append(os.path.join(root, file))
    total = len(all_files)
    if total == 0:
        messagebox.showinfo("Info", "Brak plików w wybranym folderze.")
        return

    removed = 0
    moved = 0
    suspected_spam = []

    # Czyszczenie
    for i, full_path in enumerate(all_files, start=1):
        file = os.path.basename(full_path)
        try:
            if os.path.getsize(full_path) == 0:
                os.remove(full_path)
                removed += 1
                log_box.insert(tk.END, f"🗑️ Usunięto pusty: {file}\n")
            elif is_spam_name(file):
                suspected_spam.append(full_path)
            else:
                shutil.move(full_path, os.path.join(target_path, file))
                moved += 1
                log_box.insert(tk.END, f"📦 Przeniesiono: {file}\n")
        except Exception as e:
            log_box.insert(tk.END, f"⚠️ Błąd przy {file}: {e}\n")

    # Obsługa spamowych plików
    if suspected_spam:
        log_box.insert(tk.END, "\n⚠️ Wykryto pliki spam:\n")
        for s in suspected_spam:
            log_box.insert(tk.END, f"  {s}\n")

        if delete_spam:
            if messagebox.askyesno("Potwierdzenie", "Czy chcesz usunąć pliki spam?"):
                for p in suspected_spam:
                    try:
                        os.remove(p)
                        removed += 1
                    except Exception as e:
                        log_box.insert(tk.END, f"❌ Błąd przy usuwaniu {p}: {e}\n")
                log_box.insert(tk.END, f"🧹 Usunięto {len(suspected_spam)} plików spam.\n")
            else:
                log_box.insert(tk.END, "🚫 Pominięto usuwanie plików spam.\n")
        else:
            log_box.insert(tk.END, "⚙️ Usuwanie plików spam jest WYŁĄCZONE.\n")

    log_box.insert(tk.END, f"\n✅ Zakończono!\nUsunięto: {removed} | Przeniesiono: {moved}\n")
    progress_bar["value"] = 100
    progress_label.config(text=f"Postęp: 100% ({total}/{total})")
    log_box.see(tk.END)


# === GUI ===
def choose_start():
    folder = filedialog.askdirectory(title="Wybierz folder do przeskanowania")
    if folder:
        entry_start.delete(0, tk.END)
        entry_start.insert(0, folder)

def choose_target():
    folder = filedialog.askdirectory(title="Wybierz folder docelowy")
    if folder:
        entry_target.delete(0, tk.END)
        entry_target.insert(0, folder)

def run_cleaner():
    log_box.delete(1.0, tk.END)
    start_path = entry_start.get().strip()
    target_path = entry_target.get().strip()
    delete_spam = spam_var.get()
    os_cleaner_gui(start_path, target_path, log_box, delete_spam, progress_bar, progress_label)

root = tk.Tk()
root.title("🧹 OS Cleaner GUI")
root.geometry("700x600")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# Folder źródłowy
tk.Label(frame, text="Folder do przeskanowania:").grid(row=0, column=0, sticky="w")
entry_start = tk.Entry(frame, width=50)
entry_start.grid(row=0, column=1)
tk.Button(frame, text="Wybierz", command=choose_start).grid(row=0, column=2, padx=5)

# Folder docelowy
tk.Label(frame, text="Folder docelowy:").grid(row=1, column=0, sticky="w", pady=(10, 0))
entry_target = tk.Entry(frame, width=50)
entry_target.grid(row=1, column=1, pady=(10, 0))
tk.Button(frame, text="Wybierz", command=choose_target).grid(row=1, column=2, padx=5, pady=(10, 0))

# Checkbox spam
spam_var = tk.BooleanVar(value=True)
tk.Checkbutton(frame, text="Usuwaj pliki spam (losowe nazwy)", variable=spam_var).grid(
    row=2, column=0, columnspan=3, sticky="w", pady=(10, 5)
)

# Pasek postępu
progress_label = tk.Label(frame, text="Postęp: 0%")
progress_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=(5, 0))
progress_bar = ttk.Progressbar(frame, length=600, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, pady=(0, 10))

# Przycisk start
tk.Button(frame, text="Uruchom czyszczenie", command=run_cleaner, bg="#3CB371", fg="white").grid(
    row=5, column=0, columnspan=3, pady=10
)

# Log
log_box = scrolledtext.ScrolledText(frame, width=80, height=20)
log_box.grid(row=6, column=0, columnspan=3)

root.mainloop()
