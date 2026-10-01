"""
BMI Calculator - Advanced Tier
================================
Features:
    - GUI (Tkinter)
    - Multi-user support
    - SQLite database storage
    - BMI trend graph (matplotlib)
    - Color-coded results
    - Input validation
    - Error handling
    - Delete records (single / all / by user)
"""

import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ==================================================
# CONFIG
# ==================================================

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bmi_data.db")


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def init_db():
    """Create database and tables if not exists."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("[DB] Database initialized")
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        messagebox.showerror("Database Error", f"Could not initialize database:\n{e}")


def save_record(user_name, weight, height, bmi, category):
    """Save a BMI record to database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO bmi_records (user_name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_name, weight, height, bmi, category, date))
        conn.commit()
        conn.close()
        print(f"[DB] Record saved for {user_name}")
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        messagebox.showerror("Database Error", f"Could not save record:\n{e}")
        return False


def get_users():
    """Get list of unique users."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user_name FROM bmi_records ORDER BY user_name")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return []


def get_user_records(user_name):
    """Get all records for a user (for graph)."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bmi, date FROM bmi_records
            WHERE user_name = ?
            ORDER BY date ASC
        """, (user_name,))
        records = cursor.fetchall()
        conn.close()
        return records
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return []


def delete_record(record_id):
    """Delete a single record by id."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        messagebox.showerror("Database Error", f"Could not delete record:\n{e}")
        return False


def delete_all_user_records(user_name):
    """Delete all records for a user."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bmi_records WHERE user_name = ?", (user_name,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        messagebox.showerror("Database Error", f"Could not delete records:\n{e}")
        return False


def delete_all_records():
    """Delete all records from database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bmi_records")
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        messagebox.showerror("Database Error", f"Could not delete records:\n{e}")
        return False


def get_all_records():
    """Get all records with ids."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_name, weight, height, bmi, category, date
            FROM bmi_records ORDER BY date DESC
        """)
        records = cursor.fetchall()
        conn.close()
        return records
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return []


# ==================================================
# BMI CALCULATION
# ==================================================

def calculate_bmi(weight, height):
    """Calculate BMI = weight / (height^2)."""
    return weight / (height ** 2)


def classify_bmi(bmi):
    """Return category and color based on BMI value."""
    if bmi < 18.5:
        return "Underweight", "#3498db"
    elif 18.5 <= bmi < 25:
        return "Normal", "#2ecc71"
    elif 25 <= bmi < 30:
        return "Overweight", "#f39c12"
    else:
        return "Obese", "#e74c3c"


# ==================================================
# GUI APPLICATION
# ==================================================

class BMICalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator - Advanced")
        self.root.geometry("950x750")
        self.root.minsize(850, 650)
        self.root.configure(bg="#1e1e2e")

        self.build_ui()
        self.refresh_users()

    # ----------------------------------------------
    # BUILD UI
    # ----------------------------------------------

    def build_ui(self):
        # ---------- HEADER ----------
        header = tk.Label(
            self.root,
            text="BMI Calculator",
            font=("Segoe UI", 24, "bold"),
            bg="#1e1e2e",
            fg="#89b4fa",
            pady=15,
        )
        header.pack()

        subtitle = tk.Label(
            self.root,
            text="Body Mass Index • Multi-User • Trend Graph",
            font=("Segoe UI", 11),
            bg="#1e1e2e",
            fg="#a6adc8",
        )
        subtitle.pack()

        # ---------- MAIN FRAME ----------
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # ---------- LEFT FRAME (INPUT) ----------
        left_frame = tk.Frame(main_frame, bg="#181825", padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # User Name
        tk.Label(
            left_frame, text="User Name", font=("Segoe UI", 11, "bold"),
            bg="#181825", fg="#cdd6f4", anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))

        self.user_entry = tk.Entry(
            left_frame, font=("Segoe UI", 12),
            bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
            relief=tk.FLAT, bd=0,
        )
        self.user_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))

        # Weight
        tk.Label(
            left_frame, text="Weight (kg)", font=("Segoe UI", 11, "bold"),
            bg="#181825", fg="#cdd6f4", anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))

        self.weight_entry = tk.Entry(
            left_frame, font=("Segoe UI", 12),
            bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
            relief=tk.FLAT, bd=0,
        )
        self.weight_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))

        # Height
        tk.Label(
            left_frame, text="Height (m)", font=("Segoe UI", 11, "bold"),
            bg="#181825", fg="#cdd6f4", anchor="w",
        ).pack(fill=tk.X, pady=(0, 5))

        self.height_entry = tk.Entry(
            left_frame, font=("Segoe UI", 12),
            bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
            relief=tk.FLAT, bd=0,
        )
        self.height_entry.pack(fill=tk.X, ipady=8, pady=(0, 20))

        # Calculate button
        calc_btn = tk.Button(
            left_frame, text="Calculate BMI",
            font=("Segoe UI", 12, "bold"),
            bg="#89b4fa", fg="#1e1e2e",
            activebackground="#74a8e0",
            relief=tk.FLAT, cursor="hand2", pady=10,
            command=self.calculate,
        )
        calc_btn.pack(fill=tk.X, pady=(0, 10))

        # Clear button
        clear_btn = tk.Button(
            left_frame, text="Clear",
            font=("Segoe UI", 11),
            bg="#45475a", fg="#cdd6f4",
            activebackground="#585b70",
            relief=tk.FLAT, cursor="hand2", pady=8,
            command=self.clear_form,
        )
        clear_btn.pack(fill=tk.X)

        # ---------- RIGHT FRAME (RESULT) ----------
        right_frame = tk.Frame(main_frame, bg="#181825", padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Result title
        tk.Label(
            right_frame, text="Your Result", font=("Segoe UI", 14, "bold"),
            bg="#181825", fg="#cdd6f4",
        ).pack(pady=(0, 15))

        # Result value
        self.result_label = tk.Label(
            right_frame, text="—",
            font=("Segoe UI", 36, "bold"),
            bg="#181825", fg="#6c7086",
        )
        self.result_label.pack(pady=10)

        # Category
        self.category_label = tk.Label(
            right_frame, text="Enter details to calculate",
            font=("Segoe UI", 14),
            bg="#181825", fg="#6c7086",
        )
        self.category_label.pack(pady=5)

        # Saved Users label
        tk.Label(
            right_frame, text="Saved Users", font=("Segoe UI", 12, "bold"),
            bg="#181825", fg="#cdd6f4",
        ).pack(pady=(30, 5), anchor="w")

        # Users listbox
        self.users_listbox = tk.Listbox(
            right_frame, font=("Segoe UI", 11),
            bg="#313244", fg="#cdd6f4",
            selectbackground="#89b4fa", selectforeground="#1e1e2e",
            relief=tk.FLAT, bd=0, height=5,
        )
        self.users_listbox.pack(fill=tk.X, pady=(0, 10))
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_select)

        # Show graph button
        graph_btn = tk.Button(
            right_frame, text="Show Trend Graph",
            font=("Segoe UI", 11, "bold"),
            bg="#a6e3a1", fg="#1e1e2e",
            activebackground="#94d18f",
            relief=tk.FLAT, cursor="hand2", pady=8,
            command=self.show_graph,
        )
        graph_btn.pack(fill=tk.X, pady=(0, 6))

        # View all records button
        all_btn = tk.Button(
            right_frame, text="View / Delete Records",
            font=("Segoe UI", 11, "bold"),
            bg="#f9e2af", fg="#1e1e2e",
            activebackground="#e8d09c",
            relief=tk.FLAT, cursor="hand2", pady=8,
            command=self.view_all_records,
        )
        all_btn.pack(fill=tk.X, pady=(0, 6))

        # Delete user records button
        del_btn = tk.Button(
            right_frame, text="Delete User Records",
            font=("Segoe UI", 11, "bold"),
            bg="#f38ba8", fg="#1e1e2e",
            activebackground="#e07a98",
            relief=tk.FLAT, cursor="hand2", pady=8,
            command=self.delete_user_records,
        )
        del_btn.pack(fill=tk.X)

    # ----------------------------------------------
    # CALCULATE BMI
    # ----------------------------------------------

    def calculate(self):
        user = self.user_entry.get().strip()
        weight_str = self.weight_entry.get().strip()
        height_str = self.height_entry.get().strip()

        # Validation
        if not user:
            messagebox.showerror("Error", "Please enter user name.")
            return

        if not weight_str or not height_str:
            messagebox.showerror("Error", "Please enter weight and height.")
            return

        try:
            weight = float(weight_str)
            height = float(height_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return

        if weight <= 0 or height <= 0:
            messagebox.showerror("Error", "Weight and height must be positive.")
            return

        if weight > 500:
            messagebox.showerror("Error", "Weight seems too high (max 500 kg).")
            return

        if height > 3:
            messagebox.showerror("Error", "Height seems too high (max 3 m).")
            return

        # Calculate
        bmi = calculate_bmi(weight, height)
        category, color = classify_bmi(bmi)

        # Display
        self.result_label.config(text=f"{bmi:.2f}", fg=color)
        self.category_label.config(text=category, fg=color)

        # Save
        success = save_record(user, weight, height, bmi, category)

        if success:
            self.refresh_users()
            messagebox.showinfo("Saved", f"Record saved for {user}.\n\nBMI: {bmi:.2f}\nCategory: {category}")

    # ----------------------------------------------
    # CLEAR FORM
    # ----------------------------------------------

    def clear_form(self):
        self.user_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.result_label.config(text="—", fg="#6c7086")
        self.category_label.config(text="Enter details to calculate", fg="#6c7086")

    # ----------------------------------------------
    # REFRESH USERS
    # ----------------------------------------------

    def refresh_users(self):
        self.users_listbox.delete(0, tk.END)
        users = get_users()
        for user in users:
            self.users_listbox.insert(tk.END, user)

    def on_user_select(self, event):
        selection = self.users_listbox.curselection()
        if selection:
            user = self.users_listbox.get(selection[0])
            self.user_entry.delete(0, tk.END)
            self.user_entry.insert(0, user)

    # ----------------------------------------------
    # SHOW GRAPH (works with 1+ records)
    # ----------------------------------------------

    def show_graph(self):
        user = self.user_entry.get().strip()

        if not user:
            messagebox.showerror("Error", "Please enter user name first.")
            return

        records = get_user_records(user)

        if not records:
            messagebox.showinfo("No Data", f"No records found for {user}.")
            return

        bmis = [r[0] for r in records]
        dates = [r[1] for r in records]

        # Create graph window
        graph_win = tk.Toplevel(self.root)
        graph_win.title(f"BMI Trend - {user}")
        graph_win.geometry("950x600")
        graph_win.configure(bg="#1e1e2e")

        # Title
        tk.Label(
            graph_win, text=f"BMI Trend for {user}",
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e2e", fg="#89b4fa", pady=10,
        ).pack()

        # Info label
        info_text = f"Total records: {len(records)}"
        if len(records) < 2:
            info_text += "  •  Add more records to see a trend line"
        tk.Label(
            graph_win, text=info_text,
            font=("Segoe UI", 10),
            bg="#1e1e2e", fg="#a6adc8",
        ).pack()

        # Matplotlib figure
        fig, ax = plt.subplots(figsize=(9, 5), facecolor="#1e1e2e")
        ax.set_facecolor("#181825")

        x_positions = list(range(len(bmis)))

        if len(bmis) == 1:
            ax.scatter(x_positions, bmis, color="#89b4fa", s=200,
                       zorder=5, label=f"{user}'s BMI")
        else:
            ax.plot(x_positions, bmis, marker="o", color="#89b4fa",
                    linewidth=2, markersize=12, zorder=5,
                    label=f"{user}'s BMI")
            ax.fill_between(x_positions, bmis, alpha=0.2, color="#89b4fa")

        # Category reference lines
        ax.axhline(y=18.5, color="#3498db", linestyle="--", alpha=0.6,
                   linewidth=1.5, label="Underweight limit (18.5)")
        ax.axhline(y=25, color="#2ecc71", linestyle="--", alpha=0.6,
                   linewidth=1.5, label="Normal limit (25)")
        ax.axhline(y=30, color="#e74c3c", linestyle="--", alpha=0.6,
                   linewidth=1.5, label="Obese limit (30)")

        # Labels
        ax.set_xlabel("Record Number", color="#cdd6f4", fontsize=11)
        ax.set_ylabel("BMI", color="#cdd6f4", fontsize=11)
        ax.set_xticks(x_positions)

        # X-axis labels
        x_labels = []
        for d in dates:
            try:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
                x_labels.append(dt.strftime("%d-%m %H:%M"))
            except Exception:
                x_labels.append(d[:10])
        ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=9)

        # Style
        ax.tick_params(colors="#cdd6f4")
        ax.legend(facecolor="#313244", edgecolor="#45475a",
                  labelcolor="#cdd6f4", loc="best", fontsize=9)
        ax.grid(True, alpha=0.2, color="#45475a")

        for spine in ax.spines.values():
            spine.set_color("#45475a")

        plt.tight_layout()

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Close button
        close_btn = tk.Button(
            graph_win, text="Close",
            font=("Segoe UI", 11, "bold"),
            bg="#f38ba8", fg="#1e1e2e",
            activebackground="#e07a98",
            relief=tk.FLAT, cursor="hand2", padx=30, pady=8,
            command=graph_win.destroy,
        )
        close_btn.pack(pady=10)

    # ----------------------------------------------
    # VIEW ALL RECORDS (with Delete)
    # ----------------------------------------------

    def view_all_records(self):
        records = get_all_records()

        if not records:
            messagebox.showinfo("No Records", "No records found.")
            return

        # Create records window
        rec_win = tk.Toplevel(self.root)
        rec_win.title("All BMI Records")
        rec_win.geometry("1050x620")
        rec_win.configure(bg="#1e1e2e")

        tk.Label(
            rec_win, text="All BMI Records",
            font=("Segoe UI", 16, "bold"),
            bg="#1e1e2e", fg="#89b4fa", pady=10,
        ).pack()

        tk.Label(
            rec_win,
            text="Select a row and click 'Delete Selected' to remove it.",
            font=("Segoe UI", 10),
            bg="#1e1e2e", fg="#a6adc8",
        ).pack()

        # Table frame
        table_frame = tk.Frame(rec_win, bg="#1e1e2e")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        columns = ("ID", "User", "Weight (kg)", "Height (m)", "BMI", "Category", "Date")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        widths = {"ID": 50, "User": 130, "Weight (kg)": 100, "Height (m)": 100,
                  "BMI": 80, "Category": 120, "Date": 180}
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 120), anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Insert records
        for rec in records:
            tree.insert("", tk.END, values=(
                rec[0],
                rec[1],
                f"{rec[2]:.1f}",
                f"{rec[3]:.2f}",
                f"{rec[4]:.2f}",
                rec[5],
                rec[6],
            ))

        # ---------- BUTTON ROW ----------
        btn_row = tk.Frame(rec_win, bg="#1e1e2e")
        btn_row.pack(pady=10)

        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a row to delete.")
                return

            item = tree.item(selected[0])
            values = item["values"]
            record_id = values[0]
            user = values[1]

            if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete this record?\n\nUser: {user}\nBMI: {values[4]}\nDate: {values[6]}"
            ):
                return

            if delete_record(record_id):
                tree.delete(selected[0])
                self.refresh_users()
                messagebox.showinfo("Deleted", "Record deleted successfully.")

        def delete_all():
            if not messagebox.askyesno(
                "Confirm Delete All",
                "Delete ALL records for ALL users?\n\nThis cannot be undone!"
            ):
                return

            if delete_all_records():
                for item in tree.get_children():
                    tree.delete(item)
                self.refresh_users()
                messagebox.showinfo("Deleted", "All records deleted.")

        del_btn = tk.Button(
            btn_row, text="Delete Selected",
            font=("Segoe UI", 11, "bold"),
            bg="#f38ba8", fg="#1e1e2e",
            activebackground="#e07a98",
            relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
            command=delete_selected,
        )
        del_btn.pack(side=tk.LEFT, padx=5)

        del_all_btn = tk.Button(
            btn_row, text="Delete All",
            font=("Segoe UI", 11, "bold"),
            bg="#e74c3c", fg="#ffffff",
            activebackground="#c0392b",
            relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
            command=delete_all,
        )
        del_all_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(
            btn_row, text="Close",
            font=("Segoe UI", 11, "bold"),
            bg="#89b4fa", fg="#1e1e2e",
            activebackground="#74a8e0",
            relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
            command=rec_win.destroy,
        )
        close_btn.pack(side=tk.LEFT, padx=5)

    # ----------------------------------------------
    # DELETE USER RECORDS (from main window)
    # ----------------------------------------------

    def delete_user_records(self):
        user = self.user_entry.get().strip()

        if not user:
            messagebox.showerror("Error", "Please enter user name first.")
            return

        records = get_user_records(user)

        if not records:
            messagebox.showinfo("No Data", f"No records found for {user}.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete ALL {len(records)} records for {user}?\n\nThis cannot be undone!"
        ):
            return

        if delete_all_user_records(user):
            self.refresh_users()
            self.clear_form()
            messagebox.showinfo("Deleted", f"All records deleted for {user}.")


# ==================================================
# MAIN
# ==================================================

def main():
    init_db()
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()