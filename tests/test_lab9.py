"""Automated tests for Lab 9 (Strategy, Factory, validation, exception handling).

Run from the project root with:
    python -m unittest discover -s tests -v
"""
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

# Make persistent_auditor importable when tests run from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from persistent_auditor import (
    Supplier, Product, PhysicalProduct, DigitalProduct, ProductFactory,
    Inventory, Order, OrderLine,
    DiscountStrategy, NoDiscount, PercentageDiscount, BulkDiscount, StudentDiscount,
    get_positive_float, load_products,
)

SUPPLIER = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.sg")


def make_order_of(total: float, discount=None) -> Order:
    """Helper: an order with one line whose subtotal equals `total`."""
    product = ProductFactory.create("physical", "P999", "Test", total, 10, SUPPLIER)
    order = Order("O001", discount)
    order.add_order_line(product, 1)
    return order


class TestStrategy(unittest.TestCase):
    def test_default_is_no_discount(self):
        order = make_order_of(250)
        self.assertIsInstance(order.discount, NoDiscount)
        self.assertEqual(order.calculate_total(), 250)

    def test_bulk_discount_250(self):
        order = make_order_of(250, BulkDiscount(200, 20))
        self.assertEqual(order.calculate_total(), 230)

    def test_bulk_discount_below_threshold(self):
        order = make_order_of(150, BulkDiscount(200, 20))
        self.assertEqual(order.calculate_total(), 150)

    def test_set_discount_changes_strategy(self):
        order = make_order_of(250, BulkDiscount(200, 20))
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225)

    def test_student_discount_added_without_changing_order(self):
        order = make_order_of(100, StudentDiscount())
        self.assertAlmostEqual(order.calculate_total(), 95)

    def test_new_strategy_works_with_unchanged_order(self):
        class HalfPrice(DiscountStrategy):          # brand-new strategy, Order untouched
            def apply(self, total):
                return total / 2
        order = make_order_of(80, HalfPrice())
        self.assertEqual(order.calculate_total(), 40)


class TestFactory(unittest.TestCase):
    def test_creates_physical(self):
        p = ProductFactory.create("physical", "P001", "Lamp", 25.0, 10, SUPPLIER, weight=1.5)
        self.assertIsInstance(p, PhysicalProduct)
        self.assertIsInstance(p, Product)
        self.assertEqual(p.weight, 1.5)

    def test_creates_digital(self):
        p = ProductFactory.create("digital", "D001", "App", 49.9, 100, SUPPLIER, download_size=12.5)
        self.assertIsInstance(p, DigitalProduct)
        self.assertEqual(p.download_size, 12.5)

    def test_unknown_type_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            ProductFactory.create("service", "S001", "Install", 30.0, 5, SUPPLIER)
        self.assertIn("Unknown product type", str(ctx.exception))


class TestValidation(unittest.TestCase):
    def test_price_must_be_positive(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P1", "Bad", 0, 5, SUPPLIER)
        with self.assertRaises(ValueError):
            ProductFactory.create("physical", "P1", "Bad", -5, 5, SUPPLIER)

    def test_stock_cannot_be_negative(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("digital", "D1", "Bad", 10, -1, SUPPLIER)

    def test_update_stock_rejects_negative(self):
        p = ProductFactory.create("physical", "P1", "Ok", 10, 5, SUPPLIER)
        with self.assertRaises(ValueError):
            p.update_stock(-3)
        self.assertEqual(p.stock, 5)          # unchanged after the failed update

    def test_order_quantity_must_be_positive(self):
        p = ProductFactory.create("physical", "P1", "Ok", 10, 5, SUPPLIER)
        with self.assertRaises(ValueError):
            OrderLine(p, 0)
        with self.assertRaises(ValueError):
            Order("O1").add_order_line(p, -2)

    def test_digital_product_follows_same_stock_rule(self):   # LSP
        with self.assertRaises(ValueError):
            DigitalProduct("D1", "App", 10, -1, SUPPLIER, 5.0)


class TestExceptionHandling(unittest.TestCase):
    @patch("builtins.input", side_effect=["abc", "-5", "12.50"])
    def test_get_positive_float_keeps_asking(self, _mock_input):
        with patch("sys.stdout", new_callable=StringIO) as out:
            value = get_positive_float("Enter price: ")
        self.assertEqual(value, 12.5)
        printed = out.getvalue()
        self.assertIn("Please enter a valid number, e.g. 12.50", printed)
        self.assertIn("Please enter a number greater than zero.", printed)

    def test_load_products_skips_bad_rows(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "products.csv")
        inventory = Inventory()
        with patch("sys.stdout", new_callable=StringIO) as out:
            load_products(path, inventory, SUPPLIER)
        self.assertEqual(len(inventory.products), 3)
        printed = out.getvalue()
        self.assertIn("3 products loaded.", printed)
        self.assertIn("Load attempt finished.", printed)
        self.assertIn("Unknown product type: service", printed)

    def test_load_products_missing_file(self):
        inventory = Inventory()
        with patch("sys.stdout", new_callable=StringIO) as out:
            load_products("does_not_exist.csv", inventory, SUPPLIER)
        self.assertEqual(len(inventory.products), 0)
        printed = out.getvalue()
        self.assertIn("Products file not found", printed)
        self.assertIn("Load attempt finished.", printed)
        self.assertNotIn("products loaded", printed)      # else block did NOT run


if __name__ == "__main__":
    unittest.main()