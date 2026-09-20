from datetime import datetime, date
from . import db

class Tax(db.Model):
    __tablename__ = 'taxes'

    id = db.Column(db.Integer, primary_key=True)
    tax_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    tax_type = db.Column(db.String(60), nullable=False)  # GST, Corporate Tax, TDS, Property Tax, Professional Tax, Other
    tax_period = db.Column(db.String(50), nullable=False)  # e.g., 'Q1 2026', 'August 2026'
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    due_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Paid, Pending
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    expenses = db.relationship('Expense', backref='tax_ref', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'tax_id': self.tax_id,
            'tax_type': self.tax_type,
            'tax_period': self.tax_period,
            'tax_amount': self.tax_amount,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else '',
            'payment_date': self.payment_date.strftime('%Y-%m-%d') if self.payment_date else '',
            'status': self.status,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<Tax {self.tax_id} - {self.tax_type} ({self.tax_period}): {self.tax_amount}>"
