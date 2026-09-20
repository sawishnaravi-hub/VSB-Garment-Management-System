from datetime import datetime, date
from . import db

class Worker(db.Model):
    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    # Departments: Cutting, Stitching, Quality Checking, Ironing, Packing, Maintenance, Administration
    designation = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.Date, nullable=False, default=date.today)
    monthly_salary = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active, Inactive, On Leave
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    salaries = db.relationship('Salary', backref='worker', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'worker_id': self.worker_id,
            'name': self.name,
            'phone': self.phone,
            'department': self.department,
            'designation': self.designation,
            'joining_date': self.joining_date.strftime('%Y-%m-%d') if self.joining_date else '',
            'monthly_salary': self.monthly_salary,
            'status': self.status,
            'address': self.address
        }

    def __repr__(self):
        return f"<Worker {self.worker_id} - {self.name}>"
