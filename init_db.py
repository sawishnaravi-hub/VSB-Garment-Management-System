import os
import sys
from datetime import datetime, date, timedelta

# Add parent directory to path so models and config can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from config import Config
from models import (
    db, User, Worker, Product, RawMaterial, Production,
    Sale, Income, Salary, Expense, Tax, CompanySetting
)

def create_app_for_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_verified_db_uri()
    db.init_app(app)
    return app

def seed_database():
    app = create_app_for_db()

    with app.app_context():
        print("[INIT DB] Creating database tables...")
        db.create_all()

        # 1. Seed Company Setting if empty
        if not CompanySetting.query.first():
            print("[INIT DB] Seeding Company Settings...")
            setting = CompanySetting(
                company_name="VSB Garment Manufacturing",
                opening_balance=500000.00,
                currency_symbol="₹",
                phone="+91 98765 43210",
                email="contact@vsbgarments.com",
                address="123 Textile Park, Garment Hub, Tirupur, Tamil Nadu 641602, India",
                gstin="33AAACV1234F1Z5"
            )
            db.session.add(setting)

        # 2. Seed Default Users
        if not User.query.first():
            print("[INIT DB] Seeding Users (Admin, Manager, Accountant)...")
            users_data = [
                ("admin", "admin123", "Admin", "Mr. V. Sundaramoorthy", "admin@vsbgarments.com"),
                ("manager", "manager123", "Manager", "Karthik Raja", "karthik@vsbgarments.com"),
                ("accountant", "accountant123", "Accountant", "Priya Natarajan", "priya@vsbgarments.com")
            ]
            for username, pwd, role, full_name, email in users_data:
                u = User(username=username, role=role, full_name=full_name, email=email)
                u.set_password(pwd)
                db.session.add(u)

        # 3. Seed 10 Representative Workers (50-100 factory scale across 7 departments)
        if not Worker.query.first():
            print("[INIT DB] Seeding 10 Representative Workers...")
            workers_data = [
                ("WKR-101", "Ramesh Kumar", "+91 98765 11001", "Cutting", "Senior Master Cutter", date(2023, 3, 15), 22000.00, "Active", "14 North Street, Tirupur"),
                ("WKR-102", "Suresh Balan", "+91 98765 11002", "Cutting", "Fabric Spreader & Cutter", date(2023, 6, 1), 17500.00, "Active", "8 Mill Road, Tirupur"),
                ("WKR-103", "Anitha Selvam", "+91 98765 11003", "Stitching", "Tailoring Supervisor", date(2022, 8, 10), 24000.00, "Active", "22 Gandhi Nagar, Tirupur"),
                ("WKR-104", "Murugan Velu", "+91 98765 11004", "Stitching", "Flatlock Machine Operator", date(2023, 1, 20), 19000.00, "Active", "55 Anna Nagar, Tirupur"),
                ("WKR-105", "Kavitha Raj", "+91 98765 11005", "Quality Checking", "Senior Quality Inspector", date(2023, 4, 5), 20000.00, "Active", "12 Kamaraj Nagar, Tirupur"),
                ("WKR-106", "Dinesh Kumar", "+91 98765 11006", "Quality Checking", "Inline QC Auditor", date(2023, 9, 12), 16500.00, "Active", "31 Park Road, Tirupur"),
                ("WKR-107", "Selvi Mani", "+91 98765 11007", "Ironing", "Steam Ironing Specialist", date(2023, 2, 18), 16000.00, "Active", "9 South Extension, Tirupur"),
                ("WKR-108", "Venkatesh P.", "+91 98765 11008", "Packing", "Packaging Team Lead", date(2022, 11, 1), 18000.00, "Active", "44 Ring Road, Tirupur"),
                ("WKR-109", "Arun Prakash", "+91 98765 11009", "Maintenance", "Textile Machine Mechanic", date(2023, 5, 10), 21000.00, "Active", "7 Industrial Area, Tirupur"),
                ("WKR-110", "Divya Lakshmi", "+91 98765 11010", "Administration", "HR & Shift Coordinator", date(2023, 1, 5), 23000.00, "Active", "3 Municipal Colony, Tirupur")
            ]
            for w in workers_data:
                worker = Worker(
                    worker_id=w[0], name=w[1], phone=w[2], department=w[3],
                    designation=w[4], joining_date=w[5], monthly_salary=w[6],
                    status=w[7], address=w[8]
                )
                db.session.add(worker)

        # 4. Seed Products (Covering required garment categories)
        if not Product.query.first():
            print("[INIT DB] Seeding Finished Garment Products...")
            products_data = [
                ("PRD-101", "Premium Combed Crew T-Shirt", "T-Shirts", "M", "100% Combed Cotton", 140.00, 299.00, 350, 50, "Active"),
                ("PRD-102", "Slim Fit Oxford Formal Shirt", "Formal Shirts", "L", "Cotton Rich Oxford", 260.00, 599.00, 180, 40, "Active"),
                ("PRD-103", "Stretch Denim Casual Jeans", "Jeans", "32", "Denim Spandex", 340.00, 799.00, 120, 30, "Active"),
                ("PRD-104", "School Uniform Checked Shirts", "School/College Uniforms", "S", "Poly-Cotton Twill", 130.00, 279.00, 220, 50, "Active"),
                ("PRD-105", "Breathable Dry-Fit Sports Polo", "Sportswear", "L", "Micro-Polyester", 160.00, 349.00, 15, 25, "Active"),  # Low stock item
                ("PRD-106", "Fleece Zip-Up Winter Hoodie", "Hoodies", "XL", "Cotton Fleece", 380.00, 899.00, 8, 20, "Active"),   # Low stock item
                ("PRD-107", "Pure Cotton Printed Kurti", "Ladies Kurtis", "M", "Mulmul Cotton", 210.00, 499.00, 95, 30, "Active"),
                ("PRD-108", "Corporate Chino Trousers", "Corporate Uniforms", "34", "Cotton Twill", 280.00, 649.00, 110, 25, "Active")
            ]
            for p in products_data:
                product = Product(
                    product_id=p[0], name=p[1], category=p[2], size=p[3],
                    material=p[4], production_cost=p[5], selling_price=p[6],
                    available_quantity=p[7], minimum_stock=p[8], status=p[9]
                )
                db.session.add(product)

        # 5. Seed 8 Standard Raw Materials
        if not RawMaterial.query.first():
            print("[INIT DB] Seeding 8 Standard Raw Materials...")
            materials_data = [
                ("MAT-101", "Cotton Fabric (180 GSM)", "Fabric", "Vardhman Textiles Ltd", 2500.0, "Meters", 95.00, date(2026, 8, 1), "In Stock"),
                ("MAT-102", "Polyester Fabric (Dry-Fit)", "Fabric", "Reliance Industries Polyester", 1800.0, "Meters", 75.00, date(2026, 8, 3), "In Stock"),
                ("MAT-103", "High Tensile Sewing Thread", "Trims", "Coats India Threads", 350.0, "Rolls", 65.00, date(2026, 8, 5), "In Stock"),
                ("MAT-104", "Polyester 4-Hole Shirt Buttons", "Accessories", "Standard Trims Co", 400.0, "Gross", 45.00, date(2026, 8, 8), "In Stock"),
                ("MAT-105", "Brass & Nylon Metallic Zippers", "Accessories", "YKK Zippers India", 1200.0, "Pieces", 18.00, date(2026, 8, 10), "In Stock"),
                ("MAT-106", "Woven Brand & Care Labels", "Trims", "Avery Dennison Labels", 5000.0, "Pieces", 2.50, date(2026, 8, 12), "In Stock"),
                ("MAT-107", "Transparent LDPE Packing Covers", "Packaging", "Supreme Polymers", 6000.0, "Pieces", 1.80, date(2026, 8, 15), "In Stock"),
                ("MAT-108", "Heavy Duty Corrugated Cartons", "Packaging", "PackWell Containers", 450.0, "Boxes", 55.00, date(2026, 8, 18), "In Stock")
            ]
            for m in materials_data:
                mat = RawMaterial(
                    material_id=m[0], name=m[1], material_type=m[2], supplier=m[3],
                    quantity=m[4], unit=m[5], cost_per_unit=m[6],
                    purchase_date=m[7], stock_status=m[8]
                )
                mat.calculate_total_cost()
                db.session.add(mat)

        db.session.commit()

        # 6. Seed Production Batches
        if not Production.query.first():
            print("[INIT DB] Seeding Production Batches...")
            tshirt = Product.query.filter_by(product_id="PRD-101").first()
            shirt = Product.query.filter_by(product_id="PRD-102").first()
            jeans = Product.query.filter_by(product_id="PRD-103").first()

            productions_data = [
                ("PRD-BATCH-101", tshirt.id, date(2026, 8, 10), 300, "Stitching Line A", "300m Cotton Fabric, 600m Thread", 42000.00, "Passed", "Completed", "Export grade batch"),
                ("PRD-BATCH-102", shirt.id, date(2026, 8, 14), 150, "Stitching Line B", "180m Oxford Fabric, 1500 Buttons", 39000.00, "Passed", "Completed", "Regular production run"),
                ("PRD-BATCH-103", jeans.id, date(2026, 8, 20), 100, "Stitching Line C", "150m Denim, 100 Zippers", 34000.00, "Passed", "Completed", "Finished washing process"),
                ("PRD-BATCH-104", tshirt.id, date(2026, 8, 25), 200, "Stitching Line A", "200m Cotton Fabric", 28000.00, "Minor Defects", "Quality Check", "Inspection ongoing"),
                ("PRD-BATCH-105", shirt.id, date(2026, 9, 1), 120, "Stitching Line B", "140m Fabric, 1200 Buttons", 31200.00, "Passed", "In Progress", "Currently at button holing")
            ]
            for pr in productions_data:
                prod = Production(
                    production_id=pr[0], product_id=pr[1], production_date=pr[2],
                    quantity_produced=pr[3], worker_team=pr[4], raw_material_used=pr[5],
                    production_cost=pr[6], quality_status=pr[7], status=pr[8], remarks=pr[9]
                )
                db.session.add(prod)

        # 7. Seed Sales and Associated Income
        if not Sale.query.first():
            print("[INIT DB] Seeding Sales & Auto Incomes...")
            tshirt = Product.query.filter_by(product_id="PRD-101").first()
            shirt = Product.query.filter_by(product_id="PRD-102").first()
            jeans = Product.query.filter_by(product_id="PRD-103").first()

            sales_data = [
                ("INV-1001", "Max Fashion Retail", "+91 94432 20001", tshirt.id, 80, 299.00, date(2026, 8, 12), "Paid", "Bank Transfer", "Retail outlet consignment"),
                ("INV-1002", "Pothys Textiles", "+91 94432 20002", shirt.id, 40, 599.00, date(2026, 8, 16), "Paid", "Bank Transfer", "Autumn formal order"),
                ("INV-1003", "Chennai Silks Ltd", "+91 94432 20003", jeans.id, 30, 799.00, date(2026, 8, 22), "Paid", "Cheque", "Branch supply"),
                ("INV-1004", "City Garments Wholesaler", "+91 94432 20004", tshirt.id, 50, 299.00, date(2026, 8, 28), "Partial", "Cash", "Advance received"),
                ("INV-1005", "Style Corner Boutique", "+91 94432 20005", shirt.id, 25, 599.00, date(2026, 9, 3), "Paid", "UPI", "Direct boutique order")
            ]
            for s in sales_data:
                total_amt = round(s[4] * s[5], 2)
                sale = Sale(
                    sale_id=s[0], customer_name=s[1], customer_phone=s[2],
                    product_id=s[3], quantity=s[4], selling_price=s[5],
                    total_amount=total_amt, sale_date=s[6], payment_status=s[7],
                    payment_method=s[8], notes=s[9]
                )
                db.session.add(sale)
                db.session.flush()

                # Record corresponding Income for paid/partial
                if s[7] in ['Paid', 'Partial']:
                    inc_amt = total_amt if s[7] == 'Paid' else round(total_amt * 0.5, 2)
                    inc = Income(
                        income_id=f"INC-{sale.id + 1000}",
                        sale_id=sale.id,
                        source_type="Product Sales",
                        title=f"Sale #{s[0]} - {s[1]}",
                        amount=inc_amt,
                        date=s[6],
                        payment_method=s[8],
                        notes=f"Auto generated from sale #{s[0]}"
                    )
                    db.session.add(inc)

            # Add an Other Income record (Scrap sale)
            other_inc = Income(
                income_id="INC-1050",
                source_type="Other Income",
                title="Yarn and Cotton Fabric Scrap Clearance Sale",
                amount=18500.00,
                date=date(2026, 8, 30),
                payment_method="Bank Transfer",
                notes="Bi-weekly factory textile waste sold to authorized recycling unit"
            )
            db.session.add(other_inc)

        # 8. Seed Worker Salaries and Automatic Expense Linking
        if not Salary.query.first():
            print("[INIT DB] Seeding Salaries and Expense Records...")
            w1 = Worker.query.filter_by(worker_id="WKR-101").first()
            w3 = Worker.query.filter_by(worker_id="WKR-103").first()
            w5 = Worker.query.filter_by(worker_id="WKR-105").first()
            w8 = Worker.query.filter_by(worker_id="WKR-108").first()

            salaries_data = [
                ("SAL-1001", w1.id, "2026-08", w1.monthly_salary, 1500.00, 500.00, date(2026, 8, 31), "Paid", "Bank Transfer"),
                ("SAL-1002", w3.id, "2026-08", w3.monthly_salary, 2000.00, 500.00, date(2026, 8, 31), "Paid", "Bank Transfer"),
                ("SAL-1003", w5.id, "2026-08", w5.monthly_salary, 1000.00, 400.00, date(2026, 8, 31), "Paid", "Bank Transfer"),
                ("SAL-1004", w8.id, "2026-08", w8.monthly_salary, 800.00, 300.00, None, "Pending", "Bank Transfer")
            ]
            for sl in salaries_data:
                net = round(sl[3] + sl[4] - sl[5], 2)
                salary = Salary(
                    salary_id=sl[0], worker_id=sl[1], month=sl[2], basic_salary=sl[3],
                    bonus=sl[4], deduction=sl[5], net_salary=net, payment_date=sl[6],
                    payment_status=sl[7], payment_method=sl[8]
                )
                db.session.add(salary)
                db.session.flush()

                if sl[7] == 'Paid':
                    w_obj = Worker.query.get(sl[1])
                    exp = Expense(
                        expense_id=f"EXP-SAL-{salary.id + 1000}",
                        category="Salary",
                        description=f"Payroll for {w_obj.name} ({w_obj.worker_id}) - {sl[2]}",
                        amount=net,
                        date=sl[6],
                        payment_method=sl[8],
                        salary_id=salary.id,
                        notes=f"Linked to salary slip {sl[0]}"
                    )
                    db.session.add(exp)

        # 9. Seed Company Expenses (Covering all categories)
        if not Expense.query.filter_by(category='Electricity').first():
            print("[INIT DB] Seeding Categorized Expenses...")
            expenses_data = [
                ("EXP-1001", "Electricity", "Factory & Loom Shed High-Tension Power Bill", 28500.00, date(2026, 8, 10), "Bank Transfer", "TANGEDCO Bill #78492"),
                ("EXP-1002", "Rent", "Factory Premises & Warehouse Lease", 45000.00, date(2026, 8, 1), "Bank Transfer", "Textile Park Plot 14 Lease"),
                ("EXP-1003", "Transport", "Freight Logistics: Fabric pickup & dispatch", 12400.00, date(2026, 8, 15), "Cash", "Sri Balaji Transport logistics"),
                ("EXP-1004", "Machine Maintenance", "Quarterly Overhaul of Overlock & Stitching Units", 9800.00, date(2026, 8, 18), "Bank Transfer", "Precision Sewing Machine Care"),
                ("EXP-1005", "Packaging", "Bulk Corrugated Export Cartons & Strapping", 7500.00, date(2026, 8, 22), "UPI", "PackWell Containers Ltd"),
                ("EXP-1006", "Office Expenses", "Stationery, ERP Software maintenance & tea service", 4200.00, date(2026, 8, 25), "Cash", "Monthly administrative supplies")
            ]
            for ed in expenses_data:
                exp = Expense(
                    expense_id=ed[0], category=ed[1], description=ed[2], amount=ed[3],
                    date=ed[4], payment_method=ed[5], notes=ed[6]
                )
                db.session.add(exp)

        # 10. Seed Taxes (GST, Corporate Tax, TDS)
        if not Tax.query.first():
            print("[INIT DB] Seeding Statutory Taxes...")
            taxes_data = [
                ("TAX-1001", "GST (Goods & Services Tax)", "July 2026", 18500.00, date(2026, 8, 20), date(2026, 8, 19), "Paid", "GSTR-3B Challan No. CIN33291"),
                ("TAX-1002", "GST (Goods & Services Tax)", "August 2026", 21200.00, date(2026, 9, 20), None, "Pending", "August GSTR-3B Assessment"),
                ("TAX-1003", "TDS (Tax Deducted at Source)", "August 2026", 4500.00, date(2026, 9, 7), date(2026, 9, 6), "Paid", "Challan 281 Payment"),
                ("TAX-1004", "Corporate Tax", "Q1 FY26-27", 35000.00, date(2026, 9, 15), None, "Pending", "Advance Tax Installment 2")
            ]
            for td in taxes_data:
                tax = Tax(
                    tax_id=td[0], tax_type=td[1], tax_period=td[2], tax_amount=td[3],
                    due_date=td[4], payment_date=td[5], status=td[6], notes=td[7]
                )
                db.session.add(tax)
                db.session.flush()

                if td[6] == 'Paid':
                    exp = Expense(
                        expense_id=f"EXP-TAX-{tax.id + 1000}",
                        category="Tax",
                        description=f"{td[1]} for {td[2]}",
                        amount=td[3],
                        date=td[5],
                        payment_method="Bank Transfer",
                        tax_id=tax.id,
                        notes=f"Linked to tax record {td[0]}"
                    )
                    db.session.add(exp)

        db.session.commit()
        print("[INIT DB] Database initialization and comprehensive sample seeding COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    seed_database()
