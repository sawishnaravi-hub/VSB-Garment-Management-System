from datetime import datetime, date
from . import db

class RawMaterial(db.Model):
    __tablename__ = 'raw_materials'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    material_type = db.Column(db.String(50), nullable=False, default='Fabric')
    supplier = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(20), nullable=False, default='Meters')  # Meters, Rolls, Gross, Pieces, Boxes, Kg
    cost_per_unit = db.Column(db.Float, nullable=False, default=0.0)
    total_cost = db.Column(db.Float, nullable=False, default=0.0)  # quantity * cost_per_unit
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    stock_status = db.Column(db.String(30), nullable=False, default='In Stock')  # In Stock, Low Stock, Out of Stock
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    expenses = db.relationship('Expense', backref='raw_material', lazy=True)

    def calculate_total_cost(self):
        self.total_cost = round(float(self.quantity) * float(self.cost_per_unit), 2)
        return self.total_cost

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'name': self.name,
            'material_type': self.material_type,
            'supplier': self.supplier,
            'quantity': self.quantity,
            'unit': self.unit,
            'cost_per_unit': self.cost_per_unit,
            'total_cost': self.total_cost,
            'purchase_date': self.purchase_date.strftime('%Y-%m-%d') if self.purchase_date else '',
            'stock_status': self.stock_status
        }

    def __repr__(self):
        return f"<RawMaterial {self.material_id} - {self.name}>"
