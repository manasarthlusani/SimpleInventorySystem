import sqlite3
import math


# Validate whole numbers
def get_integer(prompt):
    while True:
        try:
            value = int(input(prompt))

            if value < 0:
                print("Please enter a non-negative number.")
            else:
                return value

        except ValueError:
            print("Please enter a valid whole number.")


# Validate decimal numbers
def get_float(prompt):
    while True:
        try:
            value = float(input(prompt))

            if not math.isfinite(value) or value < 0:
                print("Please enter a non-negative number.")
            else:
                return value

        except ValueError:
            print("Please enter a valid number.")


# Validate text input
def get_text(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be empty.")


# Add a new product
def add_product():
    name = get_text("Enter product name: ")
    category = get_text("Enter category: ")
    quantity = get_integer("Enter quantity: ")
    price = get_float("Enter price: ")
    supplier = get_text("Enter supplier: ")

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, category, quantity, price, supplier)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, quantity, price, supplier))

    connection.commit()
    connection.close()

    print("Product added successfully!")


# Display products in a formatted table
def display_products(products):
    if not products:
        print("No products found.")
        return

    print(f"{'ID':<5}{'Name':<20}{'Category':<20}"
          f"{'Quantity':<12}{'Price':<12}{'Supplier':<20}")
    print("-" * 89)

    for product in products:
        print(f"{product[0]:<5}{product[1]:<20}"
              f"{product[2]:<20}{product[3]:<12}"
              f"${product[4]:<11.2f}{product[5] or 'N/A':<20}")


# View all products
def view_inventory():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products ORDER BY id")
    products = cursor.fetchall()

    print("\n--- CURRENT INVENTORY ---")

    display_products(products)

    connection.close()


# Search for a product
def search_product():
    name = get_text("Enter product name to search: ")

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE ?
    """, ("%" + name + "%",))

    products = cursor.fetchall()

    print("\n--- SEARCH RESULTS ---")

    display_products(products)

    connection.close()


# Update an existing product
def update_product():
    view_inventory()

    product_id = get_integer("Enter product ID: ")

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE id = ?
    """, (product_id,))

    product = cursor.fetchone()

    if product is None:
        print("Product not found.")
        connection.close()
        return

    print(f"Updating product: {product[1]}")

    quantity = get_integer("Enter new quantity: ")
    price = get_float("Enter new price: ")

    cursor.execute("""
        UPDATE products
        SET quantity = ?, price = ?
        WHERE id = ?
    """, (quantity, price, product_id))

    connection.commit()
    connection.close()

    print("Product updated successfully!")


# Delete a product
def delete_product():
    view_inventory()

    product_id = get_integer("Enter product ID: ")

    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE id = ?
    """, (product_id,))

    product = cursor.fetchone()

    if product is None:
        print("Product not found.")
        connection.close()
        return

    confirm = input(
        f"Are you sure you want to delete {product[1]}? (yes/no): "
    )

    if confirm.strip().lower() != "yes":
        print("Deletion cancelled.")
        connection.close()
        return

    cursor.execute("""
        DELETE FROM products
        WHERE id = ?
    """, (product_id,))

    connection.commit()
    connection.close()

    print("Product deleted successfully!")


# Display low-stock products
def low_stock():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, quantity FROM products
        WHERE quantity < 5
        ORDER BY quantity ASC
    """)

    products = cursor.fetchall()

    print("\n--- LOW STOCK ALERTS ---")

    if products:
        for product in products:
            print(f"ID: {product[0]} | {product[1]} "
                  f"| Remaining: {product[2]}")
    else:
        print("All products are sufficiently stocked.")

    connection.close()


# Calculate total inventory value
def inventory_value():
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT SUM(quantity * price)
        FROM products
    """)

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print(f"\nTotal inventory value: ${total:,.2f}")

    connection.close()
