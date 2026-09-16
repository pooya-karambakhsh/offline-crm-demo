import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import (
    insert_affiliation, 
    update_affiliation,
    delete_affiliation,
    get_all_people, 
    get_all_organisations, 
    get_all_affiliations, 
    search_affiliations,
    export_table_to_csv
)

class AffiliationFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_affiliation_id = None
        self.person_map = {}
        self.org_map = {}
        self.create_widgets()
        self.refresh_dropdowns()
        self.load_data()

    def create_widgets(self):
        self.form_frame = ttk.LabelFrame(self, text="Log / Edit Affiliation")
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.selected_person = tk.StringVar()
        self.selected_org = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        self.position_var = tk.StringVar()

        ttk.Label(self.form_frame, text="Select Person").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.person_combo = ttk.Combobox(self.form_frame, textvariable=self.selected_person, state="readonly", width=28)
        self.person_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Select Organisation").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.org_combo = ttk.Combobox(self.form_frame, textvariable=self.selected_org, state="readonly", width=28)
        self.org_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Start Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.start_date_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="End Date (YYYY-MM-DD)").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.end_date_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Position").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.position_var, width=30).grid(row=4, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.grid(row=5, columnspan=2, pady=15)

        self.submit_btn = ttk.Button(btn_frame, text="Submit", command=self.submit)
        self.submit_btn.pack(side=tk.LEFT, padx=3)

        self.delete_btn = ttk.Button(btn_frame, text="Delete", command=self.delete, state="disabled")
        self.delete_btn.pack(side=tk.LEFT, padx=3)

        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_form)
        self.clear_btn.pack(side=tk.LEFT, padx=3)

        table_frame = ttk.LabelFrame(self, text="Affiliation Records")
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        columns = ("id", "person", "organisation", "position", "start_date", "end_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("person", text="Person")
        self.tree.heading("organisation", text="Organisation")
        self.tree.heading("position", text="Position")
        self.tree.heading("start_date", text="Start Date")
        self.tree.heading("end_date", text="End Date")

        self.tree.column("id", width=30)
        self.tree.column("person", width=120)
        self.tree.column("organisation", width=130)
        self.tree.column("position", width=100)
        self.tree.column("start_date", width=80)
        self.tree.column("end_date", width=80)

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
        self.selected_affiliation_id = values[0]

        self.selected_person.set(values[1])
        self.selected_org.set(values[2])
        self.position_var.set(values[3] if values[3] != "None" else "")
        self.start_date_var.set(values[4] if values[4] != "None" else "")
        self.end_date_var.set(values[5] if values[5] != "None" else "")

        self.form_frame.config(text=f"Edit Affiliation (ID: {self.selected_affiliation_id})")
        self.submit_btn.config(text="Update")
        self.delete_btn.config(state="normal")

    def submit(self):
        person_name = self.selected_person.get()
        org_name = self.selected_org.get()
        start_date = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()
        position = self.position_var.get().strip()

        if not person_name or not org_name:
            messagebox.showerror("Error", "Please select both a person and an organisation.")
            return

        person_id = self.person_map.get(person_name)
        org_id = self.org_map.get(org_name)

        if self.selected_affiliation_id is None:
            insert_affiliation(person_id, org_id, start_date, end_date, position)
            messagebox.showinfo("Success", "Affiliation logged successfully.")
        else:
            update_affiliation(self.selected_affiliation_id, person_id, org_id, start_date, end_date, position)
            messagebox.showinfo("Success", "Affiliation updated successfully.")

        self.clear_form()
        self.load_data()

    def delete(self):
        if not self.selected_affiliation_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", 
            "Are you sure you want to delete this affiliation entry?",
            icon="warning"
        )
        if confirm:
            delete_affiliation(self.selected_affiliation_id)
            messagebox.showinfo("Deleted", "Affiliation record deleted.")
            self.clear_form()
            self.load_data()

    def clear_form(self):
        self.selected_affiliation_id = None
        self.selected_person.set("")
        self.selected_org.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.position_var.set("")
        self.form_frame.config(text="Log / Edit Affiliation")
        self.submit_btn.config(text="Submit")
        self.delete_btn.config(state="disabled")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        rows = search_affiliations(query) if query else get_all_affiliations()
        self.populate_tree(rows)

    def refresh_dropdowns(self):
        people = get_all_people()
        orgs = get_all_organisations()

        self.person_map = {f"{p[1]} {p[2]}": p[0] for p in people}
        self.org_map = {o[1]: o[0] for o in orgs}

        self.person_combo["values"] = list(self.person_map.keys())
        self.org_combo["values"] = list(self.org_map.keys())

    def populate_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def load_data(self):
        self.refresh_dropdowns()
        self.search_var.set("")
        self.populate_tree(get_all_affiliations())

    def export_csv(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("Warning", "No records available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Affiliations to CSV"
        )
        if not filepath:
            return

        headers = ["ID", "Person", "Organisation", "Position", "Start Date", "End Date"]
        try:
            export_table_to_csv(filepath, headers, rows)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")