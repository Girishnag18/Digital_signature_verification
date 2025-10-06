# Digital Signature Application

A Flask-based web application for digital signature verification of PDF documents.

## Features

- **User Authentication**: Secure login/logout with Flask-Login
- **User Registration**: New user registration with password hashing
- **PDF Upload**: Upload PDF documents for signature verification
- **Digital Signature Verification**: Verify digital signatures in PDF documents
- **Admin Interface**: Flask-Admin interface for user and document management
- **Audit Logging**: Track all document operations
- **Rate Limiting**: Prevent abuse with Flask-Limiter
- **Responsive UI**: Bootstrap-based responsive interface

## Project Structure

```
digital_sign_application/
├── app/
│   ├── __init__.py          # App package initialization
│   ├── head.py              # Application factory and configuration
│   ├── models.py            # Database models (User, DocumentLog)
│   ├── routes.py            # Application routes and views
│   ├── forms.py             # WTForms form definitions
│   ├── admin.py             # Flask-Admin configuration
│   ├── create_db.py         # Database creation script
│   ├── instance/
│   │   └── config.py        # Instance-specific configuration
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/           # Jinja2 templates
│   └── utils/
│       ├── signature_verifier.py  # PDF signature verification
│       └── audit_logger.py        # Audit logging utilities
├── run.py                   # Application entry point
├── init_db.py              # Database initialization script
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd digital_sign_application
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Copy `.env.example` to `.env` and update the values:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_change_in_production
   DATABASE_URL=sqlite:///app/app.db
   PORT=5000
   ```

5. **Initialize the database**:
   ```bash
   python init_db.py
   ```

## Usage

1. **Start the application**:
   ```bash
   python run.py
   ```

2. **Access the application**:
   Open your browser and go to `http://localhost:5000`

3. **Default admin credentials**:
   - Username: `admin`
   - Password: `admin123`

## API Endpoints

- `GET /` - Redirect to login
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /dashboard` - User dashboard (requires login)
- `GET/POST /upload` - PDF upload and verification (requires login)
- `GET /logout` - User logout
- `GET /admin/` - Admin interface (requires admin privileges)

## Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password
- `email`: User email (optional)
- `is_admin`: Admin flag
- `is_active`: Active status
- `created_at`: Creation timestamp

### DocumentLog
- `id`: Primary key
- `document_name`: Name of the uploaded document
- `user_id`: Foreign key to User
- `action`: Action performed
- `timestamp`: Action timestamp
- `ip_address`: Client IP address

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- Rate limiting with Flask-Limiter
- Secure file uploads with filename sanitization
- Admin-only access controls

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python run.py
```

### Database Migrations

If you make changes to models, create and apply migrations:

```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

## Production Deployment

1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn
3. Set up a reverse proxy (nginx)
4. Use a production database (PostgreSQL, MySQL)
5. Configure proper logging
6. Set up SSL/TLS certificates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository.