from datetime import datetime
from . import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    # Categories: T-Shirts, Formal Shirts, Pants, Jeans, School/College Uniforms,
    # Sportswear, Hoodies, Kids Wear, Ladies Kurtis, Corporate Uniforms
    size = db.Column(db.String(20), nullable=False, default='M')  # XS, S, M, L, XL, XXL, Free Size
    material = db.Column(db.String(80), nullable=False, default='Cotton')
    production_cost = db.Column(db.Float, nullable=False, default=0.0)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    available_quantity = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock = db.Column(db.Integer, nullable=False, default=10)
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Discontinued
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    productions = db.relationship('Production', backref='product', lazy=True)
    sales = db.relationship('Sale', backref='product', lazy=True)

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.minimum_stock

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'size': self.size,
            'material': self.material,
            'production_cost': self.production_cost,
            'selling_price': self.selling_price,
            'available_quantity': self.available_quantity,
            'minimum_stock': self.minimum_stock,
            'status': self.status,
            'is_low_stock': self.is_low_stock
        }

    def __repr__(self):
        return f"<Product {self.product_id} - {self.name}>"
