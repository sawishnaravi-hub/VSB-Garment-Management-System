from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models import db, CompanySetting, User

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def index():
    settings = CompanySetting.get_settings()
    users = User.query.order_by(User.id.asc()).all()

    if request.method == 'POST':
        action = request.form.get('action', 'company')

        if action == 'company':
            settings.company_name = request.form.get('company_name', settings.company_name).strip()
            settings.phone = request.form.get('phone', settings.phone).strip()
            settings.email = request.form.get('email', settings.email).strip()
            settings.address = request.form.get('address', settings.address).strip()
            settings.gstin = request.form.get('gstin', settings.gstin).strip()
            settings.currency_symbol = request.form.get('currency_symbol', settings.currency_symbol).strip()

            try:
                settings.opening_balance = float(request.form.get('opening_balance', settings.opening_balance))
            except ValueError:
                pass

            db.session.commit()
            flash('Company settings updated successfully.', 'success')
            return redirect(url_for('settings.index'))

        elif action == 'create_user':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            full_name = request.form.get('full_name', '').strip()
            role = request.form.get('role', 'Manager').strip()
            email = request.form.get('email', '').strip()

            if not username or not password or not full_name:
                flash('Username, Password, and Full Name are required.', 'danger')
                return redirect(url_for('settings.index'))

            existing = User.query.filter_by(username=username).first()
            if existing:
                flash(f'Username {username} already exists.', 'danger')
                return redirect(url_for('settings.index'))

            new_user = User(
                username=username,
                full_name=full_name,
                role=role,
                email=email
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash(f'User {username} ({role}) created successfully.', 'success')
            return redirect(url_for('settings.index'))

    return render_template('settings.html', settings=settings, users=users)
