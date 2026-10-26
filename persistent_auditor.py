import json

INVENTORY_FILE = "inventory.json"


class Product:
    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self._product_id = product_id
        self.name = name
        self._price = float(price)
        self._stock = int(stock)

    @property
    def product_id(self):
        return self._product_id

    @property
    def price(self):
        return self._price

    @property
    def stock(self):
        return self._stock

    def update_stock(self, new_stock: int):
        if new_stock >= 0:
            self._stock = new_stock
            print(f"Stock updated for {self.name}.")
        else:
            print("Stock cannot be negative.")

    def display_information(self):
        print(
            f"ID: {self._product_id} | Name: {self.name} | "
            f"Price: ${self._price:.2f} | Stock: {self._stock}"
        )

    def to_dict(self):
        return {
            "id": self._product_id,
            "name": self.name,
            "price": self._price,
            "stock": self._stock,
        }


class Inventory:
    def __init__(self):
        self.products = []

    def add_product(self, product: Product):
        self.products.append(product)

    def search_product(self, search_term: str):
        search_term = search_term.strip().upper()
        for product in self.products:
            if product.product_id.upper() == search_term or product.name.upper() == search_term:
                return product
        return None

    def display_all(self):
        print("Current Inventory")
        print("-" * 50)
        for product in self.products:
            product.display_information()
        print("-" * 50)


def load_inventory() -> Inventory:
    """Load inventory from inventory.json or use default products."""
    inventory = Inventory()
    default_products = [
        Product("P001", "Laptop", 1200.00, 15),
        Product("P002", "Mouse", 25.50, 40),
        Product("P003", "Keyboard", 45.00, 25),
    ]

    try:
        with open(INVENTORY_FILE, "r") as file:
            data = json.load(file)
            if isinstance(data, list) and data:
                for item in data:
                    inventory.add_product(
                        Product(
                            product_id=item["id"],
                            name=item["name"],
                            price=item["price"],
                            stock=item["stock"],
                        )
                    )
                print("inventory.json found.")
                print("Inventory loaded successfully.")
                return inventory
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass

    for product in default_products:
        inventory.add_product(product)
    return inventory


def save_inventory(inventory: Inventory):
    """Save the current inventory to inventory.json."""
    data = [product.to_dict() for product in inventory.products]
    with open(INVENTORY_FILE, "w") as file:
        json.dump(data, file, indent=2)


def add_product(inventory: Inventory):
    """Add a new product to the inventory."""
    product_id = input("Enter product ID: ").strip().upper()
    name = input("Enter product name: ").strip().upper()
    price = float(input("Enter price: ").strip())
    stock = int(input("Enter stock: ").strip())

    new_product = Product(product_id, name, price, stock)
    inventory.add_product(new_product)
    print("Product added successfully.")


def update_stock(inventory: Inventory):
    """Update the stock of an existing product."""
    product_id = input("Enter product ID: ").strip().upper()
    product = inventory.search_product(product_id)

    if product:
        new_stock = int(input("Enter new stock: ").strip())
        product.update_stock(new_stock)
    else:
        print("Product not found.")


def search_product(inventory: Inventory):
    """Search for a product by ID or name."""
    search_value = input("Enter product ID or name: ").strip().upper()
    product = inventory.search_product(search_value)

    if product:
        product.display_information()
    else:
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

        choice = input("Enter option: ").strip().lower()

        if choice in ["exit", "quit", "6"]:
            save_inventory(inventory)
            print("Saving inventory before exit...")
            print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        elif choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
            print("Inventory saved successfully.")
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()