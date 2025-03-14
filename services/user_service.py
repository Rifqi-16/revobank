from db.database import users_db
from models.user import User

def create_user(username, password, email, full_name=''):
    """
    Create a new user and add to database
    """
    # Check if username already exists
    if any(user['username'] == username for user in users_db):
        return None, 'Username already exists'
    
    # Create new user
    new_user = User.create(username, password, email, full_name)
    users_db.append(new_user)
    
    return new_user, None

def get_user_by_username(username):
    """
    Find a user by username
    """
    return next((user for user in users_db if user['username'] == username), None)

def get_user_by_id(user_id):
    """
    Find a user by ID
    """
    return next((user for user in users_db if user['id'] == user_id), None)

def update_user(user_id, data):
    """
    Update user information
    """
    user = get_user_by_id(user_id)
    if not user:
        return None, 'User not found'
    
    # Update fields
    if 'email' in data:
        user['email'] = data['email']
    
    if 'full_name' in data:
        user['full_name'] = data['full_name']
    
    # Update in database
    for i, u in enumerate(users_db):
        if u['id'] == user_id:
            users_db[i] = user
            break
    
    return user, None