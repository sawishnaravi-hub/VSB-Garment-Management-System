from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Product

products_bp = Blueprint('products', __name__, url_prefix='/products')

CATEGORIES = [
    'T-Shirts',
    'Formal Shirts',
    'Pants',
    'Jeans',
    'School/College Uniforms',
    'Sportswear',
    'Hoodies',
    'Kids Wear',
    'Ladies Kurtis',
    'Corporate Uniforms'
]

SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'Free Size']

@products_bp.route('/', methods=['GET'])
@login_required
def index():
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    low_stock_only = request.args.get('low_stock', '').strip()

    query = Product.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(pattern)) |
            (Product.product_id.ilike(pattern)) |
            (Product.material.ilike(pattern))
        )

    if category_filter and category_filter in CATEGORIES:
        query = query.filter(Product.category == category_filter)

    if low_stock_only == '1':
        query = query.filter(Product.available_quantity <= Product.minimum_stock)

    products = query.order_by(Product.id.asc()).all()

    last_product = Product.query.order_by(Product.id.desc()).first()
    next_id = f"PRD-{last_product.id + 101 if last_product else 101}"

    return render_template(
        'products.html',
        products=products,
        categories=CATEGORIES,
        sizes=SIZES,
        search=search,
        selected_category=category_filter,
        low_stock_only=low_stock_only,
        next_id=next_id
    )

@products_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def add():
    product_id = request.form.get('product_id', '').strip().upper()
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    size = request.form.get('size', 'M').strip()
    material = request.form.get('material', '').strip()
    production_cost_str = request.form.get('production_cost', '0').strip()
    selling_price_str = request.form.get('selling_price', '0').strip()
    available_qty_str = request.form.get('available_quantity', '0').strip()
    min_stock_str = request.form.get('minimum_stock', '10').strip()
    status = request.form.get('status', 'Active').strip()

    if not product_id or not name or not category:
        flash('Product ID, Name, and Category are required.', 'danger')
        return redirect(url_for('products.index'))

    existing = Product.query.filter_by(product_id=product_id).first()
    if existing:
        flash(f'Product ID {product_id} already exists.', 'danger')
        return redirect(url_for('products.index'))

    try:
        production_cost = float(production_cost_str)
        selling_price = float(selling_price_str)
        available_quantity = int(available_qty_str)
        minimum_stock = int(min_stock_str)

        if production_cost < 0 or selling_price < 0 or available_quantity < 0 or minimum_stock < 0:
            flash('Quantities and prices cannot be negative.', 'danger')
            return redirect(url_for('products.index'))
    except ValueError:
        flash('Invalid numeric values entered for costs or quantities.', 'danger')
        return redirect(url_for('products.index'))

    product = Product(
        product_id=product_id,
        name=name,
        category=category,
        size=size,
        material=material,
        production_cost=production_cost,
        selling_price=selling_price,
        available_quantity=available_quantity,
        minimum_stock=minimum_stock,
        status=status
    )
    db.session.add(product)
    db.session.commit()
    flash(f'Product {name} ({product_id}) added successfully!', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/edit', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def edit(id):
    product = Product.query.get_or_404(id)

    product.name = request.form.get('name', product.name).strip()
    product.category = request.form.get('category', product.category).strip()
    product.size = request.form.get('size', product.size).strip()
    product.material = request.form.get('material', product.material).strip()
    product.status = request.form.get('status', product.status).strip()

    try:
        product.production_cost = max(0.0, float(request.form.get('production_cost', product.production_cost)))
        product.selling_price = max(0.0, float(request.form.get('selling_price', product.selling_price)))
        product.available_quantity = max(0, int(request.form.get('available_quantity', product.available_quantity)))
        product.minimum_stock = max(0, int(request.form.get('minimum_stock', product.minimum_stock)))
    except ValueError:
        flash('Invalid numbers provided for price or stock.', 'danger')
        return redirect(url_for('products.index'))

    db.session.commit()
    flash(f'Product {product.name} updated successfully.', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/update-stock', methods=['POST'])
@login_required
@role_required('Admin', 'Manager')
def update_stock(id):
    product = Product.query.get_or_404(id)
    adj_type = request.form.get('adj_type', 'add')  # 'add' or 'set'
    qty_str = request.form.get('quantity', '0').strip()

    try:
        qty = int(qty_str)
        if adj_type == 'set':
            product.available_quantity = max(0, qty)
        else:
            product.available_quantity = max(0, product.available_quantity + qty)
        db.session.commit()
        flash(f'Stock for {product.name} updated to {product.available_quantity} units.', 'success')
    except ValueError:
        flash('Invalid quantity.', 'danger')

    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    product = Product.query.get_or_404(id)
    name = product.name
    p_id = product.product_id

    # Check for active sales or production references
    if product.sales or product.productions:
        flash(f'Cannot delete {name} because it has associated sales or production records.', 'warning')
        return redirect(url_for('products.index'))

    db.session.delete(product)
    db.session.commit()
    flash(f'Product {name} ({p_id}) deleted successfully.', 'info')
    return redirect(url_for('products.index'))

@products_bp.route('/<int:id>/details')
@login_required
def details(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())
