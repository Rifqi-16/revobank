# RevoBank API

## Overview
RevoBank API is a robust RESTful banking service built with Python and Flask. It provides secure banking operations including user authentication, account management, and transaction processing. The API is designed with simplicity and security in mind, making it ideal for banking applications requiring core financial functionalities.

## Database Schema

### Users Table
- `id` (INT, Primary Key): Unique identifier for the user
- `username` (VARCHAR(255), Unique): Username for login
- `email` (VARCHAR(255), Unique): User's email address
- `password_hash` (VARCHAR(255)): Securely hashed user password
- `created_at` (DATETIME): Timestamp of user creation
- `updated_at` (DATETIME): Timestamp of user information update

### Accounts Table
- `id` (INT, Primary Key): Unique identifier for the account
- `user_id` (INT, Foreign Key): References Users.id
- `account_type` (VARCHAR(255)): Type of account (checking, savings)
- `account_number` (VARCHAR(255), Unique): Unique account number
- `balance` (DECIMAL(10, 2)): Current balance
- `created_at` (DATETIME): Timestamp of account creation
- `updated_at` (DATETIME): Timestamp of account information update

### Transactions Table
- `id` (INT, Primary Key): Unique identifier for the transaction
- `from_account_id` (INT, Foreign Key): Account initiating the transaction
- `to_account_id` (INT, Foreign Key): Account receiving the transaction
- `amount` (DECIMAL(10, 2)): Transaction amount
- `type` (VARCHAR(255)): Type of transaction (deposit, withdrawal, transfer)
- `description` (VARCHAR(255)): Optional transaction description
- `created_at` (DATETIME): Timestamp of transaction creation

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
- PostgreSQL 15 or higher
- Docker and Docker Compose (optional)

### Local Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/revou-fsse-oct24/milestone-3-Rifqi-16.git
   cd milestone-3-Rifqi-16
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Environment Setup:
   Create a .env file with the following variables:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/revobank
   SECRET_KEY=your_secret_key
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Start the server:
   ```bash
   python3 run.py
   ```

### Docker Setup
1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Initialize the database:
   ```bash
   docker-compose exec web flask db upgrade
   ```

The API will be available at `http://localhost:8080`

## Database Management

### Running Migrations
1. Generate a new migration:
   ```bash
   flask db migrate -m "description of changes"
   ```

2. Apply migrations:
   ```bash
   flask db upgrade
   ```

3. Rollback migrations:
   ```bash
   flask db downgrade
   ```

## API Documentation

Detailed API documentation is available in [API_README.md](API_README.md)

## Deployment

### Deploying to Koyeb

1. Install Koyeb CLI and login:
   ```bash
   curl -fsSL https://cli.koyeb.com/install.sh | bash
   koyeb login
   ```

2. Deploy the application:
   ```bash
   koyeb app create revobank
   koyeb service create main --app revobank --git github.com/your-username/revobank --git-branch main --port 8080
   ```

3. Set environment variables:
   ```bash
   koyeb service update main --env DATABASE_URL="your-database-url" --env SECRET_KEY="your-secret-key"
   ```

### Environment Variables for Production
- `DATABASE_URL`: PostgreSQL connection URL
- `SECRET_KEY`: Secret key for JWT token generation
- `FLASK_ENV`: Set to 'production'

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.