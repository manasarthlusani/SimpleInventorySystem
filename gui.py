
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
from database import initialize_database


initialize_database()


# Application colors
BACKGROUND = "#f4f6f9"
SIDEBAR = "#17243b"
WHITE = "#ffffff"
TEXT = "#17243b"
BLUE = "#2563eb"
GRAY = "#64748b"
RED = "#dc2626"
GREEN = "#16a34a"


# Main window
root = tk.Tk()
root.title("StockFlow - Inventory Management System")
root.geometry("1250x750")
root.minsize(1000, 600)
root.configure(bg=BACKGROUND)

current_page = "Dashboard"

search_var = tk.StringVar()
category_var = tk.StringVar(value="All Categories")


# Retrieve dashboard statistics
def get_statistics():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(quantity), 0),
               COALESCE(SUM(quantity * price), 0),
               COALESCE(SUM(
                   CASE WHEN quantity < 5 THEN 1 ELSE 0 END
               ), 0)
        FROM products
    """)

    statistics = cursor.fetchone()
    connection.close()

    return statistics


# Load products into the table
def load_products(*args):
    for item in table.get_children():
        table.delete(item)

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    query = """
        SELECT * FROM products
        WHERE 1 = 1
    """

    parameters = []

    search = search_var.get().strip()

    if search:
        query += """
            AND (
                name LIKE ?
                OR category LIKE ?
                OR supplier LIKE ?
            )
        """

        parameters.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    category = category_var.get()

    if category != "All Categories":
        query += " AND category = ?"
        parameters.append(category)

    if current_page == "Low Stock":
        query += " AND quantity < 5"

    query += " ORDER BY id"

    cursor.execute(query, parameters)
    products = cursor.fetchall()

    connection.close()

    for product in products:
        tag = "low_stock" if product[3] < 5 else "normal"

        table.insert(
            "",
            "end",
            values=(
                product[0],
                product[1],
                product[2],
                product[3],
                f"${product[4]:.2f}",
                product[5]
            ),
            tags=(tag,)
        )

    results_label.config(
        text=f"Showing {len(products)} product(s)"
    )


# Update category dropdown
def refresh_categories():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT category
        FROM products
        ORDER BY category
    """)

    categories = ["All Categories"]

    for row in cursor.fetchall():
        categories.append(row[0])

    connection.close()

    category_dropdown["values"] = categories

    if category_var.get() not in categories:
        category_var.set("All Categories")


# Refresh dashboard
def refresh_dashboard():
    total, units, value, low = get_statistics()

    total_label.config(text=str(total))
    units_label.config(text=str(units))
    value_label.config(text=f"${value:,.2f}")
    low_label.config(text=str(low))

    refresh_categories()
    load_products()


# Navigation
def show_page(page):
    global current_page

    current_page = page

    page_title.config(text=page)

    if page == "Low Stock":
        table_title.config(
            text="Products Needing Restock"
        )
    else:
        table_title.config(text="Current Inventory")

    search_var.set("")
    category_var.set("All Categories")

    refresh_dashboard()


# Get selected product ID
def get_selected_id():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a product first."
        )
        return None

    values = table.item(selected[0], "values")

    return int(values[0])


