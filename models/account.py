import uuid
import datetime

class Account:
    """
    Account model representing a bank account
    """
    @staticmethod
    def create(user_id, account_type, initial_balance=0.0):
        """
        Create a new account object
        """
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'account_type': account_type,
            'balance': initial_balance,
            'account_number': f"RB-{uuid.uuid4().hex[:8].upper()}",
            'status': 'active',
            'created_at': datetime.datetime.now().isoformat()
        }