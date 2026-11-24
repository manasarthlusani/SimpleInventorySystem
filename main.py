from database import initialize_database
from inventory import (
    add_product,
    view_inventory,
    search_product,
    update_product,
    delete_product,
    low_stock,
    inventory_value
)


def main():
    initialize_database()

    while True:
        print("\n================================")
        print("  INVENTORY MANAGEMENT SYSTEM")
        print("================================")
        print("1. Add Product")
        print("2. View Inventory")
        print("3. Search Product")
        print("4. Update Product")
        print("5. Delete Product")
        print("6. View Low Stock")
        print("7. Total Inventory Value")
        print("8. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            view_inventory()
        elif choice == "3":
            search_product()
        elif choice == "4":
            update_product()
        elif choice == "5":
            delete_product()
        elif choice == "6":
            low_stock()
        elif choice == "7":
            inventory_value()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
