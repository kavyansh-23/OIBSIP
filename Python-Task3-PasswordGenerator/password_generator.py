import secrets
import string
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cryptographically Secure Password Generator")
        self.root.geometry("650x620")
        self.root.resizable(False, False)

        self.history = []

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Main Layout Frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title Label
        title_label = ttk.Label(main_frame, text="🔒 Password Generator", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 15))

        # Output & Strength Frame
        out_frame = ttk.LabelFrame(main_frame, text=" Generated Password ", padding=15)
        out_frame.pack(fill="x", pady=(0, 15))

        self.pwd_var = tk.StringVar(value="")
        self.pwd_entry = ttk.Entry(out_frame, textvariable=self.pwd_var, font=("Courier", 13, "bold"), state="readonly", justify="center")
        self.pwd_entry.pack(fill="x", pady=(0, 10))

        # Action Buttons under Output
        btn_box = ttk.Frame(out_frame)
        btn_box.pack(fill="x")

        gen_btn = tk.Button(btn_box, text="⚡ Generate Password", font=("Arial", 10, "bold"), bg="#2980b9", fg="white", activebackground="#3498db", activeforeground="white", command=self.generate_password)
        gen_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        copy_btn = tk.Button(btn_box, text="📋 Copy to Clipboard", font=("Arial", 10, "bold"), bg="#27ae60", fg="white", activebackground="#2ecc71", activeforeground="white", command=self.copy_to_clipboard)
        copy_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Strength Bar & Indicator
        strength_frame = ttk.Frame(out_frame)
        strength_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(strength_frame, text="Strength:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        self.strength_label = ttk.Label(strength_frame, text="N/A", font=("Arial", 10, "bold"))
        self.strength_label.pack(side="left")

        self.strength_progress = ttk.Progressbar(strength_frame, orient="horizontal", length=200, mode="determinate")
        self.strength_progress.pack(side="right", fill="x", expand=True, padx=(10, 0))

        # Configuration Criteria Frame
        criteria_frame = ttk.LabelFrame(main_frame, text=" Criteria & Controls ", padding=15)
        criteria_frame.pack(fill="x", pady=(0, 15))

        # Length Controls (Slider + Spinbox)
        len_frame = ttk.Frame(criteria_frame)
        len_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(len_frame, text="Password Length (Min 8):", font=("Arial", 10)).pack(side="left")

        self.length_var = tk.IntVar(value=16)
        self.len_spin = ttk.Spinbox(len_frame, from_=8, to=128, textvariable=self.length_var, width=5, command=self.sync_length_slider)
        self.len_spin.pack(side="right", padx=(5, 0))

        self.len_scale = ttk.Scale(len_frame, from_=8, to=64, variable=self.length_var, command=self.sync_length_spin)
        self.len_scale.pack(side="right", fill="x", expand=True, padx=10)

        # Character Types Checkboxes
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.auto_copy_var = tk.BooleanVar(value=True)

        chk_grid = ttk.Frame(criteria_frame)
        chk_grid.pack(fill="x")

        ttk.Checkbutton(chk_grid, text="Uppercase (A-Z)", variable=self.use_upper).grid(row=0, column=0, sticky="w", pady=2, padx=5)
        ttk.Checkbutton(chk_grid, text="Lowercase (a-z)", variable=self.use_lower).grid(row=0, column=1, sticky="w", pady=2, padx=5)
        ttk.Checkbutton(chk_grid, text="Numbers (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", pady=2, padx=5)
        ttk.Checkbutton(chk_grid, text="Symbols (!@#$%...)", variable=self.use_symbols).grid(row=1, column=1, sticky="w", pady=2, padx=5)
        ttk.Checkbutton(chk_grid, text="Exclude Ambiguous (0, O, 1, l, I)", variable=self.exclude_ambiguous).grid(row=2, column=0, columnspan=2, sticky="w", pady=2, padx=5)
        ttk.Checkbutton(chk_grid, text="Auto-copy password on generation", variable=self.auto_copy_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2, padx=5)

        # Session History Frame
        history_frame = ttk.LabelFrame(main_frame, text=" Session History (Last 5 - Not Saved to Disk) ", padding=10)
        history_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(history_frame, height=4, font=("Courier", 9), selectmode="single")
        self.history_listbox.pack(fill="both", expand=True)

    def sync_length_slider(self):
        try:
            val = self.length_var.get()
            if val < 8:
                self.length_var.set(8)
        except tk.TclError:
            pass

    def sync_length_spin(self, val):
        self.length_var.set(int(float(val)))

    def generate_password(self):
        try:
            length = self.length_var.get()
        except tk.TclError:
            messagebox.showerror("Input Error", "Please enter a valid length number.")
            return

        if length < 8:
            messagebox.showerror("Validation Error", "Password length must be at least 8 characters.")
            return

        pools = []
        ambiguous_chars = set("0O1lI")

        if self.use_upper.get():
            chars = set(string.ascii_uppercase)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append(list(chars))

        if self.use_lower.get():
            chars = set(string.ascii_lowercase)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append(list(chars))

        if self.use_digits.get():
            chars = set(string.digits)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append(list(chars))

        if self.use_symbols.get():
            chars = set(string.punctuation)
            if self.exclude_ambiguous.get():
                chars -= ambiguous_chars
            pools.append(list(chars))

        if len(pools) < 2:
            messagebox.showwarning("Validation Error", "Please select at least 2 character types.")
            return

        # Guarantee at least 1 character from each selected pool
        password_chars = [secrets.choice(pool) for pool in pools]

        # Combine all allowed characters for the remaining slots
        combined_pool = [c for pool in pools for c in pool]

        remaining_length = length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(combined_pool))

        # Cryptographically shuffle the characters
        secrets.SystemRandom().shuffle(password_chars)
        final_password = "".join(password_chars)

        # Update GUI
        self.pwd_var.set(final_password)
        self.update_strength(final_password, len(pools))
        self.add_to_history(final_password)

        if self.auto_copy_var.get():
            pyperclip.copy(final_password)

    def update_strength(self, pwd, pool_count):
        length = len(pwd)

        # Score calculation based on length and pool diversity
        score = (length * 4) + (pool_count * 15)

        if score < 60 or length < 10 or pool_count < 2:
            strength = "Weak"
            color = "#e74c3c"
            progress_val = 33
        elif score < 90 or length < 14:
            strength = "Medium"
            color = "#f39c12"
            progress_val = 66
        else:
            strength = "Strong"
            color = "#2ecc71"
            progress_val = 100

        self.strength_label.config(text=strength, foreground=color)
        self.strength_progress["value"] = progress_val

    def copy_to_clipboard(self):
        pwd = self.pwd_var.get()
        if pwd:
            pyperclip.copy(pwd)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "No password generated yet to copy.")

    def add_to_history(self, pwd):
        self.history.insert(0, pwd)
        if len(self.history) > 5:
            self.history.pop()

        self.history_listbox.delete(0, tk.END)
        for idx, item in enumerate(self.history, 1):
            self.history_listbox.insert(tk.END, f"{idx}. {item}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()