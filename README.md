# VSB Garment Manufacturing Company Management System

A full-stack, enterprise-grade web application built in **Python 3**, **Flask**, **MySQL**, **SQLAlchemy ORM**, **Jinja2**, **Bootstrap 5**, and **Chart.js**.

Designed specifically for garment manufacturing enterprises (50–100 worker capacity) to manage production lines, inventory, worker payroll, sales invoicing, operational overheads, statutory taxation, and company balance accounting.

---

## Key Features

1. **Role-Based Access Control**:
   - **Admin**: Complete system control, master financial overview, system settings, user creation.
   - **Manager**: Factory operations, worker management, product stock, raw materials, production batches, sales.
   - **Accountant**: Payroll disbursement, expense logging, tax compliance, cash inflow/outflow, financial reports.
2. **Dynamic Dashboard & Visual Analytics**:
   - 8 dynamic KPI cards (Total Income, Expenses, Salary, Taxes, Units Produced, Net Profit, Balance, Active Workers).
   - 5 Chart.js charts: Monthly Income vs Expenses, Monthly Profit Trend, Product Sales Distribution, Expense Category Breakdown, and Production Quantity.
3. **Automated Inventory & Accounting Logic**:
   - **Production Completion**: Marking a production batch as `Completed` automatically adds produced units to finished garment stock.
   - **Sales Invoicing**: Immediate stock deduction with validation (blocks sale if stock is insufficient). Automatically creates corresponding `Income` records.
   - **Salary Protection**: Prevents duplicate salary payouts for the same worker and month. Automatically logs paid salaries as company expenses under `Salary`.
   - **Tax Integration**: Paid taxes automatically flow into company expenses under `Tax`.
4. **10 Comprehensive Report Modules with CSV Export**:
   - Worker Report, Salary Report, Product Inventory Valuation, Production Log, Sales Invoices, Income Audit, Expense Statement, Tax Compliance, Profit & Loss Statement, and Monthly Financial Summary.

---

## Financial Accounting Equations

All calculations are derived dynamically from verified database records:

$$\text{Total Income} = \text{Product Sales} + \text{Other Income}$$

$$\begin{aligned}
\text{Total Expenses} = &\ \text{Salary} + \text{Raw Material Cost} + \text{Electricity} + \text{Rent} \\
&+ \text{Transport} + \text{Machine Maintenance} + \text{Packaging} + \text{Tax} + \text{Other Expenses}
\end{aligned}$$

$$\text{Net Profit} = \text{Total Income} - \text{Total Expenses}$$

$$\text{Current Balance} = \text{Opening Balance} + \text{Net Profit}$$

---

## Default Demonstration Credentials

| Role | Username | Password | Default Redirect |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Executive Dashboard |
| **Manager** | `manager` | `manager123` | Operations Dashboard |
| **Accountant** | `accountant` | `accountant123` | Finance & Accounting |

---

## Installation & Setup Instructions

### 1. Prerequisites
- Python 3.10+ (Python 3.14 compatible)
- MySQL Server (via XAMPP, WAMP, Docker, or standalone MySQL Server)

### 2. Setup Virtual Environment (Optional but Recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
#### Option A: MySQL (Primary)
1. Ensure your MySQL server is running (e.g., via XAMPP control panel on port 3306).
2. Configure `.env` with your MySQL user and password:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=vsb_garment_management
   ```
3. Initialize the database and seed complete sample data:
   ```bash
   python database/init_db.py
   ```
   *(Alternatively, you can import `database/schema.sql` directly into phpMyAdmin or MySQL Workbench).*

#### Option B: Automatic Fallback (Zero Setup)
If MySQL is not active on your machine when you launch the application, the system automatically detects this and falls back to a local SQLite database (`vsb_garment_management.db`) so you can immediately explore and demonstrate all features without manual server installation.

### 5. Launch Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## Verification & Complete Business Flow

1. **Login**: Sign in as `admin` / `admin123`.
2. **Dashboard**: Observe dynamic KPI cards and 5 live Chart.js visualizations.
3. **Add Worker**: Navigate to **Workers** &rarr; click **Add New Worker**.
4. **Add Product**: Navigate to **Products** &rarr; click **Add New Product**.
5. **Add Raw Material**: Navigate to **Raw Materials** &rarr; record fabric with automatic expense logging.
6. **Create Production**: Navigate to **Production** &rarr; create a batch and update status to **Completed** &rarr; observe that finished product stock increases automatically.
7. **Process Sale**: Navigate to **Sales** &rarr; process an invoice &rarr; product stock decreases and an Income record is created.
8. **Disburse Salary**: Navigate to **Salary** &rarr; generate salary slip and click **Pay Now** &rarr; an Expense record under `Salary` is automatically added.
9. **Log Expenses**: Navigate to **Expenses** &rarr; record factory electricity or logistics overhead.
10. **Tax Remittance**: Navigate to **Taxes** &rarr; record GST and click **Remit** &rarr; Expense record under `Tax` is created.
11. **Review Finance**: Navigate to **Finance** &rarr; inspect Net Profit and Current Balance updated with live MySQL entries.
12. **Export Reports**: Navigate to **Reports** &rarr; select any of the 10 report tabs, filter by date, or download a CSV report.
