import os
from fastapi import FastAPI
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

@app.get("/")
def read_root():
    return {"message": "Server running and connected to Supabase"}