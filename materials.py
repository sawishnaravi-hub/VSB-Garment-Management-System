from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, RawMaterial, Expense

materials_bp = Blueprint('materials', __name__, url_prefix='/materials')

STANDARD_MATERIALS = [
    'Cotton Fabric',
    'Polyester Fabric',
    'Thread',
    'Buttons',
    'Zippers',
    'Labels',
    'Packing Covers',
    'Cartons'
]

UNITS = ['Meters', 'Rolls', 'Gross', 'Pieces', 'Boxes', 'Kg']
MATERIAL_TYPES = ['Fabric', 'Trims', 'Accessories', 'Packaging', 'Other']

@materials_bp.route('/', methods=['GET'])
@login_required
def index():
    search = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '').strip()

    query = RawMaterial.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (RawMaterial.name.ilike(pattern)) |
            (RawMaterial.material_id.ilike(pattern)) |
            (RawMaterial.supplier.ilike(pattern))
        )

    if type_filter and type_filter in MATERIAL_TYPES:
        query = query.filter(RawMaterial.material_type == type_filter)

    materials = query.order_by(RawMaterial.id.asc()).all()

    last_mat = RawMaterial.query.order_by(RawMaterial.id.desc()).first()
    next_id = f"MAT-{last_mat.id + 101 if last_mat else 101}"

    return render_template(
        'materials.html',
        materials=materials,
        standard_materials=STANDARD_MATERIALS,
        units=UNITS,
        material_types=MATERIAL_TYPES,
        search=search,
        selected_type=type_filter,
        next_id=next_id
    )

@materials_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def add():
    material_id = request.form.get('material_id', '').strip().upper()
    name = request.form.get('name', '').strip()
    material_type = request.form.get('material_type', 'Fabric').strip()
    supplier = request.form.get('supplier', '').strip()
    quantity_str = request.form.get('quantity', '0').strip()
    unit = request.form.get('unit', 'Meters').strip()
    cost_per_unit_str = request.form.get('cost_per_unit', '0').strip()
    purchase_date_str = request.form.get('purchase_date', '').strip()
    stock_status = request.form.get('stock_status', 'In Stock').strip()
    record_expense = request.form.get('record_expense') == '1'

    if not material_id or not name or not supplier:
        flash('Material ID, Name, and Supplier are required.', 'danger')
        return redirect(url_for('materials.index'))

    existing = RawMaterial.query.filter_by(material_id=material_id).first()
    if existing:
        flash(f'Material ID {material_id} already exists.', 'danger')
        return redirect(url_for('materials.index'))

    try:
        quantity = float(quantity_str)
        cost_per_unit = float(cost_per_unit_str)
        if quantity < 0 or cost_per_unit < 0:
            flash('Quantity and cost cannot be negative.', 'danger')
            return redirect(url_for('materials.index'))
    except ValueError:
        flash('Invalid numeric values entered.', 'danger')
        return redirect(url_for('materials.index'))

    purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else date.today()
    total_cost = round(quantity * cost_per_unit, 2)

    material = RawMaterial(
        material_id=material_id,
        name=name,
        material_type=material_type,
        supplier=supplier,
        quantity=quantity,
        unit=unit,
        cost_per_unit=cost_per_unit,
        total_cost=total_cost,
        purchase_date=purchase_date,
        stock_status=stock_status
    )
    db.session.add(material)
    db.session.flush()

    # Automatically record as raw material company expense if requested (default True)
    if record_expense and total_cost > 0:
        expense_code = f"EXP-MAT-{material.id + 1000}"
        expense = Expense(
            expense_id=expense_code,
            category='Raw Material',
            description=f"Purchase of {quantity} {unit} {name} from {supplier}",
            amount=total_cost,
            date=purchase_date,
            payment_method='Bank Transfer',
            material_id=material.id,
            notes=f"Linked to Raw Material {material_id}"
        )
        db.session.add(expense)

    db.session.commit()
    flash(f'Raw material {name} ({material_id}) added successfully! Total cost: ₹{total_cost:,.2f}', 'success')
    return redirect(url_for('materials.index'))

@materials_bp.route('/<int:id>/edit', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def edit(id):
    material = RawMaterial.query.get_or_404(id)

    material.name = request.form.get('name', material.name).strip()
    material.material_type = request.form.get('material_type', material.material_type).strip()
    material.supplier = request.form.get('supplier', material.supplier).strip()
    material.unit = request.form.get('unit', material.unit).strip()
    material.stock_status = request.form.get('stock_status', material.stock_status).strip()

    try:
        material.quantity = max(0.0, float(request.form.get('quantity', material.quantity)))
        material.cost_per_unit = max(0.0, float(request.form.get('cost_per_unit', material.cost_per_unit)))
        material.calculate_total_cost()
    except ValueError:
        flash('Invalid numbers for quantity or cost.', 'danger')
        return redirect(url_for('materials.index'))

    db.session.commit()
    flash(f'Material {material.name} updated successfully.', 'success')
    return redirect(url_for('materials.index'))

@materials_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    material = RawMaterial.query.get_or_404(id)
    name = material.name
    m_id = material.material_id
    db.session.delete(material)
    db.session.commit()
    flash(f'Material {name} ({m_id}) deleted successfully.', 'info')
    return redirect(url_for('materials.index'))
