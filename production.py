from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Production, Product, Worker

production_bp = Blueprint('production', __name__, url_prefix='/production')

STATUS_CHOICES = ['In Progress', 'Completed', 'Quality Check', 'Rejected']
QUALITY_CHOICES = ['Passed', 'Minor Defects', 'Rejected']

@production_bp.route('/', methods=['GET'])
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    product_filter = request.args.get('product_id', '').strip()

    query = Production.query

    if status_filter and status_filter in STATUS_CHOICES:
        query = query.filter(Production.status == status_filter)

    if product_filter:
        try:
            p_id = int(product_filter)
            query = query.filter(Production.product_id == p_id)
        except ValueError:
            pass

    productions = query.order_by(Production.production_date.desc(), Production.id.desc()).all()
    products = Product.query.filter_by(status='Active').all()
    workers = Worker.query.filter_by(status='Active').all()

    last_prod = Production.query.order_by(Production.id.desc()).first()
    next_id = f"PRD-BATCH-{last_prod.id + 101 if last_prod else 101}"

    return render_template(
        'production.html',
        productions=productions,
        products=products,
        workers=workers,
        statuses=STATUS_CHOICES,
        qualities=QUALITY_CHOICES,
        selected_status=status_filter,
        selected_product=product_filter,
        next_id=next_id
    )

@production_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def add():
    production_id = request.form.get('production_id', '').strip().upper()
    product_id_str = request.form.get('product_id', '').strip()
    production_date_str = request.form.get('production_date', '').strip()
    quantity_str = request.form.get('quantity_produced', '0').strip()
    worker_team = request.form.get('worker_team', '').strip()
    raw_material_used = request.form.get('raw_material_used', '').strip()
    cost_str = request.form.get('production_cost', '0').strip()
    quality_status = request.form.get('quality_status', 'Passed').strip()
    status = request.form.get('status', 'In Progress').strip()
    remarks = request.form.get('remarks', '').strip()

    if not production_id or not product_id_str or not worker_team:
        flash('Production ID, Product, and Worker/Team are required.', 'danger')
        return redirect(url_for('production.index'))

    existing = Production.query.filter_by(production_id=production_id).first()
    if existing:
        flash(f'Production batch {production_id} already exists.', 'danger')
        return redirect(url_for('production.index'))

    try:
        product_id = int(product_id_str)
        product = Product.query.get_or_404(product_id)
        quantity_produced = int(quantity_str)
        production_cost = float(cost_str)
        if quantity_produced <= 0 or production_cost < 0:
            flash('Quantity produced must be greater than 0 and cost cannot be negative.', 'danger')
            return redirect(url_for('production.index'))
    except ValueError:
        flash('Invalid numeric inputs.', 'danger')
        return redirect(url_for('production.index'))

    production_date = datetime.strptime(production_date_str, '%Y-%m-%d').date() if production_date_str else date.today()

    production = Production(
        production_id=production_id,
        product_id=product.id,
        production_date=production_date,
        quantity_produced=quantity_produced,
        worker_team=worker_team,
        raw_material_used=raw_material_used,
        production_cost=production_cost,
        quality_status=quality_status,
        status=status,
        remarks=remarks
    )

    # Automated Inventory Trigger: When marked Completed, increase product stock!
    if status == 'Completed':
        product.available_quantity += quantity_produced
        flash(f'Production completed! Automatically added {quantity_produced} units to {product.name} stock (New Stock: {product.available_quantity}).', 'success')

    db.session.add(production)
    db.session.commit()

    if status != 'Completed':
        flash(f'Production batch {production_id} created successfully.', 'success')
    return redirect(url_for('production.index'))

@production_bp.route('/<int:id>/status', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def update_status(id):
    production = Production.query.get_or_404(id)
    new_status = request.form.get('status', '').strip()
    new_quality = request.form.get('quality_status', production.quality_status).strip()

    if new_status not in STATUS_CHOICES:
        flash('Invalid status choice.', 'danger')
        return redirect(url_for('production.index'))

    old_status = production.status
    production.quality_status = new_quality
    production.status = new_status

    # Stock adjustment logic
    product = Product.query.get(production.product_id)
    if product:
        if old_status != 'Completed' and new_status == 'Completed':
            product.available_quantity += production.quantity_produced
            flash(f'Batch marked Completed! Product stock increased by {production.quantity_produced} units (New Stock: {product.available_quantity}).', 'success')
        elif old_status == 'Completed' and new_status != 'Completed':
            # Revert stock if it was previously counted as completed
            product.available_quantity = max(0, product.available_quantity - production.quantity_produced)
            flash(f'Batch status reverted from Completed! Product stock reduced by {production.quantity_produced} units.', 'warning')

    db.session.commit()
    return redirect(url_for('production.index'))

@production_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    production = Production.query.get_or_404(id)
    # If it was completed, adjust stock
    if production.status == 'Completed':
        product = Product.query.get(production.product_id)
        if product:
            product.available_quantity = max(0, product.available_quantity - production.quantity_produced)
    
    batch_id = production.production_id
    db.session.delete(production)
    db.session.commit()
    flash(f'Production batch {batch_id} deleted.', 'info')
    return redirect(url_for('production.index'))
