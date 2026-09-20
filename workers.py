from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Worker, Salary

workers_bp = Blueprint('workers', __name__, url_prefix='/workers')

DEPARTMENTS = [
    'Cutting',
    'Stitching',
    'Quality Checking',
    'Ironing',
    'Packing',
    'Maintenance',
    'Administration'
]

STATUSES = ['Active', 'Inactive', 'On Leave']

@workers_bp.route('/', methods=['GET'])
@login_required
@role_required('Admin', 'Manager')
def index():
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('department', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Worker.query

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Worker.name.ilike(search_pattern)) |
            (Worker.worker_id.ilike(search_pattern)) |
            (Worker.phone.ilike(search_pattern)) |
            (Worker.designation.ilike(search_pattern))
        )

    if dept_filter and dept_filter in DEPARTMENTS:
        query = query.filter(Worker.department == dept_filter)

    if status_filter and status_filter in STATUSES:
        query = query.filter(Worker.status == status_filter)

    workers = query.order_by(Worker.id.asc()).all()

    # Generate next suggested ID
    last_worker = Worker.query.order_by(Worker.id.desc()).first()
    next_id = f"WKR-{last_worker.id + 101 if last_worker else 101}"

    return render_template(
        'workers.html',
        workers=workers,
        departments=DEPARTMENTS,
        statuses=STATUSES,
        search=search,
        selected_dept=dept_filter,
        selected_status=status_filter,
        next_id=next_id
    )

@workers_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def add():
    worker_id = request.form.get('worker_id', '').strip().upper()
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    department = request.form.get('department', '').strip()
    designation = request.form.get('designation', '').strip()
    joining_date_str = request.form.get('joining_date', '').strip()
    salary_str = request.form.get('monthly_salary', '0').strip()
    status = request.form.get('status', 'Active').strip()
    address = request.form.get('address', '').strip()

    if not worker_id or not name or not phone or not department or not designation:
        flash('Please fill in all required worker fields.', 'danger')
        return redirect(url_for('workers.index'))

    # Check for duplicate worker_id
    existing = Worker.query.filter_by(worker_id=worker_id).first()
    if existing:
        flash(f'Worker with ID {worker_id} already exists.', 'danger')
        return redirect(url_for('workers.index'))

    try:
        monthly_salary = float(salary_str)
        if monthly_salary < 0:
            flash('Salary cannot be negative.', 'danger')
            return redirect(url_for('workers.index'))
    except ValueError:
        flash('Invalid salary amount.', 'danger')
        return redirect(url_for('workers.index'))

    joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d').date() if joining_date_str else datetime.utcnow().date()

    worker = Worker(
        worker_id=worker_id,
        name=name,
        phone=phone,
        department=department,
        designation=designation,
        joining_date=joining_date,
        monthly_salary=monthly_salary,
        status=status,
        address=address
    )
    db.session.add(worker)
    db.session.commit()
    flash(f'Worker {name} ({worker_id}) added successfully!', 'success')
    return redirect(url_for('workers.index'))

@workers_bp.route('/<int:id>/edit', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def edit(id):
    worker = Worker.query.get_or_404(id)

    worker.name = request.form.get('name', worker.name).strip()
    worker.phone = request.form.get('phone', worker.phone).strip()
    worker.department = request.form.get('department', worker.department).strip()
    worker.designation = request.form.get('designation', worker.designation).strip()
    worker.status = request.form.get('status', worker.status).strip()
    worker.address = request.form.get('address', worker.address).strip()

    salary_str = request.form.get('monthly_salary', str(worker.monthly_salary)).strip()
    try:
        salary_val = float(salary_str)
        if salary_val >= 0:
            worker.monthly_salary = salary_val
    except ValueError:
        pass

    joining_date_str = request.form.get('joining_date', '').strip()
    if joining_date_str:
        try:
            worker.joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db.session.commit()
    flash(f'Worker {worker.name} updated successfully.', 'success')
    return redirect(url_for('workers.index'))

@workers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    worker = Worker.query.get_or_404(id)
    name = worker.name
    w_id = worker.worker_id
    db.session.delete(worker)
    db.session.commit()
    flash(f'Worker {name} ({w_id}) deleted successfully.', 'info')
    return redirect(url_for('workers.index'))

@workers_bp.route('/<int:id>/details')
@login_required
def details(id):
    worker = Worker.query.get_or_404(id)
    salaries = Salary.query.filter_by(worker_id=worker.id).order_by(Salary.id.desc()).all()
    return jsonify({
        'worker': worker.to_dict(),
        'salaries': [s.to_dict() for s in salaries]
    })
