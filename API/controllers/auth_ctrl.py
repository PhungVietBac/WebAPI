from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt
import auth
from supabase_client import supabase
from repositories.user_repo import get_user_by_id
import uuid

router = APIRouter()

# Config security with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

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

@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {"iduser": current_user["iduser"], "role": current_user["role"]}