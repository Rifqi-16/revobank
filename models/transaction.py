import uuid
import datetime

class Transaction:
    """
    Transaction model representing a bank transaction
    """
    @staticmethod
    def create(transaction_type, amount, source_account_id=None, destination_account_id=None):
        """
        Create a new transaction object
        """
        return {
            'id': str(uuid.uuid4()),
            'transaction_type': transaction_type,
            'amount': amount,
            'source_account_id': source_account_id,
            'destination_account_id': destination_account_id,
            'status': 'completed',
            'created_at': datetime.datetime.now().isoformat()
        }