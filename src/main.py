import tkinter as tk
from tkinter import ttk
from db import init_db
from person_form import PersonFrame
from org_form import OrgFrame
from interaction_form import InteractionFrame
from affiliation_form import AffiliationFrame

def main():
    init_db()

    root = tk.Tk()
    root.title("Offline CRM")
    root.geometry("850x550")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    person_tab = PersonFrame(notebook)
    org_tab = OrgFrame(notebook)
    interaction_tab = InteractionFrame(notebook)
    affiliation_tab = AffiliationFrame(notebook)

    notebook.add(person_tab, text="People")
    notebook.add(org_tab, text="Organisations")
    notebook.add(interaction_tab, text="Interactions")
    notebook.add(affiliation_tab, text="Affiliations")

    # Automatically refresh dropdowns/records when switching tabs
    def on_tab_change(event):
        selected_widget = notebook.nametowidget(notebook.select())
        if hasattr(selected_widget, "load_data"):
            selected_widget.load_data()

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    root.mainloop()

if __name__ == "__main__":
    main()