import csv
import io
from datetime import datetime, date
from flask import Blueprint, render_template, request, Response, send_file
from routes.auth import login_required
from models import db, Worker, Salary, Product, Production, Sale, Income, Expense, Tax, CompanySetting
from services.finance_service import FinanceService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

REPORT_TYPES = [
    ('workers', 'Worker Report'),
    ('salaries', 'Salary Report'),
    ('products', 'Product Inventory Report'),
    ('production', 'Production Report'),
    ('sales', 'Sales Report'),
    ('income', 'Income Report'),
    ('expenses', 'Expense Report'),
    ('taxes', 'Tax Report'),
    ('pnl', 'Profit & Loss Statement'),
    ('monthly_financial', 'Monthly Financial Report')
]

@reports_bp.route('/', methods=['GET'])
@login_required
def index():
    report_type = request.args.get('type', 'pnl')
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    search = request.args.get('search', '').strip()

    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    data = []
    totals = {}
    summary = None

    if report_type == 'workers':
        q = Worker.query
        if search:
            q = q.filter((Worker.name.ilike(f"%{search}%")) | (Worker.department.ilike(f"%{search}%")))
        data = q.all()
        totals['count'] = len(data)
        totals['total_salary'] = round(sum(w.monthly_salary for w in data), 2)

    elif report_type == 'salaries':
        q = Salary.query
        if start_date:
            q = q.filter(Salary.created_at >= start_date)
        if end_date:
            q = q.filter(Salary.created_at <= end_date)
        data = q.order_by(Salary.id.desc()).all()
        totals['count'] = len(data)
        totals['total_basic'] = round(sum(s.basic_salary for s in data), 2)
        totals['total_bonus'] = round(sum(s.bonus for s in data), 2)
        totals['total_deduction'] = round(sum(s.deduction for s in data), 2)
        totals['total_net'] = round(sum(s.net_salary for s in data), 2)

    elif report_type == 'products':
        q = Product.query
        if search:
            q = q.filter((Product.name.ilike(f"%{search}%")) | (Product.category.ilike(f"%{search}%")))
        data = q.all()
        totals['count'] = len(data)
        totals['total_quantity'] = sum(p.available_quantity for p in data)
        totals['inventory_value'] = round(sum(p.available_quantity * p.production_cost for p in data), 2)
        totals['sales_value'] = round(sum(p.available_quantity * p.selling_price for p in data), 2)

    elif report_type == 'production':
        q = Production.query
        if start_date:
            q = q.filter(Production.production_date >= start_date)
        if end_date:
            q = q.filter(Production.production_date <= end_date)
        data = q.order_by(Production.production_date.desc()).all()
        totals['count'] = len(data)
        totals['total_produced'] = sum(p.quantity_produced for p in data)
        totals['total_cost'] = round(sum(p.production_cost for p in data), 2)

    elif report_type == 'sales':
        q = Sale.query
        if start_date:
            q = q.filter(Sale.sale_date >= start_date)
        if end_date:
            q = q.filter(Sale.sale_date <= end_date)
        data = q.order_by(Sale.sale_date.desc()).all()
        totals['count'] = len(data)
        totals['total_quantity'] = sum(s.quantity for s in data)
        totals['total_amount'] = round(sum(s.total_amount for s in data), 2)

    elif report_type == 'income':
        q = Income.query
        if start_date:
            q = q.filter(Income.date >= start_date)
        if end_date:
            q = q.filter(Income.date <= end_date)
        data = q.order_by(Income.date.desc()).all()
        totals['count'] = len(data)
        totals['total_income'] = round(sum(i.amount for i in data), 2)

    elif report_type == 'expenses':
        q = Expense.query
        if start_date:
            q = q.filter(Expense.date >= start_date)
        if end_date:
            q = q.filter(Expense.date <= end_date)
        data = q.order_by(Expense.date.desc()).all()
        totals['count'] = len(data)
        totals['total_expense'] = round(sum(e.amount for e in data), 2)

    elif report_type == 'taxes':
        q = Tax.query
        if start_date:
            q = q.filter(Tax.due_date >= start_date)
        if end_date:
            q = q.filter(Tax.due_date <= end_date)
        data = q.order_by(Tax.due_date.desc()).all()
        totals['count'] = len(data)
        totals['total_tax'] = round(sum(t.tax_amount for t in data), 2)
        totals['paid_tax'] = round(sum(t.tax_amount for t in data if t.status == 'Paid'), 2)
        totals['pending_tax'] = round(sum(t.tax_amount for t in data if t.status == 'Pending'), 2)

    elif report_type in ['pnl', 'monthly_financial']:
        summary = FinanceService.get_financial_summary(start_date, end_date)

    settings = CompanySetting.get_settings()

    return render_template(
        'reports.html',
        report_types=REPORT_TYPES,
        active_report=report_type,
        data=data,
        totals=totals,
        summary=summary,
        settings=settings,
        start_date=start_date_str,
        end_date=end_date_str,
        search=search,
        today=date.today().strftime('%Y-%m-%d')
    )

