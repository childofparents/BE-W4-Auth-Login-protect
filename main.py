import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from your .env file
load_dotenv()

# Grab the variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize FastAPI
app = FastAPI()

# Stage 0: Runs server and connects to Supabase with no errors
@app.get("/")
def read_root():
    return {"message": "Server running and connected to Supabase"}

# Stage 1: User signup and login
# Pydantic model to parse the JSON body
class UserCredentials(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup(credentials: UserCredentials):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        # Call the Supabase sign-up method[cite: 1]
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })

        # Safely extract user properties and convert the datetime to a string
        user_data = {
            "id": str(response.user.id),
            "email": response.user.email,
            "created_at": str(response.user.created_at)
        } if response.user else {}

        # On success, return 201 with the user object Supabase returns[cite: 1]
        return JSONResponse(
            status_code=201,
            content={"user": user_data}
        )

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.post("/auth/login")
def login(credentials: UserCredentials):
    # Validate empty fields -> 400
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        # Call the Supabase sign-in method
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        # On success, return 200 with the access token and refresh token
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception:
        # If Supabase rejects the credentials, return 401
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )


# Stage 2: The public and protected gates
# 1. Public Endpoint
@app.get("/public/info")
def public_info():
    # Returns a 200 OK automatically in FastAPI
    return {"message": "Welcome stranger! This info is public."}

# Stage 3
# 2. Protected Endpoint (Verify user's access token)
@app.get("/protected/profile")
def protected_profile(authorization: str = Header(default=None)):
    # 1. Extract the token from the header
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    # Extract the token (we will verify it in Stage 3)
    token = authorization.split(" ")[1]

    if not token:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )

    try:
        # 2. Ask Supabase whether it's real
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        # 4. If it verifies -> return 200 with safe metadata
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    except Exception:
        # 3. If expired, tampered with, or invalid -> return 401
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )