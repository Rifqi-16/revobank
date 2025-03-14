# RevoBank API

## Overview
RevoBank API is a robust RESTful banking service built with Python and Flask. It provides secure banking operations including user authentication, account management, and transaction processing. The API is designed with simplicity and security in mind, making it ideal for banking applications requiring core financial functionalities.

## Features

### User Management
- Secure user registration and authentication using JWT
- User profile management
- Password protection and validation
- Email verification support

### Account Management
- Multiple account types (savings, checking)
- Account balance tracking
- Account creation and closure
- Account details retrieval

### Transaction Processing
- Secure money transfers between accounts
- Deposit and withdrawal operations
- Transaction history tracking
- Real-time balance updates

### Security
- JWT-based authentication
- Secure password hashing
- Protected endpoints
- Session management

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- UV package manager

### Setup Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/revou-fsse-oct24/milestone-3-Rifqi-16.git
   cd revobank-api
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Environment Setup:
   - Copy .env.example to .env
   - Configure environment variables:
     ```
     JWT_SECRET_KEY=your_secret_key
     PORT=8080
     ```

4. Start the server:
   ```bash
   python3 run.py
   ```

## API Documentation

### Authentication

#### Register New User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123",
  "email": "john@example.com",
  "full_name": "John Doe"
}

Response (200 OK):
{
  "id": "user123",
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-03-20T10:00:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}

Response (200 OK):
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "user123",
    "username": "johndoe"
  }
}
```

### Account Management

#### Create Account
```http
POST /accounts
Authorization: Bearer <token>
Content-Type: application/json

{
  "account_type": "savings",
  "initial_balance": 1000.00
}

Response (201 Created):
{
  "id": "acc123",
  "account_type": "savings",
  "balance": 1000.00,
  "created_at": "2024-03-20T10:30:00Z"
}
```

#### Get Account Details
```http
GET /accounts/{account_id}
Authorization: Bearer <token>

Response (200 OK):
{
  "id": "acc123",
  "account_type": "savings",
  "balance": 1000.00,
  "created_at": "2024-03-20T10:30:00Z",
  "transactions": [...]
}
```

### Transaction Operations

#### Create Transaction
```http
POST /transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "from_account_id": "acc123",
  "to_account_id": "acc456",
  "amount": 500.00,
  "description": "Rent payment"
}

Response (201 Created):
{
  "id": "txn789",
  "from_account_id": "acc123",
  "to_account_id": "acc456",
  "amount": 500.00,
  "description": "Rent payment",
  "status": "completed",
  "created_at": "2024-03-20T11:00:00Z"
}
```

## Testing

Run the test suite with coverage reporting:

```bash
uv run pytest --cov=.
```

Current test coverage: ~93%

## Error Handling

The API uses standard HTTP response codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message describing the error:
```json
{
  "error": "Invalid account ID",
  "status": 400
}
```