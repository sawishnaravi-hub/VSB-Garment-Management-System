from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Salary, Worker, Expense

salaries_bp = Blueprint('salaries', __name__, url_prefix='/salaries')

@salaries_bp.route('/', methods=['GET'])
@login_required
@role_required('Admin', 'Accountant')
def index():
    month_filter = request.args.get('month', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Salary.query

    if month_filter:
        query = query.filter(Salary.month == month_filter)

    if status_filter and status_filter in ['Paid', 'Pending']:
        query = query.filter(Salary.payment_status == status_filter)

    salaries = query.order_by(Salary.id.desc()).all()
    workers = Worker.query.filter_by(status='Active').order_by(Worker.name.asc()).all()

    # Generate next ID
    last_sal = Salary.query.order_by(Salary.id.desc()).first()
    next_id = f"SAL-{last_sal.id + 1001 if last_sal else 1001}"

    # Current month string default: YYYY-MM
    current_month = datetime.now().strftime('%Y-%m')

    return render_template(
        'salaries.html',
        salaries=salaries,
        workers=workers,
        selected_month=month_filter,
        selected_status=status_filter,
        next_id=next_id,
        current_month=current_month
    )

@salaries_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def add():
    salary_id = request.form.get('salary_id', '').strip().upper()
    worker_id_str = request.form.get('worker_id', '').strip()
    month = request.form.get('month', '').strip()  # Format: YYYY-MM
    bonus_str = request.form.get('bonus', '0').strip()
    deduction_str = request.form.get('deduction', '0').strip()
    payment_status = request.form.get('payment_status', 'Pending').strip()
    payment_method = request.form.get('payment_method', 'Bank Transfer').strip()
    payment_date_str = request.form.get('payment_date', '').strip()
    notes = request.form.get('notes', '').strip()

    if not salary_id or not worker_id_str or not month:
        flash('Salary ID, Worker, and Month are required.', 'danger')
        return redirect(url_for('salaries.index'))

    worker = Worker.query.get_or_404(int(worker_id_str))

    # CRITICAL RULE: Prevent duplicate salary payment for same worker and month
    existing = Salary.query.filter_by(worker_id=worker.id, month=month).first()
    if existing:
        flash(
            f'Duplicate salary record! A salary slip ({existing.salary_id}) for {worker.name} for month {month} already exists.',
            'danger'
        )
        return redirect(url_for('salaries.index'))

    try:
        bonus = max(0.0, float(bonus_str))
        deduction = max(0.0, float(deduction_str))
        basic_salary = float(worker.monthly_salary)
    except ValueError:
        flash('Invalid numeric inputs for salary components.', 'danger')
        return redirect(url_for('salaries.index'))

    net_salary = round(basic_salary + bonus - deduction, 2)
    if net_salary < 0:
        flash('Deductions cannot exceed basic salary + bonus.', 'danger')
        return redirect(url_for('salaries.index'))

    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date() if (payment_date_str and payment_status == 'Paid') else (date.today() if payment_status == 'Paid' else None)

    salary = Salary(
        salary_id=salary_id,
        worker_id=worker.id,
        month=month,
        basic_salary=basic_salary,
        bonus=bonus,
        deduction=deduction,
        net_salary=net_salary,
        payment_date=payment_date,
        payment_status=payment_status,
        payment_method=payment_method,
        notes=notes
    )
    db.session.add(salary)
    db.session.flush()

    # CRITICAL RULE: When marked Paid, add to company expenses!
    if payment_status == 'Paid':
        expense = Expense(
            expense_id=f"EXP-SAL-{salary.id + 1000}",
            category='Salary',
            description=f"Salary for {worker.name} ({worker.worker_id}) - Month {month}",
            amount=net_salary,
            date=payment_date or date.today(),
            payment_method=payment_method,
            salary_id=salary.id,
            notes=f"Linked to Salary {salary.salary_id}"
        )
        db.session.add(expense)

    db.session.commit()
    flash(f'Salary slip for {worker.name} ({month}) created successfully. Net: ₹{net_salary:,.2f}', 'success')
    return redirect(url_for('salaries.index'))

@salaries_bp.route('/<int:id>/pay', methods=['POST'])
@login_required
@role_required('Admin', 'Accountant')
def mark_paid(id):
    salary = Salary.query.get_or_404(id)
    if salary.payment_status == 'Paid':
        flash('This salary is already marked as Paid.', 'info')
        return redirect(url_for('salaries.index'))

    salary.payment_status = 'Paid'
    salary.payment_date = date.today()

    # Record company expense
    expense = Expense(
        expense_id=f"EXP-SAL-{salary.id + 1000}",
        category='Salary',
        description=f"Salary for {salary.worker.name} ({salary.worker.worker_id}) - Month {salary.month}",
        amount=salary.net_salary,
        date=salary.payment_date,
        payment_method=salary.payment_method,
        salary_id=salary.id,
        notes=f"Linked to Salary {salary.salary_id}"
    )
    db.session.add(expense)
    db.session.commit()

    flash(f'Salary {salary.salary_id} marked as Paid and added to company expenses.', 'success')
    return redirect(url_for('salaries.index'))

@salaries_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    salary = Salary.query.get_or_404(id)
    s_id = salary.salary_id
    db.session.delete(salary)
    db.session.commit()
    flash(f'Salary record {s_id} deleted.', 'info')
    return redirect(url_for('salaries.index'))
