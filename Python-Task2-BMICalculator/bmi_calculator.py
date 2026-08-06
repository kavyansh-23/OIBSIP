import os
import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_NAME = "bmi_data.db"

class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator & Tracker")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.init_db()

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.calc_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.calc_tab, text=" Calculate BMI ")
        self.build_calc_tab()

        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text=" History & Trends ")
        self.build_history_tab()

    def init_db(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

    def calculate_bmi(self, weight_kg, height_cm):
        # Convert height from cm to meters: height_m = height_cm / 100
        height_m = height_cm / 100.0
        return weight_kg / (height_m ** 2)

    def classify_bmi(self, bmi):
        if bmi < 18.5:
            return "Underweight", "#3498db"
        elif 18.5 <= bmi <= 24.9:
            return "Normal Weight", "#2ecc71"
        elif 25.0 <= bmi <= 29.9:
            return "Overweight", "#f39c12"
        else:
            return "Obese", "#e74c3c"

    def build_calc_tab(self):
        frame = ttk.LabelFrame(self.calc_tab, text=" User Input & Measurement ", padding=20)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="User / Profile Name:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=10)
        self.name_entry = ttk.Entry(frame, font=("Arial", 11), width=30)
        self.name_entry.grid(row=0, column=1, pady=10, padx=10)

        ttk.Label(frame, text="Weight (kg):", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=10)
        self.weight_entry = ttk.Entry(frame, font=("Arial", 11), width=30)
        self.weight_entry.grid(row=1, column=1, pady=10, padx=10)

        # Updated Label for cm
        ttk.Label(frame, text="Height (cm):", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=10)
        self.height_entry = ttk.Entry(frame, font=("Arial", 11), width=30)
        self.height_entry.grid(row=2, column=1, pady=10, padx=10)

        calc_btn = tk.Button(frame, text="Calculate & Save BMI", font=("Arial", 11, "bold"), bg="#2980b9", fg="white", activebackground="#3498db", activeforeground="white", command=self.handle_calculation)
        calc_btn.grid(row=3, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

        self.result_card = tk.Frame(frame, bg="#ecf0f1", bd=2, relief="groove")
        self.result_card.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10, ipady=15)

        self.result_label = tk.Label(self.result_card, text="Enter details and click calculate.", font=("Arial", 13, "bold"), bg="#ecf0f1", fg="#2c3e50")
        self.result_label.pack(expand=True)

    def handle_calculation(self):
        username = self.name_entry.get().strip()
        weight_str = self.weight_entry.get().strip()
        height_str = self.height_entry.get().strip()

        if not username:
            messagebox.showwarning("Input Error", "Please enter a profile name.")
            return

        try:
            weight = float(weight_str)
            height_cm = float(height_str)

            if weight <= 0 or height_cm <= 0:
                messagebox.showerror("Input Error", "Weight and Height must be positive numbers.")
                return

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for weight and height.")
            return

        bmi = self.calculate_bmi(weight, height_cm)
        category, color = self.classify_bmi(bmi)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.result_card.config(bg=color)
        self.result_label.config(
            text=f"BMI: {bmi:.2f} | Category: {category}",
            bg=color,
            fg="white"
        )

        self.save_record(username, weight, height_cm, bmi, category, timestamp)

    def save_record(self, username, weight, height, bmi, category, timestamp):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bmi_records (username, weight, height, bmi, category, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (username, weight, height, round(bmi, 2), category, timestamp)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"BMI record saved for user '{username}'.")
            self.refresh_user_dropdown()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save record: {e}")

    def build_history_tab(self):
        control_frame = ttk.Frame(self.history_tab, padding=10)
        control_frame.pack(fill="x")

        ttk.Label(control_frame, text="Select User Profile:", font=("Arial", 11)).pack(side="left", padx=5)

        self.user_dropdown = ttk.Combobox(control_frame, font=("Arial", 11), state="readonly")
        self.user_dropdown.pack(side="left", padx=5)

        view_btn = tk.Button(control_frame, text="Load Trends", font=("Arial", 10, "bold"), bg="#27ae60", fg="white", command=self.load_user_trends)
        view_btn.pack(side="left", padx=10)

        self.plot_frame = ttk.Frame(self.history_tab, padding=10)
        self.plot_frame.pack(fill="both", expand=True)

        self.refresh_user_dropdown()

    def refresh_user_dropdown(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT username FROM bmi_records")
            users = [row[0] for row in cursor.fetchall()]
            conn.close()

            self.user_dropdown["values"] = users
            if users:
                self.user_dropdown.current(0)
        except sqlite3.Error as e:
            print(f"Error fetching users: {e}")

    def load_user_trends(self):
        selected_user = self.user_dropdown.get()
        if not selected_user:
            messagebox.showwarning("Select User", "Please select a user profile to view trends.")
            return

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT bmi, timestamp FROM bmi_records WHERE username = ? ORDER BY timestamp ASC",
                (selected_user,)
            )
            records = cursor.fetchall()
            conn.close()

            if not records:
                messagebox.showinfo("No Data", f"No records found for user '{selected_user}'.")
                return

            bmis = [r[0] for r in records]
            timestamps = [r[1].split()[0] for r in records]

            fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
            ax.plot(timestamps, bmis, marker="o", color="#2980b9", linewidth=2, label="BMI")
            
            ax.axhline(18.5, color="#3498db", linestyle="--", alpha=0.7, label="Underweight (<18.5)")
            ax.axhline(24.9, color="#2ecc71", linestyle="--", alpha=0.7, label="Normal (18.5-24.9)")
            ax.axhline(29.9, color="#f39c12", linestyle="--", alpha=0.7, label="Overweight (25-29.9)")

            ax.set_title(f"BMI History for {selected_user}", fontsize=12, fontweight="bold")
            ax.set_xlabel("Date")
            ax.set_ylabel("BMI Value")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(loc="upper right", fontsize=8)
            fig.autofmt_xdate(rotation=30)

            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load records: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()
