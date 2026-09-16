import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import (
    insert_organisation, 
    update_organisation, 
    delete_organisation,
    get_all_organisations, 
    search_organisations,
    check_organisation_exists,
    export_table_to_csv
)

class OrgFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_org_id = None
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.form_frame = ttk.LabelFrame(self, text="Add / Edit Organisation")
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.name_var = tk.StringVar()
        self.industry_var = tk.StringVar()
        self.contact_var = tk.StringVar()

        ttk.Label(self.form_frame, text="Organisation Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Industry").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.industry_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.form_frame, text="Contact Info").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.form_frame, textvariable=self.contact_var).grid(row=2, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.grid(row=3, columnspan=2, pady=15)

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

        columns = ("id", "name", "industry", "contact_info")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("industry", text="Industry")
        self.tree.heading("contact_info", text="Contact Info")

        self.tree.column("id", width=40)
        self.tree.column("name", width=150)
        self.tree.column("industry", width=120)
        self.tree.column("contact_info", width=150)

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
        self.selected_org_id = values[0]

        self.name_var.set(values[1])
        self.industry_var.set(values[2] if values[2] != "None" else "")
        self.contact_var.set(values[3] if values[3] != "None" else "")

        self.form_frame.config(text=f"Edit Organisation (ID: {self.selected_org_id})")
        self.submit_btn.config(text="Update")
        self.delete_btn.config(state="normal")

    def submit(self):
        name = self.name_var.get().strip()
        industry = self.industry_var.get().strip()
        contact = self.contact_var.get().strip()

        if not name:
            messagebox.showerror("Error", "Name is required.")
            return

        if self.selected_org_id is None:
            if check_organisation_exists(name):
                messagebox.showwarning("Duplicate Entry", "A record with this name already exists.")
                return
            insert_organisation(name, industry, contact)
            messagebox.showinfo("Success", "Organisation created.")
        else:
            update_organisation(self.selected_org_id, name, industry, contact)
            messagebox.showinfo("Success", "Organisation updated.")

        self.clear_form()
        self.load_data()

    def delete(self):
        if not self.selected_org_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", 
            "Are you sure you want to delete this organisation?\n"
            "This will also delete associated affiliations.",
            icon="warning"
        )
        if confirm:
            delete_organisation(self.selected_org_id)
            messagebox.showinfo("Deleted", "Organisation record deleted.")
            self.clear_form()
            self.load_data()

    def clear_form(self):
        self.selected_org_id = None
        self.name_var.set("")
        self.industry_var.set("")
        self.contact_var.set("")
        self.form_frame.config(text="Add / Edit Organisation")
        self.submit_btn.config(text="Submit")
        self.delete_btn.config(state="disabled")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def on_search(self, event=None):
        query = self.search_var.get().strip()
        rows = search_organisations(query) if query else get_all_organisations()
        self.populate_tree(rows)

    def populate_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def load_data(self):
        self.search_var.set("")
        self.populate_tree(get_all_organisations())

    def export_csv(self):
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("Warning", "No records available to export.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Organisations to CSV"
        )
        if not filepath:
            return

        headers = ["ID", "Name", "Industry", "Contact Info"]
        try:
            export_table_to_csv(filepath, headers, rows)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")