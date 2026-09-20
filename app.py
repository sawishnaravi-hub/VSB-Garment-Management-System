import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Dynamic database URI check (MySQL primary, SQLite fallback if local MySQL is offline)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_verified_db_uri()

    # Initialize SQLAlchemy ORM
    db.init_app(app)

    # Register Route Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.workers import workers_bp
    from routes.products import products_bp
    from routes.materials import materials_bp
    from routes.production import production_bp
    from routes.sales import sales_bp
    from routes.salaries import salaries_bp
    from routes.expenses import expenses_bp
    from routes.taxes import taxes_bp
    from routes.finance import finance_bp
    from routes.reports import reports_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(workers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(salaries_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(taxes_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Context processors for global template variables
    @app.context_processor
    def inject_global_variables():
        return {
            'now': datetime.now(timezone.utc),
            'app_version': '2.0',
            'company_title': 'VSB Garment Manufacturing'
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content_error="404 - Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', content_error="500 - Internal Server Error"), 500

    return app

if __name__ == '__main__':
    app = create_app()

    # Automatically create tables & seed initial sample data on first run
    with app.app_context():
        from database.init_db import seed_database
        seed_database()

    port = int(os.getenv('PORT', 5000))
    print(f"\n=======================================================")
    print(f" VSB GARMENT MANUFACTURING COMPANY MANAGEMENT SYSTEM ")
    print(f" Server active at: http://localhost:{port}")
    print(f" Login Credentials:")
    print(f"   - Admin:      admin / admin123")
    print(f"   - Manager:    manager / manager123")
    print(f"   - Accountant: accountant / accountant123")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
