from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Expense

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

CATEGORIES = [
    'Raw Material',
    'Electricity',
    'Rent',
    'Transport',
    'Machine Maintenance',
    'Packaging',
    'Salary',
    'Tax',
    'Office Expenses',
    'Other'
]

PAYMENT_METHODS = ['Cash', 'Bank Transfer', 'UPI', 'Cheque']

@expenses_bp.route('/', methods=['GET'])
@login_required
@role_required('Admin', 'Accountant')
def index():
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    query = Expense.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Expense.expense_id.ilike(pattern)) |
            (Expense.description.ilike(pattern)) |
            (Expense.notes.ilike(pattern))
        )

    if category_filter and category_filter in CATEGORIES:
        query = query.filter(Expense.category == category_filter)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= end_date)
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total_amount = sum(e.amount for e in expenses)

    last_exp = Expense.query.order_by(Expense.id.desc()).first()
    next_id = f"EXP-{last_exp.id + 1001 if last_exp else 1001}"

    return render_template(
        'expenses.html',
        expenses=expenses,
        categories=CATEGORIES,
        payment_methods=PAYMENT_METHODS,
        search=search,
        selected_category=category_filter,
        start_date=start_date_str,
        end_date=end_date_str,
        total_amount=round(total_amount, 2),
        next_id=next_id,
        today=date.today().strftime('%Y-%m-%d')
    )

@expenses_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def add():
    expense_id = request.form.get('expense_id', '').strip().upper()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '0').strip()
    date_str = request.form.get('date', '').strip()
    payment_method = request.form.get('payment_method', 'Cash').strip()
    notes = request.form.get('notes', '').strip()

    if not expense_id or not category or not description:
        flash('Expense ID, Category, and Description are required.', 'danger')
        return redirect(url_for('expenses.index'))

    existing = Expense.query.filter_by(expense_id=expense_id).first()
    if existing:
        flash(f'Expense ID {expense_id} already exists.', 'danger')
        return redirect(url_for('expenses.index'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash('Expense amount must be greater than 0.', 'danger')
            return redirect(url_for('expenses.index'))
    except ValueError:
        flash('Invalid expense amount.', 'danger')
        return redirect(url_for('expenses.index'))

    exp_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    expense = Expense(
        expense_id=expense_id,
        category=category,
        description=description,
        amount=round(amount, 2),
        date=exp_date,
        payment_method=payment_method,
        notes=notes
    )
    db.session.add(expense)
    db.session.commit()
    flash(f'Expense {expense_id} ({category}: ₹{amount:,.2f}) recorded successfully.', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/<int:id>/edit', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def edit(id):
    expense = Expense.query.get_or_404(id)

    expense.category = request.form.get('category', expense.category).strip()
    expense.description = request.form.get('description', expense.description).strip()
    expense.payment_method = request.form.get('payment_method', expense.payment_method).strip()
    expense.notes = request.form.get('notes', expense.notes).strip()

    try:
        amount = float(request.form.get('amount', expense.amount))
        if amount > 0:
            expense.amount = round(amount, 2)
    except ValueError:
        pass

    date_str = request.form.get('date', '').strip()
    if date_str:
        try:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db.session.commit()
    flash(f'Expense {expense.expense_id} updated.', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    expense = Expense.query.get_or_404(id)
    exp_code = expense.expense_id
    db.session.delete(expense)
    db.session.commit()
    flash(f'Expense {exp_code} deleted.', 'info')
    return redirect(url_for('expenses.index'))
