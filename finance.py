from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from services.finance_service import FinanceService
from models import db, Income, Expense, CompanySetting

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/', methods=['GET'])
@login_required
@role_required('Admin', 'Accountant')
def index():
    view_type = request.args.get('view', 'all')  # daily, monthly, yearly, custom, all
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    today = date.today()
    start_date = None
    end_date = None

    if view_type == 'daily':
        start_date = today
        end_date = today
    elif view_type == 'monthly':
        start_date = today.replace(day=1)
        end_date = today
    elif view_type == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif view_type == 'custom':
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

    summary = FinanceService.get_financial_summary(start_date, end_date)

    # Incomes list in the period
    income_query = Income.query
    if start_date:
        income_query = income_query.filter(Income.date >= start_date)
    if end_date:
        income_query = income_query.filter(Income.date <= end_date)
    incomes = income_query.order_by(Income.date.desc(), Income.id.desc()).limit(50).all()

    # Expenses list in the period
    expense_query = Expense.query
    if start_date:
        expense_query = expense_query.filter(Expense.date >= start_date)
    if end_date:
        expense_query = expense_query.filter(Expense.date <= end_date)
    expenses = expense_query.order_by(Expense.date.desc(), Expense.id.desc()).limit(50).all()

    settings = CompanySetting.get_settings()

    return render_template(
        'finance.html',
        summary=summary,
        incomes=incomes,
        expenses=expenses,
        settings=settings,
        view_type=view_type,
        start_date=start_date_str or (start_date.strftime('%Y-%m-%d') if start_date else ''),
        end_date=end_date_str or (end_date.strftime('%Y-%m-%d') if end_date else ''),
        today=today.strftime('%Y-%m-%d')
    )

@finance_bp.route('/add-income', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def add_income():
    income_id = request.form.get('income_id', '').strip().upper()
    title = request.form.get('title', '').strip()
    source_type = request.form.get('source_type', 'Other Income').strip()
    amount_str = request.form.get('amount', '0').strip()
    date_str = request.form.get('date', '').strip()
    payment_method = request.form.get('payment_method', 'Cash').strip()
    notes = request.form.get('notes', '').strip()

    if not income_id or not title:
        flash('Income ID and Title are required.', 'danger')
        return redirect(url_for('finance.index'))

    existing = Income.query.filter_by(income_id=income_id).first()
    if existing:
        flash(f'Income ID {income_id} already exists.', 'danger')
        return redirect(url_for('finance.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Income amount must be greater than 0.', 'danger')
            return redirect(url_for('finance.index'))
    except ValueError:
        flash('Invalid amount.', 'danger')
        return redirect(url_for('finance.index'))

    inc_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    income = Income(
        income_id=income_id,
        title=title,
        source_type=source_type,
        amount=amount,
        date=inc_date,
        payment_method=payment_method,
        notes=notes
    )
    db.session.add(income)
    db.session.commit()
    flash(f'Income record {income_id} (₹{amount:,.2f}) added.', 'success')
    return redirect(url_for('finance.index'))

@finance_bp.route('/update-opening-balance', methods=['POST'])
@login_required
@role_required('Admin')
def update_opening_balance():
    bal_str = request.form.get('opening_balance', '0').strip()
    try:
        new_balance = float(bal_str)
        settings = CompanySetting.get_settings()
        settings.opening_balance = new_balance
        db.session.commit()
        flash(f'Company Opening Balance updated to ₹{new_balance:,.2f}.', 'success')
    except ValueError:
        flash('Invalid opening balance amount.', 'danger')

    return redirect(url_for('finance.index'))
