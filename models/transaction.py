from db.database import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    source_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    destination_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(50), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def to_response(transaction):
        """Convert transaction object to response format"""
        return {
            'id': transaction.id,
            'source_account_id': transaction.source_account_id,
            'destination_account_id': transaction.destination_account_id,
            'amount': float(transaction.amount),
            'transaction_type': transaction.transaction_type,
            'description': transaction.description,
            'status': transaction.status,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None
        }
