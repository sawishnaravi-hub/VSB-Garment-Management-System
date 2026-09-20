from datetime import datetime, date
from . import db

class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(25), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)  # quantity * selling_price
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_status = db.Column(db.String(20), nullable=False, default='Paid')  # Paid, Pending, Partial
    payment_method = db.Column(db.String(30), nullable=False, default='Cash')  # Cash, Bank Transfer, UPI, Cheque, Credit
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to income
    incomes = db.relationship('Income', backref='sale', cascade='all, delete-orphan', lazy=True)

    def calculate_total(self):
        self.total_amount = round(float(self.quantity) * float(self.selling_price), 2)
        return self.total_amount

    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'N/A',
            'quantity': self.quantity,
            'selling_price': self.selling_price,
            'total_amount': self.total_amount,
            'sale_date': self.sale_date.strftime('%Y-%m-%d') if self.sale_date else '',
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<Sale {self.sale_id} - {self.customer_name}>"
