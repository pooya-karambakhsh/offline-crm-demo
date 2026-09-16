import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import (
    insert_interaction, 
    update_interaction,
    delete_interaction,
    get_all_people, 
    get_all_interactions, 
    search_interactions,
    export_table_to_csv
)

class InteractionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_interaction_id = None
        self.person_map = {}
        self.create_widgets()
        self.refresh_people_dropdown()
        self.load_data()

    def create_widgets(self):
        self.form_frame = ttk.LabelFrame(self, text="Log / Edit Interaction")
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.selected_person = tk.StringVar()
        self.date_var = tk.StringVar()
        self.description_var = tk.StringVar()

        ttk.Label(self.form_frame, text="Person").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.person_combo = ttk.Combobox(self.form_frame, textvariable=self.selected_person, state="readonly", width=28)
        self.person_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.date_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Description").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.description_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.grid(row=3, columnspan=2, pady=15)

        self.submit_btn = ttk.Button(btn_frame, text="Submit", command=self.submit)
        self.submit_btn.pack(side=tk.LEFT, padx=3)

        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete, state="disabled")
        self.delete_btn.pack(side=tk.LEFT, padx=3)

        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=3)

        table_frame = ttk.LabelFrame(self, text="Interaction Records")
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        columns = ("id", "person_name", "date", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("person_name", text="Person")
        self.tree.heading("date", text="Date")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=40)
        self.tree.column("person_name", width=140)
        self.tree.column("date", width=100)
        self.tree.column("description", width=220)

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
        self.selected_interaction_id = values[0]

        self.selected_person.set(values[1])
        self.date_var.set(values[2] if values[2] != "None" else "")
        self.description_var.set(values[3] if values[3] != "None" else "")

        self.form_frame.config(text=f"Edit Interaction (ID: {self.selected_interaction_id})")
        self.submit_btn.config(text="Update")
        self.delete_btn.config(state="normal")

    def submit(self):
        person_name = self.selected_person.get()
        date_str = self.date_var.get().strip()
        desc_str = self.description_var.get().strip()

        if not person_name or person_name not in self.person_map:
            messagebox.showerror("Error", "Please select a valid person.")
            return

        if not date_str:
            messagebox.showerror("Error", "Date is required.")
            return

        person_id = self.person_map[person_name]

        if self.selected_interaction_id is None:
            insert_interaction(person_id, date_str, desc_str)
            messagebox.showinfo("Success", "Interaction logged successfully.")
        else:
            update_interaction(self.selected_interaction_id, person_id, date_str, desc_str)
            messagebox.showinfo("Success", "Interaction updated successfully.")

        self.clear_form()
        self.load_data()

    def delete(self):
        if not self.selected_interaction_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", 
            "Are you sure you want to delete this interaction record?",
            icon="warning"
        )
        if confirm:
            delete_interaction(self.selected_interaction_id)
            messagebox.showinfo("Deleted", "Interaction record deleted.")
            self.clear_form()
            self.load_data()

    def clear_form(self):
        self.selected_interaction_id = None
        self.selected_person.set("")
        self.date_var.set("")
        self.description_var.set("")
        self.form_frame.config(text="Log / Edit Interaction")
        self.submit_btn.config(text="Submit")
        self.delete_btn.config(state="disabled")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        rows = search_interactions(query) if query else get_all_interactions()
        self.populate_tree(rows)

    def refresh_people_dropdown(self):
        people = get_all_people()
        self.person_map = {f"{p[1]} {p[2]}": p[0] for p in people}
        self.person_combo["values"] = list(self.person_map.keys())

    def populate_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def load_data(self):
        self.refresh_people_dropdown()
        self.search_var.set("")
        self.populate_tree(get_all_interactions())

    def export_csv(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("Warning", "No records available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Interactions to CSV"
        )
        if not filepath:
            return

        headers = ["ID", "Person", "Date", "Description"]
        try:
            export_table_to_csv(filepath, headers, rows)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")