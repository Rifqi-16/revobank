from db.database import db
from datetime import datetime
from models.user import User


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(db.String(255), nullable=False)
    account_number = db.Column(db.String(255), unique=True, nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.0)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions_from = db.relationship(
        'Transaction', foreign_keys='Transaction.source_account_id', backref='source_account', lazy=True)
    transactions_to = db.relationship(
        'Transaction', foreign_keys='Transaction.destination_account_id', backref='destination_account', lazy=True)

    @staticmethod
    def to_response(account):
        """Convert account object to response format"""
        return {
            'id': account.id,
            'user_id': account.user_id,
            'account_type': account.account_type,
            'account_number': account.account_number,
            'balance': float(account.balance),
            'status': account.status,
            'created_at': account.created_at.isoformat() if account.created_at else None
        }
