from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt
import auth
from supabase_client import supabase

router = APIRouter()

# Config security with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

# API register user
@router.post("/register")
def register(username: str, password: str):
    existing_user = supabase.table("tokens").select("*").eq("username", username).execute()

    if existing_user.data:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = auth.hash_password(password)
    
    response = supabase.table("tokens").insert({"username": username, "hashed_password": hashed_pw}).execute()

    return response.data[0] if response.data else None

# API login user
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = supabase.table("tokens").select("*").eq("username", form_data.username).execute()
    if not user.data or not auth.verify_password(form_data.password, user.data[0]["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = auth.create_access_token({"sub": user.data[0]["username"]}, timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = supabase.table("tokens").select("*").eq("username", username).execute()
    if user.data is None:
        raise credentials_exception
    
    return user
    