@reports_bp.route('/export/csv')
@login_required
def export_csv():
    report_type = request.args.get('type', 'sales')
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'workers':
        writer.writerow(['Worker ID', 'Name', 'Phone', 'Department', 'Designation', 'Joining Date', 'Monthly Salary', 'Status'])
        workers = Worker.query.all()
        for w in workers:
            writer.writerow([w.worker_id, w.name, w.phone, w.department, w.designation, w.joining_date, w.monthly_salary, w.status])

    elif report_type == 'products':
        writer.writerow(['Product ID', 'Name', 'Category', 'Size', 'Material', 'Cost', 'Selling Price', 'Available Stock', 'Min Stock', 'Status'])
        products = Product.query.all()
        for p in products:
            writer.writerow([p.product_id, p.name, p.category, p.size, p.material, p.production_cost, p.selling_price, p.available_quantity, p.minimum_stock, p.status])

    elif report_type == 'production':
        writer.writerow(['Production ID', 'Product', 'Date', 'Quantity Produced', 'Worker/Team', 'Production Cost', 'Quality', 'Status'])
        prods = Production.query.all()
        for pr in prods:
            writer.writerow([pr.production_id, pr.product.name if pr.product else '', pr.production_date, pr.quantity_produced, pr.worker_team, pr.production_cost, pr.quality_status, pr.status])

    elif report_type == 'sales':
        writer.writerow(['Invoice ID', 'Customer Name', 'Phone', 'Product', 'Quantity', 'Price', 'Total Amount', 'Date', 'Payment Status', 'Payment Method'])
        sales = Sale.query.all()
        for s in sales:
            writer.writerow([s.sale_id, s.customer_name, s.customer_phone, s.product.name if s.product else '', s.quantity, s.selling_price, s.total_amount, s.sale_date, s.payment_status, s.payment_method])

    elif report_type == 'salaries':
        writer.writerow(['Salary ID', 'Worker Name', 'Worker ID', 'Month', 'Basic Salary', 'Bonus', 'Deduction', 'Net Salary', 'Status', 'Payment Date'])
        salaries = Salary.query.all()
        for sl in salaries:
            writer.writerow([sl.salary_id, sl.worker.name if sl.worker else '', sl.worker.worker_id if sl.worker else '', sl.month, sl.basic_salary, sl.bonus, sl.deduction, sl.net_salary, sl.payment_status, sl.payment_date or ''])

    elif report_type == 'expenses':
        writer.writerow(['Expense ID', 'Category', 'Description', 'Amount', 'Date', 'Payment Method', 'Notes'])
        expenses = Expense.query.all()
        for e in expenses:
            writer.writerow([e.expense_id, e.category, e.description, e.amount, e.date, e.payment_method, e.notes or ''])

    elif report_type == 'taxes':
        writer.writerow(['Tax ID', 'Tax Type', 'Period', 'Amount', 'Due Date', 'Payment Date', 'Status'])
        taxes = Tax.query.all()
        for t in taxes:
            writer.writerow([t.tax_id, t.tax_type, t.tax_period, t.tax_amount, t.due_date, t.payment_date or '', t.status])

    elif report_type in ['pnl', 'monthly_financial']:
        summary = FinanceService.get_financial_summary(start_date, end_date)
        writer.writerow(['Metric', 'Amount (INR)'])
        writer.writerow(['Opening Balance', summary['opening_balance']])
        writer.writerow(['Product Sales Income', summary['product_sales_income']])
        writer.writerow(['Other Income', summary['other_income']])
        writer.writerow(['Total Income', summary['total_income']])
        writer.writerow(['---', '---'])
        for cat, amt in summary['category_expenses'].items():
            writer.writerow([f"Expense: {cat}", amt])
        writer.writerow(['---', '---'])
        writer.writerow(['Total Expenses', summary['total_expenses']])
        writer.writerow(['Net Profit', summary['net_profit']])
        writer.writerow(['Current Balance', summary['current_balance']])

    output.seek(0)
    filename = f"VSB_{report_type.upper()}_REPORT_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
