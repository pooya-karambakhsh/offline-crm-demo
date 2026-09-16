import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import (
    insert_person, 
    update_person, 
    delete_person,
    get_all_people, 
    search_people,
    check_person_exists, 
    export_table_to_csv
)

class PersonFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_person_id = None
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.form_frame = ttk.LabelFrame(self, text="Add / Edit Person")
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()

        ttk.Label(self.form_frame, text="First Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.first_name_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Last Name").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.last_name_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Email").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.email_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Phone").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.phone_var).grid(row=3, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.grid(row=4, columnspan=2, pady=15)

        self.submit_btn = ttk.Button(btn_frame, text="Submit", command=self.submit)
        self.submit_btn.pack(side=tk.LEFT, padx=3)

        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete, state="disabled")
        self.delete_btn.pack(side=tk.LEFT, padx=3)

        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=3)

        table_frame = ttk.LabelFrame(self, text="Records")
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        columns = ("id", "first_name", "last_name", "email", "phone")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("first_name", text="First Name")
        self.tree.heading("last_name", text="Last Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")

        self.tree.column("id", width=30)
        self.tree.column("first_name", width=100)
        self.tree.column("last_name", width=100)
        self.tree.column("email", width=150)
        self.tree.column("phone", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        bottom_bar = ttk.Frame(table_frame)
        bottom_bar.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(bottom_bar, text="Export to CSV", command=self.export_csv).pack(side=tk.RIGHT)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    def on_select_row(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_person_id = values[0]

        self.first_name_var.set(values[1])
        self.last_name_var.set(values[2])
        self.email_var.set(values[3] if values[3] != "None" else "")
        self.phone_var.set(values[4] if values[4] != "None" else "")

        self.form_frame.config(text=f"Edit Person (ID: {self.selected_person_id})")
        self.submit_btn.config(text="Update")
        self.delete_btn.config(state="normal")

    def submit(self):
        first = self.first_name_var.get().strip()
        last = self.last_name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()

        if not first or not last:
            messagebox.showerror("Error", "First and Last Name are required.")
            return

        if self.selected_person_id is None:
            if check_person_exists(email):
                messagebox.showwarning("Duplicate Entry", "A person with this email already exists.")
                return
            insert_person(first, last, email, phone)
            messagebox.showinfo("Success", "Person added successfully.")
        else:
            update_person(self.selected_person_id, first, last, email, phone)
            messagebox.showinfo("Success", "Person record updated.")

        self.clear_form()
        self.load_data()

    def delete(self):
        if not self.selected_person_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", 
            "Are you sure you want to delete this person?\n"
            "This will also delete associated affiliations and interactions.",
            icon="warning"
        )
        if confirm:
            delete_person(self.selected_person_id)
            messagebox.showinfo("Deleted", "Person record deleted.")
            self.clear_form()
            self.load_data()

    def clear_form(self):
        self.selected_person_id = None
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.form_frame.config(text="Add / Edit Person")
        self.submit_btn.config(text="Submit")
        self.delete_btn.config(state="disabled")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        rows = search_people(query) if query else get_all_people()
        self.populate_tree(rows)

    def populate_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def load_data(self):
        self.search_var.set("")
        self.populate_tree(get_all_people())

    def export_csv(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("Warning", "No records available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export People to CSV"
        )
        if not filepath:
            return

        headers = ["ID", "First Name", "Last Name", "Email", "Phone"]
        try:
            export_table_to_csv(filepath, headers, rows)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")