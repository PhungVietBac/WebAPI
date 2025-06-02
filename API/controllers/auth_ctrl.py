from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from datetime import timedelta
from jose import jwt
import auth
from supabase_client import supabase
from repositories.user_repo import get_user_by_id
import uuid
from dotenv import load_dotenv
import os
from urllib.parse import urlencode
import httpx
import uuid

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

# Scope yêu cầu
SCOPE = "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"

# Config security with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# API register user
@router.post("/register")
def register(username: str, password: str):
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")
    
    existing_user = supabase.table("users").select("*").eq("username", username).execute()

    if existing_user.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    
    hashed_pw = auth.hash_password(password)
    
    idUser = ""
    while not idUser or get_user_by_id(idUser):
        idUser = f"US{str(uuid.uuid4())[:4]}"
    
    response = supabase.table("users").insert({"iduser": idUser, "username": username, "password": hashed_pw, "role": 1}).execute()

    return response.data[0] if response.data else None

# API login user
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = supabase.table("users").select("*").eq("username", form_data.username).execute()
    if not user.data or not auth.verify_password(form_data.password, user.data[0]["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = auth.create_access_token({"sub": user.data[0]["iduser"], "role": user.data[0]["role"]}, timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        iduser: str = payload.get("sub")
        role: int = payload.get("role")
        if not iduser or role is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    return {"iduser": iduser, "role": role}

def require_role(roles: list[int]):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user
    return role_checker
    
def assert_owner_or_admin(user, target_id):
    if user["role"] != 0 and user["iduser"] != target_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    
@router.get("/google/login")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    }
     
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/google/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No code provided")
    
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_data = token_resp.json()
        
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get access token")
    
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = userinfo_resp.json()
        
    email = user_info["email"]
    name = user_info["name"]
    avatar = user_info["picture"]
    
    idUser = ""
    while not idUser or get_user_by_id(idUser):
        idUser = f"US{str(uuid.uuid4())[:4]}"
    
    new_user = {
        "iduser": idUser, 
        "name": name,
        "username": name,
        "password": None,
        "gender": 2,           
        "email": email,
        "phonenumber": None,   
        "avatar": avatar,
        "theme": 0,          
        "language": 0,
        "role": 1   
    }
    
    role = 1
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if not existing.data:
        supabase.table("users").insert(new_user).execute()
    else:
        idUser = existing.data[0]["iduser"]
        role = existing.data[0]["role"]
        
    access_token = auth.create_access_token({"sub": idUser, "role": role}, timedelta(minutes=30))
    return RedirectResponse(f"https://ai-trip-system.vercel.app/auth/callback?access_token={access_token}")