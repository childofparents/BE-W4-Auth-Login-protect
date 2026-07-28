# BE-W4-Auth-Login-protect
FlyRank BE Track W4 Assignment

# Secure Auth API

This project is a secure backend API built with Python and FastAPI, using Supabase Auth as the Identity Provider. It handles user sign-up, login, logout, and protects specific routes using JWT verification via a reusable dependency guard.

## Setup Instructions

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file based on `.env.example` and add your Supabase Project URL and anon key.

## How to Run

Start the server on localhost with this single command:
`fastapi dev main.py --port 8000`

## API Reference

| Route | Purpose | Auth Required? |
|-------|---------|----------------|
| `POST /auth/signup` | Create a new user account | No |
| `POST /auth/login` | Authenticate & return a JWT | No |
| `POST /auth/logout` | End the user's session | Yes (Bearer Token) |
| `GET /public/info` | Read public, open data | No |
| `GET /protected/profile` | Read private profile data | Yes (Bearer Token) |

## Swagger UI showing locked protected routes
![](https://github.com/childofparents/BE-W4-Auth-Login-protect/blob/6fa48f440075b82fe1f63df375f169cf0f0721d2/Swagger%20UI%20with%20padlocks%20next%20to%20protected%20routes.png)
