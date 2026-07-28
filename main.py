import os
from fastapi import FastAPI, HTTPException
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
    # Validate: if email or password is missing/empty string -> 400 Bad Request
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    # Call the Supabase sign-up method
    response = supabase.auth.sign_up({
        "email": credentials.email,
        "password": credentials.password
    })

    # On success, return 201 with the user object Supabase returns
    # (Supabase's AuthResponse can be converted to a dictionary)
    return JSONResponse(
        status_code=201,
        content=response.model_dump() if hasattr(response, 'model_dump') else response.dict()
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