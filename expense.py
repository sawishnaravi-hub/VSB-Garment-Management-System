from datetime import datetime, date
from . import db

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False)
    # Categories: Raw Material, Electricity, Rent, Transport, Machine Maintenance,
    # Packaging, Salary, Tax, Office Expenses, Other
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(30), nullable=False, default='Cash')  # Cash, Bank Transfer, UPI, Cheque
    salary_id = db.Column(db.Integer, db.ForeignKey('salaries.id', ondelete='SET NULL'), nullable=True)
    tax_id = db.Column(db.Integer, db.ForeignKey('taxes.id', ondelete='SET NULL'), nullable=True)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id', ondelete='SET NULL'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'expense_id': self.expense_id,
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d') if self.date else '',
            'payment_method': self.payment_method,
            'salary_id': self.salary_id,
            'tax_id': self.tax_id,
            'material_id': self.material_id,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<Expense {self.expense_id} - {self.category}: {self.amount}>"
