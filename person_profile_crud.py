import sqlite3
import re
import tkinter as tk
from tkinter import ttk, messagebox


class DatabaseManager:

    def __init__(self, db_name="profiles.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS person_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        city TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        occupation TEXT NOT NULL
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Initialization failed: {e}")

    def add_profile(self, full_name, email, phone, city, age, occupation):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO person_profiles (full_name, email, phone, city, age, occupation)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (full_name, email, phone, city, age, occupation))
                conn.commit()
                return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not insert record: {e}")
            return False

    def fetch_all_profiles(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM person_profiles")
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch records: {e}")
            return []

    def update_profile(self, profile_id, full_name, email, phone, city, age, occupation):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE person_profiles
                    SET full_name = ?, email = ?, phone = ?, city = ?, age = ?, occupation = ?
                    WHERE id = ?
                """, (full_name, email, phone, city, age, occupation, profile_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not update record: {e}")
            return False

    def delete_profile(self, profile_id):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM person_profiles WHERE id = ?", (profile_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not delete record: {e}")
            return False

    def search_profiles(self, query):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                search_term = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM person_profiles
                    WHERE full_name LIKE ? OR city LIKE ? OR occupation LIKE ?
                """, (search_term, search_term, search_term))
                return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {e}")
            return []


class PersonProfileApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Person Profile Management System")
        self.geometry("950x600")
        self.minsize(850, 500)

        self.db = DatabaseManager()

        self.selected_profile_id = None

        self.BG_COLOR = "#EAF4FB"
        self.TITLE_COLOR = "#154360"
        self.LABEL_COLOR = "#1F618D"
        self.ENTRY_BG = "#FFFFFF"

        self.ADD_COLOR = "#27AE60"
        self.UPDATE_COLOR = "#F39C12"
        self.DELETE_COLOR = "#E74C3C"
        self.CLEAR_COLOR = "#7F8C8D"
        self.BUTTON_TEXT = "white"

        self.configure(bg=self.BG_COLOR)

        self.create_styles()
        self.create_widgets()

        self.display_profiles()

    def create_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Treeview.Heading",
            background="#1F618D",
            foreground="white",
            font=("Arial", 10, "bold"),
            padding=6
        )

        self.style.configure(
            "Treeview",
            background="white",
            foreground="#212121",
            rowheight=26,
            fieldbackground="white",
            font=("Arial", 9)
        )

        self.style.map(
            "Treeview",
            background=[("selected", "#5DADE2")],
            foreground=[("selected", "white")]
        )

    def create_widgets(self):
        title_label = tk.Label(
            self,
            text="Person Profile Management System",
            font=("Arial", 18, "bold"),
            bg=self.BG_COLOR,
            fg=self.TITLE_COLOR
        )
        title_label.pack(side="top", fill="x", pady=10)

        main_frame = tk.Frame(self, bg=self.BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        left_pane = tk.LabelFrame(
            main_frame,
            text=" Profile Information ",
            font=("Arial", 11, "bold"),
            fg=self.TITLE_COLOR,
            bg="white",
            bd=2,
            relief="groove"
        )
        left_pane.pack(side="left", fill="y", padx=(0, 10), pady=5)

        fields = [
            ("Full Name:", "name_entry"),
            ("Email Address:", "email_entry"),
            ("Phone Number:", "phone_entry"),
            ("City:", "city_entry"),
            ("Age:", "age_entry"),
            ("Occupation:", "occupation_entry")
        ]

        for idx, (label_text, attr_name) in enumerate(fields):
            lbl = tk.Label(
                left_pane,
                text=label_text,
                font=("Arial", 10, "bold"),
                bg="white",
                fg=self.LABEL_COLOR
            )
            lbl.grid(row=idx, column=0, padx=10, pady=8, sticky="e")

            entry = tk.Entry(
                left_pane,
                width=26,
                font=("Arial", 10),
                bg=self.ENTRY_BG,
                fg="#212121",
                relief="solid",
                bd=1
            )
            entry.grid(row=idx, column=1, padx=(0, 10), pady=8, sticky="w")
            setattr(self, attr_name, entry)

        btn_frame = tk.Frame(left_pane, bg="white")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15, padx=10)

        add_btn = tk.Button(
            btn_frame, text="Add Profile", width=12, font=("Arial", 9, "bold"),
            bg=self.ADD_COLOR, fg=self.BUTTON_TEXT, activebackground="#1E8449",
            activeforeground="white", relief="flat", cursor="hand2", command=self.add_profile
        )
        add_btn.grid(row=0, column=0, padx=3, pady=4)

        update_btn = tk.Button(
            btn_frame, text="Update Selected", width=12, font=("Arial", 9, "bold"),
            bg=self.UPDATE_COLOR, fg=self.BUTTON_TEXT, activebackground="#D68910",
            activeforeground="white", relief="flat", cursor="hand2", command=self.update_profile
        )
        update_btn.grid(row=0, column=1, padx=3, pady=4)

        delete_btn = tk.Button(
            btn_frame, text="Delete Selected", width=12, font=("Arial", 9, "bold"),
            bg=self.DELETE_COLOR, fg=self.BUTTON_TEXT, activebackground="#C0392B",
            activeforeground="white", relief="flat", cursor="hand2", command=self.delete_profile
        )
        delete_btn.grid(row=1, column=0, padx=3, pady=4)

        clear_btn = tk.Button(
            btn_frame, text="Clear Form", width=12, font=("Arial", 9, "bold"),
            bg=self.CLEAR_COLOR, fg=self.BUTTON_TEXT, activebackground="#626567",
            activeforeground="white", relief="flat", cursor="hand2", command=self.clear_fields
        )
        clear_btn.grid(row=1, column=1, padx=3, pady=4)

        right_pane = tk.Frame(main_frame, bg=self.BG_COLOR)
        right_pane.pack(side="right", fill="both", expand=True, pady=5)

        search_frame = tk.Frame(right_pane, bg=self.BG_COLOR)
        search_frame.pack(fill="x", pady=(0, 8))

        search_lbl = tk.Label(
            search_frame, text="Search (Name, City, Occupation):",
            font=("Arial", 10, "bold"), bg=self.BG_COLOR, fg=self.LABEL_COLOR
        )
        search_lbl.pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(
            search_frame, font=("Arial", 10), bg=self.ENTRY_BG,
            fg="#212121", relief="solid", bd=1
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search_key_release)

        clear_search_btn = tk.Button(
            search_frame, text="Clear Filter", font=("Arial", 9, "bold"),
            bg=self.CLEAR_COLOR, fg=self.BUTTON_TEXT, activebackground="#626567",
            activeforeground="white", relief="flat", cursor="hand2", command=self.clear_search
        )
        clear_search_btn.pack(side="right")

        tree_container = tk.Frame(right_pane)
        tree_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        columns = ("ID", "Full Name", "Email", "Phone", "City", "Age", "Occupation")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.config(command=self.tree.yview)

        col_widths = {
            "ID": 40, "Full Name": 120, "Email": 130,
            "Phone": 90, "City": 80, "Age": 45, "Occupation": 100
        }

        for col in columns:
            self.tree.heading(col, text=col)
            align = "center" if col in ("ID", "Age", "Phone") else "w"
            self.tree.column(col, width=col_widths[col], anchor=align)

        self.tree.tag_configure("evenrow", background="#F4F9FC")
        self.tree.tag_configure("oddrow", background="#FFFFFF")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.select_profile)

    def validate_inputs(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        city = self.city_entry.get().strip()
        age_raw = self.age_entry.get().strip()
        occupation = self.occupation_entry.get().strip()

        if not all([name, email, phone, city, age_raw, occupation]):
            messagebox.showwarning("Validation Error", "All input fields are required.")
            return False, None

        try:
            age = int(age_raw)
            if age < 1 or age > 120:
                messagebox.showerror("Validation Error", "Age must be a positive integer between 1 and 120.")
                return False, None
        except ValueError:
            messagebox.showerror("Validation Error", "Age must be a valid numeric integer.")
            return False, None

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            messagebox.showerror("Validation Error", "Please enter a valid email address (e.g., user@domain.com).")
            return False, None

        return True, (name, email, phone, city, age, occupation)

    def display_profiles(self, records=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if records is None:
            records = self.db.fetch_all_profiles()

        for idx, row in enumerate(records):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=row, tags=(tag,))

    def add_profile(self):
        is_valid, data = self.validate_inputs()
        if not is_valid:
            return

        if self.db.add_profile(*data):
            messagebox.showinfo("Success", "Profile added successfully.")
            self.clear_fields()
            self.display_profiles()

    def update_profile(self):
        if not self.selected_profile_id:
            messagebox.showwarning("Warning", "Please select a profile from the table to update.")
            return

        is_valid, data = self.validate_inputs()
        if not is_valid:
            return

        if self.db.update_profile(self.selected_profile_id, *data):
            messagebox.showinfo("Success", "Profile updated successfully.")
            self.clear_fields()
            self.display_profiles()

    def delete_profile(self):
        if not self.selected_profile_id:
            messagebox.showwarning("Warning", "Please select a profile from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected profile?")
        if confirm:
            if self.db.delete_profile(self.selected_profile_id):
                messagebox.showinfo("Success", "Profile deleted successfully.")
                self.clear_fields()
                self.display_profiles()

    def select_profile(self, event):
        selected = self.tree.selection()
        if selected:
            row = self.tree.item(selected[0])["values"]
            self.selected_profile_id = row[0]

            self.clear_fields(keep_selection=True)

            self.name_entry.insert(0, row[1])
            self.email_entry.insert(0, row[2])
            self.phone_entry.insert(0, row[3])
            self.city_entry.insert(0, row[4])
            self.age_entry.insert(0, row[5])
            self.occupation_entry.insert(0, row[6])

    def clear_fields(self, keep_selection=False):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.city_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.occupation_entry.delete(0, tk.END)

        if not keep_selection:
            self.selected_profile_id = None
            if self.tree.selection():
                self.tree.selection_remove(self.tree.selection())

    def on_search_key_release(self, event):
        query = self.search_entry.get().strip()
        if query:
            filtered_data = self.db.search_profiles(query)
            self.display_profiles(filtered_data)
        else:
            self.display_profiles()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.display_profiles()


if __name__ == "__main__":
    app = PersonProfileApp()
    app.mainloop()
