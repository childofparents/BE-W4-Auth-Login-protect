import os
from fastapi import FastAPI, HTTPException, Header, Depends, Response
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

# Stage 4: Turns protected route logic into a reusable middleware dependency
def get_current_user(authorization: str = Header(default=None)):
    # 1. Extract the token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="Access token required")

    try:
        # 2. Ask Supabase whether it's real
        user_response = supabase.auth.get_user(token)
        # Return the verified user
        return user_response.user
    except Exception:
        # 3. Reject if expired, tampered with, or invalid
        raise HTTPException(status_code=401, detail="Invalid or expired token")

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
        # Call the Supabase sign-up method
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

        # On success, return 201 with the user object Supabase returns
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

# Stage 3 & 4: Use the dependency defined at top to create the protected route
# 2. Protected Endpoint (Verify user's access token)
@app.get("/protected/profile")
def protected_profile(user= Depends(get_current_user)):
    # The route body only runs AFTER the guard verifies the user
    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": str(user.created_at)
    }

# A brand new route using the same middleware
@app.get("/protected/dashboard")
def protected_dashboard(user = Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {user.email}!"}

# Stage 4: User log out protected route
@app.post("/auth/logout")
def logout(user = Depends(get_current_user)):
    # Call the sign-out method
    supabase.auth.sign_out()

    # Return 204 ("No Content") on success
    return Response(status_code=204)
