import uuid
import datetime

class User:
    """
    User model representing a bank customer
    """
    @staticmethod
    def create(username, password, email, full_name=''):
        """
        Create a new user object
        """
        return {
            'id': str(uuid.uuid4()),
            'username': username,
            'password': password,  # In production, hash the password
            'email': email,
            'full_name': full_name,
            'created_at': datetime.datetime.now().isoformat()
        }
    
    @staticmethod
    def to_response(user):
        """
        Convert user object to response format (without password)
        """
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'created_at': user['created_at']
        }