# Add or edit product form
def product_form(product_id=None):
    editing = product_id is not None

    product = None

    if editing:
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM products
            WHERE id = ?
        """, (product_id,))

        product = cursor.fetchone()
        connection.close()

        if product is None:
            messagebox.showerror(
                "Error",
                "Product not found."
            )
            refresh_dashboard()
            return

    window = tk.Toplevel(root)

    window.title(
        "Edit Product" if editing else "Add Product"
    )

    window.geometry("450x540")
    window.resizable(False, False)
    window.configure(bg=BACKGROUND)
    window.transient(root)
    window.grab_set()

    tk.Label(
        window,
        text="Edit Product" if editing else "Add Product",
        font=("Segoe UI", 22, "bold"),
        bg=BACKGROUND,
        fg=TEXT
    ).pack(pady=(20, 15))

    form = tk.Frame(window, bg=BACKGROUND)
    form.pack(fill="x", padx=30)

    fields = [
        "Product Name",
        "Category",
        "Quantity",
        "Price",
        "Supplier"
    ]

    entries = {}

    for index, field in enumerate(fields):
        tk.Label(
            form,
            text=field,
            font=("Segoe UI", 10, "bold"),
            bg=BACKGROUND,
            fg=TEXT
        ).pack(anchor="w", pady=(8, 4))

        entry = ttk.Entry(
            form,
            font=("Segoe UI", 11)
        )

        entry.pack(fill="x", ipady=5)

        entries[field] = entry

        if editing:
            value = product[index + 1]
            entry.insert(0, "" if value is None else str(value))

    entries["Product Name"].focus_set()

    # Save product
    def save_product():
        name = entries["Product Name"].get().strip()
        category = entries["Category"].get().strip()
        supplier = entries["Supplier"].get().strip()

        if not name or not category or not supplier:
            messagebox.showerror(
                "Invalid Input",
                "Please complete all text fields.",
                parent=window
            )
            return

        try:
            quantity = int(entries["Quantity"].get())
            price = float(entries["Price"].get())

            if quantity < 0:
                raise ValueError

            if not math.isfinite(price) or price < 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a valid non-negative quantity and price.",
                parent=window
            )
            return

        connection = None

        try:
            connection = sqlite3.connect("inventory.db")
            cursor = connection.cursor()

            if editing:
                cursor.execute("""
                    UPDATE products
                    SET name = ?,
                        category = ?,
                        quantity = ?,
                        price = ?,
                        supplier = ?
                    WHERE id = ?
                """, (
                    name,
                    category,
                    quantity,
                    price,
                    supplier,
                    product_id
                ))

                if cursor.rowcount == 0:
                    messagebox.showerror(
                        "Error",
                        "Product no longer exists.",
                        parent=window
                    )
                    return

            else:
                cursor.execute("""
                    INSERT INTO products
                    (name, category, quantity, price, supplier)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    name,
                    category,
                    quantity,
                    price,
                    supplier
                ))

            connection.commit()

        except (sqlite3.Error, OverflowError) as error:
            messagebox.showerror(
                "Database Error",
                str(error),
                parent=window
            )
            return

        finally:
            if connection is not None:
                connection.close()

        window.destroy()

        search_var.set("")
        category_var.set("All Categories")
        refresh_dashboard()

        messagebox.showinfo(
            "Success",
            "Product updated successfully!"
            if editing
            else "Product added successfully!"
        )

    buttons = tk.Frame(window, bg=BACKGROUND)
    buttons.pack(pady=20)

    tk.Button(
        buttons,
        text="Save Product",
        command=save_product,
        bg=BLUE,
        fg=WHITE,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8,
        cursor="hand2"
    ).pack(side="left", padx=5)

    tk.Button(
        buttons,
        text="Cancel",
        command=window.destroy,
        bg="#e2e8f0",
        fg=TEXT,
        font=("Segoe UI", 11),
        relief="flat",
        padx=20,
        pady=8,
        cursor="hand2"
    ).pack(side="left", padx=5)


# Add product
def add_product():
    product_form()


# Edit selected product
def edit_product():
    product_id = get_selected_id()

    if product_id is not None:
        product_form(product_id)


