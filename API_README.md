# RevoBank API Documentation

A RESTful API for RevoBank, providing secure and efficient interactions between users and the banking system.

## Project Overview

This project implements a RESTful API for RevoBank with the following features:

- User Management: Create and manage user accounts
- Account Management: Create and manage bank accounts
- Transaction Management: Process deposits, withdrawals, and transfers
- Authentication: Secure access to API endpoints using JWT tokens

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Authenticate user and generate access token |

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user account |
| GET | `/users/me` | Retrieve the profile of the currently logged-in user |
| PUT | `/users/me` | Update the profile information of the currently logged-in user |

### Account Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts` | Retrieve a list of all accounts for the current user |
| GET | `/accounts/:id` | Retrieve details of a specific account by its ID |
| POST | `/accounts` | Create a new account |
| PUT | `/accounts/:id` | Update details of an existing account |
| DELETE | `/accounts/:id` | Delete an account |

### Transaction Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transactions` | Retrieve a list of all transactions for the current user |
| GET | `/transactions/:id` | Retrieve details of a specific transaction by its ID |
| POST | `/transactions` | Initiate a new transaction (deposit, withdrawal, or transfer) |

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Flask
- PyJWT

### Installation

1. Clone the repository

```bash
git clone <repository-url>
cd revobank-api
```

2. Install dependencies

```bash
pip install flask pyjwt
```

### Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:5000`.

## Authentication Flow

The authentication flow follows these steps:

1. User submits credentials (username and password)
2. System validates credentials
3. If valid, system generates a JWT token
4. Token is returned to the user
5. User includes token in subsequent requests in the Authorization header

## Transaction Handling Flow

The transaction handling flow follows these steps:

1. System validates the account
2. System verifies sufficient balance for withdrawals and transfers
3. System processes the transaction
4. System generates a transaction history record
5. System returns the transaction details

## Error Handling

The API uses appropriate HTTP status codes to indicate success, failure, or specific error conditions:

- 200: Success
- 201: Resource created
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource not found
- 409: Conflict
- 500: Internal server error

## Sample Data

The application includes sample data for testing:

- Sample user: username: `demo`, password: `password`
- Sample account: A savings account with a balance of 1000.0

## Security Considerations

- The API uses JWT tokens for authentication
- Passwords are stored in plain text for demonstration purposes only. In a production environment, passwords should be hashed.
- Account deletion is only allowed if the account has a zero balance

## License

This project is licensed under the MIT License.