from db.database import db
from models.user import User


def create_user(username, password, email, full_name=''):
    """
    Create a new user and add to database
    """
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'

    # Create new user
    new_user = User(username=username, password_hash=password,
                    email=email, full_name=full_name)
    db.session.add(new_user)
    db.session.commit()

    return new_user, None


def get_user_by_username(username):
    """
    Find a user by username
    """
    return User.query.filter_by(username=username).first()


def get_user_by_id(user_id):
    """
    Find a user by ID
    """
    return User.query.get(user_id)


def update_user(user_id, data):
    """
    Update user information
    """
    user = User.query.get(user_id)
    if not user:
        return None, 'User not found'

    # Update fields
    if 'email' in data:
        user.email = data['email']

    if 'full_name' in data:
        user.full_name = data['full_name']

    # Update in database
    db.session.commit()

    return user, None

    return user, None