# Delete selected product
def delete_product():
    product_id = get_selected_id()

    if product_id is None:
        return

    selected = table.selection()[0]
    product_name = table.item(selected, "values")[1]

    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to delete {product_name}?"
    )

    if not confirm:
        return

    connection = None

    try:
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM products
            WHERE id = ?
        """, (product_id,))

        deleted = cursor.rowcount
        connection.commit()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            str(error)
        )
        return

    finally:
        if connection is not None:
            connection.close()

    refresh_dashboard()

    if deleted:
        messagebox.showinfo(
            "Success",
            "Product deleted successfully!"
        )
    else:
        messagebox.showwarning(
            "Not Found",
            "Product no longer exists."
        )


# Clear search and filters
def clear_filters():
    search_var.set("")
    category_var.set("All Categories")
    load_products()


# Sidebar
sidebar = tk.Frame(
    root,
    bg=SIDEBAR,
    width=210
)

sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="StockFlow",
    font=("Segoe UI", 24, "bold"),
    bg=SIDEBAR,
    fg=WHITE
).pack(pady=(30, 5))

tk.Label(
    sidebar,
    text="Inventory Management",
    font=("Segoe UI", 10),
    bg=SIDEBAR,
    fg="#94a3b8"
).pack(pady=(0, 35))


# Sidebar button helper
def sidebar_button(text, command):
    tk.Button(
        sidebar,
        text=text,
        command=command,
        font=("Segoe UI", 12),
        bg=SIDEBAR,
        fg=WHITE,
        activebackground="#334155",
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=20,
        pady=12,
        cursor="hand2"
    ).pack(fill="x", padx=10, pady=3)


sidebar_button(
    "Dashboard",
    lambda: show_page("Dashboard")
)

sidebar_button(
    "Inventory",
    lambda: show_page("Inventory")
)

sidebar_button(
    "Add Product",
    add_product
)

sidebar_button(
    "Low Stock",
    lambda: show_page("Low Stock")
)

sidebar_button(
    "Refresh",
    refresh_dashboard
)

tk.Button(
    sidebar,
    text="Exit",
    command=root.destroy,
    font=("Segoe UI", 12),
    bg=SIDEBAR,
    fg=WHITE,
    relief="flat",
    cursor="hand2"
).pack(side="bottom", pady=25)


# Main content
content = tk.Frame(root, bg=BACKGROUND)

content.pack(
    side="left",
    fill="both",
    expand=True,
    padx=25,
    pady=25
)

page_title = tk.Label(
    content,
    text="Dashboard",
    font=("Segoe UI", 26, "bold"),
    bg=BACKGROUND,
    fg=TEXT
)

page_title.pack(anchor="w")

tk.Label(
    content,
    text="Monitor and manage your inventory.",
    font=("Segoe UI", 11),
    bg=BACKGROUND,
    fg=GRAY
).pack(anchor="w", pady=(0, 25))


# Statistics cards
cards_frame = tk.Frame(content, bg=BACKGROUND)
cards_frame.pack(fill="x")


def create_card(parent, title, value, column):
    card = tk.Frame(
        parent,
        bg=WHITE,
        padx=18,
        pady=18
    )

    card.grid(
        row=0,
        column=column,
        padx=5,
        sticky="nsew"
    )

    parent.grid_columnconfigure(column, weight=1)

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 10),
        bg=WHITE,
        fg=GRAY
    ).pack(anchor="w")

    label = tk.Label(
        card,
        text=value,
        font=("Segoe UI", 19, "bold"),
        bg=WHITE,
        fg=TEXT
    )

    label.pack(anchor="w", pady=(10, 0))

    return label


total_label = create_card(
    cards_frame, "Total Products", "0", 0
)

units_label = create_card(
    cards_frame, "Units in Stock", "0", 1
)

value_label = create_card(
    cards_frame, "Inventory Value", "$0.00", 2
)

low_label = create_card(
    cards_frame, "Low Stock", "0", 3
)


# Table title
table_title = tk.Label(
    content,
    text="Current Inventory",
    font=("Segoe UI", 18, "bold"),
    bg=BACKGROUND,
    fg=TEXT
)

table_title.pack(anchor="w", pady=(25, 10))


# Search and filter area
filter_frame = tk.Frame(content, bg=BACKGROUND)
filter_frame.pack(fill="x", pady=(0, 10))

tk.Label(
    filter_frame,
    text="Search:",
    bg=BACKGROUND,
    fg=TEXT,
    font=("Segoe UI", 10)
).pack(side="left", padx=(0, 5))

search_entry = ttk.Entry(
    filter_frame,
    textvariable=search_var,
    font=("Segoe UI", 11),
    width=24
)

search_entry.pack(side="left", ipady=4, padx=(0, 15))

category_dropdown = ttk.Combobox(
    filter_frame,
    textvariable=category_var,
    state="readonly",
    width=20
)

category_dropdown.pack(side="left", padx=5)

ttk.Button(
    filter_frame,
    text="Clear Filters",
    command=clear_filters
).pack(side="left", padx=5)


# Action buttons
action_frame = tk.Frame(content, bg=BACKGROUND)
action_frame.pack(fill="x", pady=(0, 12))


def action_button(text, command, color):
    tk.Button(
        action_frame,
        text=text,
        command=command,
        bg=color,
        fg=WHITE,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=16,
        pady=9,
        cursor="hand2"
    ).pack(side="left", padx=(0, 8))


action_button("+ Add Product", add_product, BLUE)
action_button("Edit Product", edit_product, "#475569")
action_button("Delete Product", delete_product, RED)


# Table container
table_frame = tk.Frame(content, bg=WHITE)
table_frame.pack(fill="both", expand=True)


# Table styling
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    foreground=TEXT,
    rowheight=35,
    fieldbackground=WHITE,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background="#e2e8f0",
    foreground=TEXT,
    font=("Segoe UI", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", BLUE)],
    foreground=[("selected", WHITE)]
)


# Table columns
columns = (
    "ID",
    "Name",
    "Category",
    "Quantity",
    "Price",
    "Supplier"
)

table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)

for column in columns:
    table.heading(column, text=column)

table.column("ID", width=50, anchor="center")
table.column("Name", width=150)
table.column("Category", width=130)
table.column("Quantity", width=80, anchor="center")
table.column("Price", width=100, anchor="center")
table.column("Supplier", width=130)


# Low-stock highlighting
table.tag_configure(
    "low_stock",
    background="#fee2e2",
    foreground="#991b1b"
)

table.tag_configure(
    "normal",
    background=WHITE
)


# Scrollbar
scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)

table.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
table.pack(fill="both", expand=True)


# Double-click to edit
table.bind(
    "<Double-1>",
    lambda event: edit_product()
)


# Status bar
status_frame = tk.Frame(content, bg=BACKGROUND)
status_frame.pack(fill="x", pady=(12, 0))

tk.Label(
    status_frame,
    text="SQLite Database Connected",
    font=("Segoe UI", 10),
    bg=BACKGROUND,
    fg=GREEN
).pack(side="left")

results_label = tk.Label(
    status_frame,
    text="Showing 0 products",
    font=("Segoe UI", 10),
    bg=BACKGROUND,
    fg=GRAY
)

results_label.pack(side="right")


# Live search and category filtering
search_var.trace_add("write", load_products)

category_dropdown.bind(
    "<<ComboboxSelected>>",
    load_products
)


# Load initial dashboard
refresh_dashboard()


# Run application
root.mainloop()