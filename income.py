from datetime import datetime, date
from . import db

class Income(db.Model):
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    income_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id', ondelete='SET NULL'), nullable=True)
    source_type = db.Column(db.String(50), nullable=False, default='Product Sales')  # Product Sales, Other Income, Scrap Sale, Contract Work
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(30), nullable=False, default='Cash')  # Cash, Bank Transfer, UPI, Cheque
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'income_id': self.income_id,
            'sale_id': self.sale_id,
            'source_type': self.source_type,
            'title': self.title,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d') if self.date else '',
            'payment_method': self.payment_method,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<Income {self.income_id} - {self.title}: {self.amount}>"
