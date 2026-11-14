from abc import ABC, abstractmethod
import json
import csv

INVENTORY_FILE = "inventory.json"
PRODUCTS_CSV = "products.csv"

class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str):
        self.supplier_id: str = supplier_id
        self.name: str = name
        self.contact_email: str = contact_email

    def display_information(self) -> None:
        print(f"Supplier ID: {self.supplier_id} | Name: {self.name} | "
              f"Email: {self.contact_email}")

    def to_dict(self) -> dict:
        return {"supplier_id": self.supplier_id,
                "name": self.name,
                "contact_email": self.contact_email}

class CanBeShipped(ABC):
    """Interface-style contract for items that can be shipped."""

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        """Calculate and return the shipping fee."""
        pass

class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier):
        price = float(price)          # may raise ValueError if price is not a number
        stock = int(stock)            # may raise ValueError if stock is not a number
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if stock < 0:
            raise ValueError("Stock cannot be negative.")

        self._product_id = product_id
        self.name = name
        self._price = price
        self._stock = stock
        self.supplier: Supplier = supplier

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def price(self) -> float:
        return self._price

    @property
    def stock(self) -> int:
        return self._stock

    def update_stock(self, new_stock: int) -> None:
        if new_stock < 0:
            raise ValueError("Stock cannot be negative.")
        self._stock = new_stock
        print(f"Stock updated for {self.name}.")

    def display_information(self) -> None:
        print(
            f"ID: {self._product_id} | Name: {self.name} | "
            f"Price: ${self._price:.2f} | Stock: {self._stock}",
            f"Supplier: {self.supplier.name}",
            end=" | "
        )

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Abstract contract: Every product subclass must define how it is fulfilled."""
        pass

    def to_dict(self) -> dict:
        return {
            "id": self._product_id,
            "name": self.name,
            "price": self._price,
            "stock": self._stock,
            "supplier": self.supplier.to_dict(),
        }


class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier, weight: float):
        super().__init__(product_id, name, price, stock, supplier)
        self._weight = float(weight)

    @property
    def weight(self) -> float:
        return self._weight

    def calculate_shipping_cost(self) -> float:
        # $5.00 base fee + $2.50 per kg
        return 5.00 + (self._weight * 2.50)

    def get_fulfilment_info(self) -> str:
        return f"Physical shipping required. Shipping fee: ${self.calculate_shipping_cost():.2f}"

    def display_information(self) -> None:
        super().display_information()
        print(
            f"Type: Physical | Weight: {self._weight:.2f}kg | Fulfilment: {self.get_fulfilment_info()}"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self._weight
        return data


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier, download_size: float):
        super().__init__(product_id, name, price, stock, supplier)
        self._download_size = float(download_size)

    @property
    def download_size(self) -> float:
        return self._download_size

    def get_fulfilment_info(self) -> str:
        return f"Delivered via digital download link ({self._download_size:.1f} MB)."

    def display_information(self) -> None:
        super().display_information()
        print(
            f"Type: Digital  | Size: {self._download_size:.1f}MB | Fulfilment: {self.get_fulfilment_info()}"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self._download_size
        return data


class ProductFactory:
    @staticmethod
    def create(product_type: str, product_id: str, name: str, price: float,
               stock: int, supplier: Supplier,
               weight: float = 1.0, download_size: float = 100.0) -> Product:
        product_type = product_type.strip().lower()
        if product_type == "physical":
            return PhysicalProduct(product_id, name, price, stock, supplier, weight)
        elif product_type == "digital":
            return DigitalProduct(product_id, name, price, stock, supplier, download_size)
        else:
            raise ValueError(f"Unknown product type: {product_type}")

class Inventory:
    def __init__(self):
        self.products: list[Product] = []

    def add_product(self, product: Product) -> None:
        self.products.append(product)

    def remove_product(self, product_id: str) -> Product | None:
        product = self.find_product(product_id)
        if product is not None:
            self.products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        for product in self.products:
            if product.product_id.upper() == product_id.strip().upper():
                return product
        return None

    def search_product(self, search_term: str) -> Product | None:
        search_term = search_term.strip().upper()
        for product in self.products:
            if product.product_id.upper() == search_term or product.name.upper() == search_term:
                return product
        return None

    def display_all_products(self) -> None:
        print("Current Inventory")
        print("-" * 50)
        for product in self.products:
            product.display_information()
        print("-" * 50)


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass


class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = float(percentage)

    def apply(self, total: float) -> float:
        return total * (1 - self.percentage / 100)   # 10 -> multiply by 0.9


class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float):
        self.threshold = float(threshold)
        self.amount = float(amount)

    def apply(self, total: float) -> float:
        if total >= self.threshold:
            return total - self.amount
        return total


class StudentDiscount(DiscountStrategy):        # Section 2.4 - the 4th one
    def apply(self, total: float) -> float:
        return total * 0.95

class OrderLine:
    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity

    def display_information(self) -> None:
        print(f"  {self.product.product_id} {self.product.name} x {self.quantity} "
              f"= ${self.calculate_subtotal():.2f}")

class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None):
        self.order_id: str = order_id
        self.order_lines: list[OrderLine] = []
        self.discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)   # Order CREATES it
        self.order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for line in self.order_lines:
            if line.product.product_id.upper() == product_id.strip().upper():
                self.order_lines.remove(line)
                return True
        return False

    def calculate_total(self) -> float:
        total = sum(line.calculate_subtotal() for line in self.order_lines)
        return self.discount.apply(total)        # NO if/elif here

    def display_order(self) -> None:
        print(f"Order {self.order_id}")
        for line in self.order_lines:
            line.display_information()
        print(f"  TOTAL: ${self.calculate_total():.2f}")


DEFAULT_SUPPLIER = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.sg")

def get_or_create_supplier(data: dict | None, suppliers: dict[str, Supplier]) -> Supplier:
    if not data:
        suppliers.setdefault(DEFAULT_SUPPLIER.supplier_id, DEFAULT_SUPPLIER)
        return DEFAULT_SUPPLIER
    sid = data["supplier_id"]
    if sid not in suppliers:
        suppliers[sid] = Supplier(sid, data["name"], data["contact_email"])
    return suppliers[sid]


def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_non_negative_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter 0 or a positive whole number.")
                continue
            return value
        except ValueError:
            print("Please enter a whole number, e.g. 10")


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)                      # skip the header row
            for row in reader:
                try:
                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(product_type, product_id, name,
                                                    price, stock, supplier)
                    inventory.add_product(product)
                    loaded += 1
                except ValueError as e:
                    print(f"Skipped row {row}: {e}")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")

def load_inventory() -> tuple[Inventory, dict[str, Supplier]]:
    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}

    try:
        with open(INVENTORY_FILE, "r") as file:
            data = json.load(file)
            if isinstance(data, list) and data:
                for item in data:
                    supplier = get_or_create_supplier(item.get("supplier"), suppliers)
                    prod = ProductFactory.create(
                        item.get("type", "physical"),
                        item["id"],
                        item["name"],
                        item["price"],
                        item["stock"],
                        supplier,
                        weight=float(item.get("weight", 1.0)),
                        download_size=float(item.get("download_size", 100.0)),
                    )
                    inventory.add_product(prod)
                print("inventory.json found.")
                print("Inventory loaded successfully.")
                return inventory, suppliers
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    
    supplier = get_or_create_supplier(None, suppliers)
    default_products = [
        ProductFactory.create("physical", "P001", "Laptop", 1200.00, 15, supplier, weight=2.3),
        ProductFactory.create("physical", "P002", "Mouse", 25.50, 40, supplier, weight=0.15),
        ProductFactory.create("digital", "P003", "Antivirus", 45.00, 25, supplier, download_size=250.0),
    ]
    for product in default_products:
        inventory.add_product(product)
    return inventory, suppliers


def save_inventory(inventory: Inventory):
    """Save the current inventory to inventory.json."""
    data = [product.to_dict() for product in inventory.products]
    with open(INVENTORY_FILE, "w") as file:
        json.dump(data, file, indent=2)


def add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    """Add a new product to the inventory."""
    print("\nSelect Product Type:")
    print("1. Physical Product")
    print("2. Digital Product")
    p_type = input("Enter choice (1 or 2): ").strip()

    if p_type not in ["1", "2"]:
        print("Invalid choice.")
        return

    product_id = input("Enter product ID: ").strip().upper()
    if inventory.find_product(product_id):
        print("A product with this ID already exists.")
        return

    name = input("Enter product name: ").strip().upper()
    try:
        price = get_positive_float("Enter price: ")
        stock = get_non_negative_int("Enter stock: ")

        sid = input("Enter supplier ID: ").strip().upper()
        if sid in suppliers:
            supplier = suppliers[sid]
        else:
            supplier_name = input("Enter supplier name: ").strip()
            supplier_email = input("Enter supplier email: ").strip()
            supplier = Supplier(sid, supplier_name, supplier_email)
            suppliers[sid] = supplier

        if p_type == "1":
            weight = get_positive_float("Enter weight in kg: ")
            new_product = ProductFactory.create("physical", product_id, name, price,
                                                stock, supplier, weight=weight)
        else:
            download_size = get_positive_float("Enter download size in MB: ")
            new_product = ProductFactory.create("digital", product_id, name, price,
                                                stock, supplier, download_size=download_size)

        inventory.add_product(new_product)
        print("Product added successfully.")
    except ValueError as e:
        print(f"Could not add product: {e}")

def update_stock(inventory: Inventory) -> None:
    """Update stock of an existing product."""
    product_id = input("Enter product ID: ").strip().upper()
    product = inventory.find_product(product_id)

    if product:
        try:
            new_stock = int(input("Enter new stock: ").strip())
            product.update_stock(new_stock)
        except ValueError as e:
            print(f"Invalid stock: {e}")
    else:
        print("Product not found.")


def search_product(inventory: Inventory) -> None:
    """Search for a product by ID or name."""
    search_value = input("Enter product ID or name: ").strip().upper()
    product = inventory.search_product(search_value)

    if product:
        product.display_information()
        product.supplier.display_information()   
    else:
        print("Product not found.")

def remove_product(inventory: Inventory) -> None:
    product_id = input("Enter product ID to remove: ").strip().upper()
    removed = inventory.remove_product(product_id)
    if removed:
        print(f"{removed.name} removed from inventory (the product object still exists).")
    else:
        print("Product not found.")

def choose_discount() -> DiscountStrategy:
    """The MENU picks which strategy object to hand to Order. Order itself never decides."""
    print("Select discount:")
    print("1. No discount")
    print("2. 10% percentage discount")
    print("3. Bulk discount ($20 off orders of $200 or more)")
    print("4. Student discount (5%)")
    choice = input("Enter choice (1-4): ").strip()
    if choice == "2":
        return PercentageDiscount(10)
    elif choice == "3":
        return BulkDiscount(200, 20)
    elif choice == "4":
        return StudentDiscount()
    return NoDiscount()

def create_order(inventory: Inventory, order_count: int) -> None:
    order = Order(f"O{order_count:03d}", choose_discount())
    print(f"Creating order {order.order_id}. Type 'done' when finished.")
    while True:
        product_id = input("Enter product ID (or 'done'): ").strip().upper()
        if product_id == "DONE":
            break
        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue
        try:
            quantity = int(input("Enter quantity: ").strip())
            order.add_order_line(product, quantity)
        except ValueError as e:
            print(f"Invalid quantity: {e}")
            continue
        order.add_order_line(product, quantity)
    order.display_order()


def main() -> None:
    inventory, suppliers = load_inventory()
    order_count = 0  

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
        print("6. Remove Product")                                    
        print("7. Create Order")
        print("8. Load Products from CSV")
        print("9. Exit")                     
        print("---------------------------")

        choice = input("Enter option: ").strip().lower()

        if choice in ["exit", "quit", "9"]:
            save_inventory(inventory)
            print("Saving inventory before exit...")
            print("Inventory saved successfully.")
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        elif choice == "1":
            inventory.display_all_products()
        elif choice == "2":
            add_product(inventory, suppliers)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
            print("Inventory saved successfully.")
        elif choice == "6":                                            
            remove_product(inventory)
        elif choice == "7":
            order_count += 1
            create_order(inventory, order_count)
        elif choice == "8":
            load_products(PRODUCTS_CSV, inventory, DEFAULT_SUPPLIER)
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()