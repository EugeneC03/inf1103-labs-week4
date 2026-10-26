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

