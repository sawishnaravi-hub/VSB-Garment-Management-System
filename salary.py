from datetime import datetime, date
from . import db

class Salary(db.Model):
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    salary_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)  # e.g., '2026-08' or 'August 2026'
    basic_salary = db.Column(db.Float, nullable=False, default=0.0)
    bonus = db.Column(db.Float, nullable=False, default=0.0)
    deduction = db.Column(db.Float, nullable=False, default=0.0)
    net_salary = db.Column(db.Float, nullable=False, default=0.0)  # basic + bonus - deduction
    payment_date = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(20), nullable=False, default='Pending')  # Paid, Pending
    payment_method = db.Column(db.String(30), nullable=False, default='Bank Transfer')  # Cash, Bank Transfer, Cheque
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    expenses = db.relationship('Expense', backref='salary_ref', cascade='all, delete-orphan', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('worker_id', 'month', name='uq_worker_month_salary'),
    )

    def calculate_net_salary(self):
        self.net_salary = round(float(self.basic_salary) + float(self.bonus) - float(self.deduction), 2)
        return self.net_salary

    def to_dict(self):
        return {
            'id': self.id,
            'salary_id': self.salary_id,
            'worker_id': self.worker_id,
            'worker_name': self.worker.name if self.worker else 'N/A',
            'worker_code': self.worker.worker_id if self.worker else 'N/A',
            'department': self.worker.department if self.worker else 'N/A',
            'month': self.month,
            'basic_salary': self.basic_salary,
            'bonus': self.bonus,
            'deduction': self.deduction,
            'net_salary': self.net_salary,
            'payment_date': self.payment_date.strftime('%Y-%m-%d') if self.payment_date else '',
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<Salary {self.salary_id} - Worker {self.worker_id} ({self.month}): {self.net_salary}>"
