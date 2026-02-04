
# Core Platform API

Core Platform API is the centralized backend service that powers all current and future applications, websites and internal tools.

It provides:
- Authentication and authorization (JWT + Refresh Token)
- Role-based access control (Attendee, Manager, Core)
- User identity and profile management
- Secure, reusable APIs shared accorss multiple platforms

This API is designed to be stable, extensible and serve as the single source of truth for all platform services going forward.

Goal: To reduce duplication, improve security and provide a consistent backend foundation for all products of AWS Cloud Club LPU.

Repository: https://github.com/awscloudclublpu/core-platform-api.git

---

## Overview
Core Platform API is a robust, scalable, and secure API service designed & hosted by AWS Cloud Club at LPU. Built with FastAPI, it provides authentication, user management, and role-based access control for all current and future applications and tools within the Horizon ecosystem.

## Features
- JWT-based authentication (RS256, asymmetric keys)
- Role-based access control (Attendee, Manager, Core)
- Secure password hashing (bcrypt)
- Refresh token support with HTTP-only cookies
- Modular project structure for maintainability
- MongoDB integration for data persistence
- CORS policy for frontend integration
- Environment-based configuration

## Project Structure
```
main.py                # FastAPI app entry point
requirements.txt       # Python dependencies
.env                   # Environment variables (not committed)
core/
  auth/                # Authentication logic (JWT, dependencies)
db/                    # Database collections and indexes
models/                # Pydantic models for requests, responses, tokens
routers/               # API route definitions
```

## Getting Started
### Prerequisites
- Python 3.9+
- MongoDB instance (local or remote)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/awscloudclublpu/core-platform-api.git
   cd core-platform-api
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Copy `.env.example` to `.env` and fill in the required values (see below).

### Environment Variables
- `MONGO_URI` - MongoDB connection string
- `MONGO_DB_NAME` - Database name
- `JWT_PRIVATE_KEY` - RSA private key for signing JWTs
- `JWT_PUBLIC_KEY` - RSA public key for verifying JWTs
- `JWT_ISSUER` - JWT issuer string
- `JWT_AUDIENCE` - JWT audience string
- `ACCESS_TOKEN_TTL_MINUTES` - Access token expiry (minutes)

### Running the Application
```sh
python main.py
```
The API will be available at `http://localhost:8000` by default.

## API Documentation
Interactive API docs are available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security Best Practices
- Store secrets and keys securely (consider using a secrets manager in production)
- Restrict CORS origins in production
- Use HTTPS in production deployments
- Regularly update dependencies and monitor for vulnerabilities

## Contributing
Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.
