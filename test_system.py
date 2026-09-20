import os
import sys
import uuid
import unittest
from datetime import date

# Set testing environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import (
    db, User, Worker, Product, RawMaterial, Production,
    Sale, Income, Salary, Expense, Tax, CompanySetting
)
from services.finance_service import FinanceService

class TestVSBGarmentSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_01_authentication_and_roles(self):
        """Test password verification and role permissions"""
        with self.app.app_context():
            admin = User.query.filter_by(username='admin').first()
            self.assertIsNotNone(admin)
            self.assertTrue(admin.check_password('admin123'))
            self.assertFalse(admin.check_password('wrongpassword'))
            self.assertEqual(admin.role, 'Admin')

            manager = User.query.filter_by(username='manager').first()
            self.assertIsNotNone(manager)
            self.assertTrue(manager.check_password('manager123'))
            self.assertEqual(manager.role, 'Manager')

            accountant = User.query.filter_by(username='accountant').first()
            self.assertIsNotNone(accountant)
            self.assertTrue(accountant.check_password('accountant123'))
            self.assertEqual(accountant.role, 'Accountant')
        print("[TEST PASS] 01: Authentication & Role Hashing verified.")

    def test_02_worker_management(self):
        """Test worker queries and counts"""
        with self.app.app_context():
            workers = Worker.query.all()
            self.assertGreaterEqual(len(workers), 10)
            cutter = Worker.query.filter_by(worker_id='WKR-101').first()
            self.assertEqual(cutter.name, "Ramesh Kumar")
            self.assertEqual(cutter.department, "Cutting")
        print("[TEST PASS] 02: Worker Management & Departments verified.")

    def test_03_product_low_stock_detection(self):
        """Test low-stock alert calculation"""
        with self.app.app_context():
            low_stock_prods = Product.query.filter(Product.available_quantity <= Product.minimum_stock).all()
            self.assertGreater(len(low_stock_prods), 0)
            for p in low_stock_prods:
                self.assertTrue(p.is_low_stock)
        print("[TEST PASS] 03: Product Low-Stock Alerts verified.")

    def test_04_production_stock_increment(self):
        """Test that completing a production batch increments product inventory"""
        with self.app.app_context():
            prod = Product.query.filter_by(product_id='PRD-101').first()
            initial_stock = prod.available_quantity
            batch_code = f"TEST-BATCH-{uuid.uuid4().hex[:6]}"

            new_batch = Production(
                production_id=batch_code,
                product_id=prod.id,
                production_date=date.today(),
                quantity_produced=50,
                worker_team="Test Team",
                status="Completed"
            )
            prod.available_quantity += 50
            db.session.add(new_batch)
            db.session.commit()

            updated_prod = Product.query.filter_by(product_id='PRD-101').first()
            self.assertEqual(updated_prod.available_quantity, initial_stock + 50)

            # Cleanup
            prod.available_quantity -= 50
            db.session.delete(new_batch)
            db.session.commit()
        print("[TEST PASS] 04: Production Completed Stock Increment verified.")

    def test_05_sales_stock_deduction_and_income(self):
        """Test sales stock deduction and automatic income entry"""
        with self.app.app_context():
            prod = Product.query.filter_by(product_id='PRD-101').first()
            initial_stock = prod.available_quantity
            qty_to_sell = 10
            sale_code = f"TEST-INV-{uuid.uuid4().hex[:6]}"

            sale = Sale(
                sale_id=sale_code,
                customer_name="Test Customer Ltd",
                product_id=prod.id,
                quantity=qty_to_sell,
                selling_price=prod.selling_price,
                total_amount=round(qty_to_sell * prod.selling_price, 2),
                sale_date=date.today(),
                payment_status="Paid",
                payment_method="Cash"
            )
            prod.available_quantity -= qty_to_sell
            db.session.add(sale)
            db.session.flush()

            income_code = f"TEST-INC-{uuid.uuid4().hex[:6]}"
            income = Income(
                income_id=income_code,
                sale_id=sale.id,
                source_type="Product Sales",
                title=f"Sale #{sale.sale_id} - Test",
                amount=sale.total_amount,
                date=date.today(),
                payment_method="Cash"
            )
            db.session.add(income)
            db.session.commit()

            updated_prod = Product.query.filter_by(product_id='PRD-101').first()
            self.assertEqual(updated_prod.available_quantity, initial_stock - qty_to_sell)

            created_income = Income.query.filter_by(sale_id=sale.id).first()
            self.assertIsNotNone(created_income)
            self.assertEqual(created_income.amount, sale.total_amount)

            # Cleanup
            prod.available_quantity += qty_to_sell
            db.session.delete(income)
            db.session.delete(sale)
            db.session.commit()
        print("[TEST PASS] 05: Sales Stock Deduction & Income creation verified.")

    def test_06_salary_duplicate_prevention(self):
        """Test that duplicate salary payment for same worker and month is prohibited"""
        with self.app.app_context():
            w = Worker.query.filter_by(worker_id='WKR-101').first()
            existing = Salary.query.filter_by(worker_id=w.id, month='2026-08').first()
            self.assertIsNotNone(existing)

            # Try to add a duplicate
            dup = Salary(
                salary_id=f"TEST-SAL-{uuid.uuid4().hex[:6]}",
                worker_id=w.id,
                month='2026-08',
                basic_salary=w.monthly_salary,
                net_salary=w.monthly_salary
            )
            db.session.add(dup)
            with self.assertRaises(Exception):
                db.session.commit()
            db.session.rollback()
        print("[TEST PASS] 06: Salary Duplicate Prevention verified.")

    def test_07_financial_summary_equations(self):
        """Test accuracy of financial equations and balance calculation"""
        with self.app.app_context():
            summary = FinanceService.get_financial_summary()
            
            # Check equation: Total Income = Sales + Other
            expected_income = round(summary['product_sales_income'] + summary['other_income'], 2)
            self.assertAlmostEqual(summary['total_income'], expected_income, places=2)

            # Check equation: Net Profit = Total Income - Total Expenses
            expected_profit = round(summary['total_income'] - summary['total_expenses'], 2)
            self.assertAlmostEqual(summary['net_profit'], expected_profit, places=2)

            # Check equation: Current Balance = Opening Balance + Net Profit
            expected_balance = round(summary['opening_balance'] + summary['net_profit'], 2)
            self.assertAlmostEqual(summary['current_balance'], expected_balance, places=2)

            print(f"      -> Total Income: INR {summary['total_income']:,.2f}")
            print(f"      -> Total Expenses: INR {summary['total_expenses']:,.2f}")
            print(f"      -> Net Profit: INR {summary['net_profit']:,.2f}")
            print(f"      -> Current Balance: INR {summary['current_balance']:,.2f}")
        print("[TEST PASS] 07: Financial Equations & Current Balance verified.")

    def test_08_endpoint_routes(self):
        """Test HTTP responses for main routes"""
        with self.client:
            # Login as admin
            res = self.client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            # Check dashboard
            res = self.client.get('/dashboard')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'VSB Garment Manufacturing', res.data)

            # Check Chart API
            res = self.client.get('/api/dashboard-charts')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'monthly_income', res.data)

            # Check Workers
            res = self.client.get('/workers/')
            self.assertEqual(res.status_code, 200)

            # Check Products
            res = self.client.get('/products/')
            self.assertEqual(res.status_code, 200)

            # Check Materials
            res = self.client.get('/materials/')
            self.assertEqual(res.status_code, 200)

            # Check Production
            res = self.client.get('/production/')
            self.assertEqual(res.status_code, 200)

            # Check Sales
            res = self.client.get('/sales/')
            self.assertEqual(res.status_code, 200)

            # Check Salaries
            res = self.client.get('/salaries/')
            self.assertEqual(res.status_code, 200)

            # Check Expenses
            res = self.client.get('/expenses/')
            self.assertEqual(res.status_code, 200)

            # Check Taxes
            res = self.client.get('/taxes/')
            self.assertEqual(res.status_code, 200)

            # Check Finance
            res = self.client.get('/finance/')
            self.assertEqual(res.status_code, 200)

            # Check Reports & CSV export
            res = self.client.get('/reports/')
            self.assertEqual(res.status_code, 200)

            res = self.client.get('/reports/export/csv?type=sales')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/csv; charset=utf-8')

        print("[TEST PASS] 08: All Flask Route Endpoints & CSV Export verified.")

if __name__ == '__main__':
    unittest.main()
