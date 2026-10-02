import json

INVENTORY_FILE = "inventory.json"


def load_inventory():
    """Load inventory from inventory.json or use default products."""
    default_inventory = [
        {"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15},
        {"id": "P002", "name": "Mouse", "price": 25.50, "stock": 40},
        {"id": "P003", "name": "Keyboard", "price": 45.00, "stock": 25},
    ]

    try:
        with open(INVENTORY_FILE, "r") as file:
            inventory = json.load(file)
            if isinstance(inventory, list) and inventory:
                print("inventory.json found.")
                print("Inventory loaded successfully.")
                return inventory
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass

    return default_inventory


def save_inventory(inventory):
    """Save the current inventory to inventory.json."""
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=2)


def display_all(inventory):
    """Display all products in the inventory."""
    print("Current Inventory")
    print("-" * 50)
    for product in inventory:
        print(
            f"ID: {product['id']} | Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | Stock: {product['stock']}"
        )
    print("-" * 50)


def add_product(inventory):
    """Add a new product to the inventory list."""
    product_id = input("Enter product ID: ").strip().upper() #add upper() to ensure case-insensitive matching       
    name = input("Enter product name: ").strip().upper() #add upper() to ensure case-insensitive matching
    price = float(input("Enter price: ").strip())
    stock = int(input("Enter stock: ").strip())

    inventory.append({
        "id": product_id,
        "name": name,
        "price": price,
        "stock": stock,
    })
    print("Product added successfully.")


def update_stock(inventory):
    """Update the stock of an existing product."""
    product_id = input("Enter product ID: ").strip().upper() #add upper() to ensure case-insensitive matching

    for product in inventory:
        if product["id"] == product_id:
            new_stock = int(input("Enter new stock: ").strip())
            product["stock"] = new_stock
            print(f"Stock updated for {product['name']}.")
            return

    print("Product not found.")


def search_product(inventory):
    """Search for a product by ID or name."""
    search_value = input("Enter product ID or name: ").strip().upper() #add upper() to ensure case-insensitive matching

    for product in inventory:
        if product["id"] == search_value or product["name"].lower() == search_value.lower():
            print(
                f"ID: {product['id']} | Name: {product['name']} | "
                f"Price: ${product['price']:.2f} | Stock: {product['stock']}"
            )
            return

    print("Product not found.")


def main():
    inventory = load_inventory()

    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)

    while True:
        print("----------- MENU -----------")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")
        print("---------------------------")

        choice = input("Enter option: ").strip().lower() #add upper() to ensure case-insensitive matching

        # Check exit commands FIRST (before other conditions)
        if choice in ["exit", "quit", "6"]:
            save_inventory(inventory)
            print("Saving inventory before exit...")
            print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break


        if choice == "1":
            display_all(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
            print("Inventory saved successfully.")
        elif choice == "6":
            save_inventory(inventory)
            print("Inventory saved successfully.!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
