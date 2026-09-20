from flask import Blueprint, render_template, jsonify, session
from routes.auth import login_required
from services.finance_service import FinanceService
from models import Product, Production, Sale, Worker

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_role = session.get('role', 'Admin')
    finance_data = FinanceService.get_financial_summary()
    
    # Recent activities
    recent_sales = Sale.query.order_by(Sale.sale_date.desc(), Sale.id.desc()).limit(5).all()
    recent_productions = Production.query.order_by(Production.production_date.desc(), Production.id.desc()).limit(5).all()
    low_stock_items = Product.query.filter(Product.available_quantity <= Product.minimum_stock).all()

    return render_template(
        'dashboard.html',
        role=user_role,
        stats=finance_data,
        recent_sales=recent_sales,
        recent_productions=recent_productions,
        low_stock_items=low_stock_items
    )

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def chart_data():
    data = FinanceService.get_dashboard_chart_data()
    return jsonify(data)
