from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Tax, Expense

taxes_bp = Blueprint('taxes', __name__, url_prefix='/taxes')

TAX_TYPES = [
    'GST (Goods & Services Tax)',
    'Corporate Tax',
    'TDS (Tax Deducted at Source)',
    'Property Tax',
    'Professional Tax',
    'Other'
]

STATUSES = ['Paid', 'Pending']

@taxes_bp.route('/', methods=['GET'])
@login_required
@role_required('Admin', 'Accountant')
def index():
    status_filter = request.args.get('status', '').strip()
    type_filter = request.args.get('tax_type', '').strip()

    query = Tax.query

    if status_filter and status_filter in STATUSES:
        query = query.filter(Tax.status == status_filter)

    if type_filter and type_filter in TAX_TYPES:
        query = query.filter(Tax.tax_type == type_filter)

    taxes = query.order_by(Tax.due_date.desc(), Tax.id.desc()).all()

    last_tax = Tax.query.order_by(Tax.id.desc()).first()
    next_id = f"TAX-{last_tax.id + 1001 if last_tax else 1001}"

    return render_template(
        'taxes.html',
        taxes=taxes,
        tax_types=TAX_TYPES,
        statuses=STATUSES,
        selected_status=status_filter,
        selected_type=type_filter,
        next_id=next_id,
        today=date.today().strftime('%Y-%m-%d')
    )

@taxes_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def add():
    tax_id = request.form.get('tax_id', '').strip().upper()
    tax_type = request.form.get('tax_type', '').strip()
    tax_period = request.form.get('tax_period', '').strip()
    amount_str = request.form.get('tax_amount', '0').strip()
    due_date_str = request.form.get('due_date', '').strip()
    payment_date_str = request.form.get('payment_date', '').strip()
    status = request.form.get('status', 'Pending').strip()
    notes = request.form.get('notes', '').strip()

    if not tax_id or not tax_type or not tax_period:
        flash('Tax ID, Type, and Period are required.', 'danger')
        return redirect(url_for('taxes.index'))

    existing = Tax.query.filter_by(tax_id=tax_id).first()
    if existing:
        flash(f'Tax record {tax_id} already exists.', 'danger')
        return redirect(url_for('taxes.index'))

    try:
        tax_amount = float(amount_str)
        if tax_amount <= 0:
            flash('Tax amount must be greater than 0.', 'danger')
            return redirect(url_for('taxes.index'))
    except ValueError:
        flash('Invalid tax amount.', 'danger')
        return redirect(url_for('taxes.index'))

    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else date.today()
    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date() if (payment_date_str and status == 'Paid') else (date.today() if status == 'Paid' else None)

    tax = Tax(
        tax_id=tax_id,
        tax_type=tax_type,
        tax_period=tax_period,
        tax_amount=tax_amount,
        due_date=due_date,
        payment_date=payment_date,
        status=status,
        notes=notes
    )
    db.session.add(tax)
    db.session.flush()

    # CRITICAL RULE: When marked Paid, include in company expenses
    if status == 'Paid':
        expense = Expense(
            expense_id=f"EXP-TAX-{tax.id + 1000}",
            category='Tax',
            description=f"{tax_type} for period {tax_period}",
            amount=tax_amount,
            date=payment_date or date.today(),
            payment_method='Bank Transfer',
            tax_id=tax.id,
            notes=f"Linked to Tax Record {tax_id}"
        )
        db.session.add(expense)

    db.session.commit()
    flash(f'Tax entry {tax_id} (₹{tax_amount:,.2f}) added successfully.', 'success')
    return redirect(url_for('taxes.index'))

@taxes_bp.route('/<int:id>/pay', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def mark_paid(id):
    tax = Tax.query.get_or_404(id)
    if tax.status == 'Paid':
        flash('Tax record is already marked as Paid.', 'info')
        return redirect(url_for('taxes.index'))

    tax.status = 'Paid'
    tax.payment_date = date.today()

    # Add to company expenses
    expense = Expense(
        expense_id=f"EXP-TAX-{tax.id + 1000}",
        category='Tax',
        description=f"{tax.tax_type} for period {tax.tax_period}",
        amount=tax.tax_amount,
        date=tax.payment_date,
        payment_method='Bank Transfer',
        tax_id=tax.id,
        notes=f"Linked to Tax Record {tax.tax_id}"
    )
    db.session.add(expense)
    db.session.commit()

    flash(f'Tax record {tax.tax_id} marked as Paid and added to company expenses.', 'success')
    return redirect(url_for('taxes.index'))

@taxes_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    tax = Tax.query.get_or_404(id)
    t_id = tax.tax_id
    db.session.delete(tax)
    db.session.commit()
    flash(f'Tax record {t_id} deleted.', 'info')
    return redirect(url_for('taxes.index'))
