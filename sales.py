from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, role_required
from models import db, Sale, Product, Income

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

PAYMENT_STATUSES = ['Paid', 'Pending', 'Partial']
PAYMENT_METHODS = ['Cash', 'Bank Transfer', 'UPI', 'Cheque', 'Credit']

@sales_bp.route('/', methods=['GET'])
@login_required
def index():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Sale.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Sale.sale_id.ilike(pattern)) |
            (Sale.customer_name.ilike(pattern)) |
            (Sale.customer_phone.ilike(pattern))
        )

    if status_filter and status_filter in PAYMENT_STATUSES:
        query = query.filter(Sale.payment_status == status_filter)

    sales = query.order_by(Sale.sale_date.desc(), Sale.id.desc()).all()
    products = Product.query.filter_by(status='Active').all()

    last_sale = Sale.query.order_by(Sale.id.desc()).first()
    next_id = f"INV-{last_sale.id + 1001 if last_sale else 1001}"

    return render_template(
        'sales.html',
        sales=sales,
        products=products,
        payment_statuses=PAYMENT_STATUSES,
        payment_methods=PAYMENT_METHODS,
        search=search,
        selected_status=status_filter,
        next_id=next_id
    )

@sales_bp.route('/add', methods=['POST'])
@login_required
@role_required('Admin', 'Manager', 'Accountant')
def add():
    sale_id = request.form.get('sale_id', '').strip().upper()
    customer_name = request.form.get('customer_name', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    product_id_str = request.form.get('product_id', '').strip()
    quantity_str = request.form.get('quantity', '1').strip()
    selling_price_str = request.form.get('selling_price', '0').strip()
    sale_date_str = request.form.get('sale_date', '').strip()
    payment_status = request.form.get('payment_status', 'Paid').strip()
    payment_method = request.form.get('payment_method', 'Cash').strip()
    notes = request.form.get('notes', '').strip()

    if not sale_id or not customer_name or not product_id_str:
        flash('Invoice ID, Customer Name, and Product selection are required.', 'danger')
        return redirect(url_for('sales.index'))

    existing = Sale.query.filter_by(sale_id=sale_id).first()
    if existing:
        flash(f'Invoice ID {sale_id} already exists.', 'danger')
        return redirect(url_for('sales.index'))

    try:
        product_id = int(product_id_str)
        product = Product.query.get_or_404(product_id)
        quantity = int(quantity_str)
        selling_price = float(selling_price_str) if float(selling_price_str) > 0 else product.selling_price

        if quantity <= 0:
            flash('Sale quantity must be at least 1.', 'danger')
            return redirect(url_for('sales.index'))
    except ValueError:
        flash('Invalid numeric inputs for quantity or selling price.', 'danger')
        return redirect(url_for('sales.index'))

    # Critical Business Rule: Validate available stock
    if product.available_quantity < quantity:
        flash(
            f'Insufficient stock! Requested: {quantity} units, but only {product.available_quantity} units available for {product.name}.',
            'danger'
        )
        return redirect(url_for('sales.index'))

    sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date() if sale_date_str else date.today()
    total_amount = round(quantity * selling_price, 2)

    # 1. Deduct product stock
    product.available_quantity -= quantity

    sale = Sale(
        sale_id=sale_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        product_id=product.id,
        quantity=quantity,
        selling_price=selling_price,
        total_amount=total_amount,
        sale_date=sale_date,
        payment_status=payment_status,
        payment_method=payment_method,
        notes=notes
    )
    db.session.add(sale)
    db.session.flush()

    # 2. Automatically record Income entry if payment is Paid or Partial
    if payment_status in ['Paid', 'Partial']:
        inc_amount = total_amount if payment_status == 'Paid' else round(total_amount * 0.5, 2)
        income_code = f"INC-{sale.id + 1000}"
        income = Income(
            income_id=income_code,
            sale_id=sale.id,
            source_type='Product Sales',
            title=f"Sale #{sale_id} - {customer_name} ({product.name})",
            amount=inc_amount,
            date=sale_date,
            payment_method=payment_method,
            notes=f"Payment received for invoice {sale_id}"
        )
        db.session.add(income)

    db.session.commit()
    flash(
        f'Sale #{sale_id} processed successfully! Stock reduced by {quantity} (Remaining: {product.available_quantity}). Total: ₹{total_amount:,.2f}',
        'success'
    )
    return redirect(url_for('sales.index'))

@sales_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
@role_required('Admin', 'Manager', 'Accountant')
def update_payment_status(id):
    sale = Sale.query.get_or_404(id)
    new_status = request.form.get('payment_status', sale.payment_status).strip()
    old_status = sale.payment_status

    if new_status in PAYMENT_STATUSES:
        sale.payment_status = new_status
        # Check income record
        existing_income = Income.query.filter_by(sale_id=sale.id).first()
        if new_status == 'Paid':
            if existing_income:
                existing_income.amount = sale.total_amount
            else:
                inc = Income(
                    income_id=f"INC-{sale.id + 1000}",
                    sale_id=sale.id,
                    source_type='Product Sales',
                    title=f"Sale #{sale.sale_id} - {sale.customer_name}",
                    amount=sale.total_amount,
                    date=date.today(),
                    payment_method=sale.payment_method
                )
                db.session.add(inc)
        db.session.commit()
        flash(f'Payment status for {sale.sale_id} updated to {new_status}.', 'success')
    return redirect(url_for('sales.index'))

@sales_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('Admin')
def delete(id):
    sale = Sale.query.get_or_404(id)
    # Restore stock
    product = Product.query.get(sale.product_id)
    if product:
        product.available_quantity += sale.quantity

    sale_code = sale.sale_id
    db.session.delete(sale)
    db.session.commit()
    flash(f'Sale {sale_code} deleted and {sale.quantity} units restored to stock.', 'info')
    return redirect(url_for('sales.index'))

@sales_bp.route('/<int:id>/invoice')
@login_required
def invoice(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sales_invoice_modal.html', sale=sale)
