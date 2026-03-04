import json
from sqlalchemy.exc import IntegrityError
import time
from sqlalchemy import or_
from pydantic import BaseModel
from app.schemas.auth import (RegisterUserRequest, LoginRequest, 
                              ResetPasswordWithOTP, SendOTP, VerifyOTP)

from app.db.models import (
    SupportAgent, Tickets
)
from app.utils.token_config import TokenData
from app.utils.mail_config_smtp import send_mail
from fastapi import Depends, HTTPException, Request, Response, BackgroundTasks
from fastapi.security import (HTTPBearer, HTTPAuthorizationCredentials,)
from starlette.concurrency import run_in_threadpool
from app.db.dependencies import db_dependency
from passlib.context import CryptContext
from app.core.config import (SECRET_KEY, 
                        ALGORITHM, 
                        ACCESS_TOKEN_EXPIRE_MINUTES,
                        REFRESH_TOKEN_EXPIRE_DAYS,
                        OTP_EXPIRE_MINUTES,
                        )
from datetime import datetime, timedelta
from typing import Annotated, Literal
from app.utils.redis_config import set_key, get_key, delete_key


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=16384,   # 16 MB (default is 65536 = 64 MB)
    argon2__time_cost=3,
    argon2__parallelism=2,
)
oauth2_scheme =  HTTPBearer(description="Type your token, DO not type Bearer")

SECRET_KEY = SECRET_KEY
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)


async def get_current_user_from_cookie(
    request: Request,
    db: db_dependency
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # 1️⃣ CHECK IF TOKEN IS BLACKLISTED
    blacklisted = await get_key(request, f"blacklist:{token}")
    if blacklisted:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked. Please log in again."
        )

    # 2️⃣ DECODE TOKEN
    try:
        payload = TokenData.decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(SupportAgent).filter(SupportAgent.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    return {"username": user.email, 
            "id": user.id, 
            "is_verified": getattr(user, "is_verified", True), 
            "role": payload.get("role")}


user_cookie_dependency = Annotated[dict, Depends(get_current_user_from_cookie)]


async def create_agent(db: db_dependency, 
                       user: RegisterUserRequest):
    hashed_password = pwd_context.hash(user.password) # Placeholder function

    db_user = SupportAgent(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        is_verified=True #To be changed in production
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="User exists"
        )
    return {
        "id": db_user.id,
        "email": db_user.email,
        "is_verified": db_user.is_verified
    }
       

async def store_refresh_token(request: Request, token: str, user_id: str):
    key = f"refresh:{user_id}"
    value = token
    
    await set_key(
        request=request,
        key=key,
        value=value,
        exp=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )


def authenticate_user(email: str, 
                      password: str,
                      db: db_dependency):
    
    user = db.query(SupportAgent).filter(SupportAgent.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="User not verified")

    return {
        "email": user.email,
        "id": user.id,
        "name": user.name
    }

async def login(response: Response, request: Request,
                user: LoginRequest, db: db_dependency):
    user = await run_in_threadpool(authenticate_user, 
                                   user.email, 
                                   user.password,
                                   db)
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail=f"Incorrect username or password {user}")

    token = TokenData(user["email"])

    access_token = token.create_token(
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        user_id=user.get("id"),
        name=user.get("name")
    )

    refresh_token = token.create_token(
        expires=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        user_id=user.get("id"),
        name=user.get("name")
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax"
    )

    await store_refresh_token(request, refresh_token, user.get("id"))       

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.get("id")
    }


async def send_verification_otp(request: Request, 
                                user: SendOTP, 
                                db: db_dependency,
                                background_tasks: BackgroundTasks):
    user_model = db.query(SupportAgent).filter(SupportAgent.email == user.email).first()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    if user_model.is_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    otp = generate_otp()

    await set_key(
        request=request,
        key=f"otp:{user_model.id}",
        value=json.dumps({"otp": otp}),
        exp=timedelta(minutes=OTP_EXPIRE_MINUTES)
    )

    background_tasks.add_task(
        send_mail,
        user_model.email,
        "Account Verification",
        f"Your OTP is: {otp}"
    )
    return {"detail": "OTP sent"}

    
    
def generate_otp(num1=100000, num2=999999):
    import random
    return random.randint(num1, num2)
    
    
async def verify_user_otp(request: Request, user: VerifyOTP, db: db_dependency):
    
    user_model = db.query(SupportAgent).filter(SupportAgent.email == user.email).first()
    if not user_model:
        raise HTTPException(404, "User not found")

    
    key = f"otp:{user_model.id}"
    saved = await get_key(request, key)

    if not saved:
        raise HTTPException(status_code=400, detail="OTP expired")

    saved_otp = json.loads(saved)["otp"]
    

    if int(saved_otp) == int(user.otp):
        user_model.is_verified = True
        delete_key(request, key)
        db.commit()

        return {"detail": "Account verified successfully"}

    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")    

    
async def send_forgot_password_otp(
    request: Request,
    email: SendOTP,
    db: db_dependency,
    background_tasks: BackgroundTasks
):
    user_model = db.query(SupportAgent).filter(SupportAgent.email == email.email).first()

    if not user_model:
        raise HTTPException(status_code=404, detail="Email address not found")

    otp = generate_otp()

    await set_key(
        request=request,
        key=f"forgot_otp:{user_model.id}",
        value=json.dumps({"otp": otp}),
        exp=timedelta(minutes=OTP_EXPIRE_MINUTES)
    )

    background_tasks.add_task(
        send_mail,
        user_model.email,
        "Password Reset OTP",
        f"Use this OTP to reset your password: {otp}"
    )
   
    return {"detail": "OTP sent"}

    
async def reset_password_with_otp(
    request: Request,
    data: ResetPasswordWithOTP,
    db: db_dependency
):
    # Get user
    user_model = db.query(SupportAgent).filter(SupportAgent.email == data.email).first()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    # Load OTP from Redis
    key = f"forgot_otp:{user_model.id}"
    stored = await get_key(request, key)

    if not stored:
        raise HTTPException(status_code=400, detail="OTP expired")

    stored_otp = json.loads(stored)["otp"]

    # Validate OTP
    if int(stored_otp) == int(data.otp):
        # Update password
        hashed_pw = pwd_context.hash(data.new_password)
        user_model.hashed_password = hashed_pw

        db.commit()

        return {"detail": "Password reset successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")


async def refresh_tokens(
    request: Request,
    response: Response,
    db: db_dependency
):

    #get token from cookies 
    refresh_token = request.cookies.get("refresh_token")

    # 1 Check if refresh token exists in Redis
    # Instead of refresh:{refresh_token}, use refresh:{user_id}
    # But since we don’t know user_id yet, decode the JWT first.
    try:
        payload = TokenData.decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("id")
    email = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token payload")

    # 2 Validate refresh token against Redis
    redis_key = f"refresh:{user_id}"
    saved_refresh = await get_key(request, redis_key)

    if not saved_refresh or saved_refresh != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # 3 Fetch user from database
    user = db.query(SupportAgent).filter(SupportAgent.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 4 Generate NEW access token
    token_builder = TokenData(email)

    new_access_token = token_builder.create_token(
        expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        user_id=user.id,
        name=user.name
    )

    # 5 Generate NEW refresh token (ROTATION)
    new_refresh_token = token_builder.create_token(
        expires=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        user_id=user.id,
        name=user.name
    )

    # overide new token in cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax"
    )

    # 6 Save new refresh token in Redis (replace the old one)
    await set_key(
        request=request,
        key=f"refresh:{user.id}",
        value=new_refresh_token,
        exp=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user_id": user.id
    }
   
    
    
async def logout(
    request: Request,
    user: user_cookie_dependency,
    db: db_dependency
):
    # Get access token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")

    access_token = auth_header.split(" ")[1]
    payload = TokenData.decode_token(access_token)

    exp = payload.get("exp")
    if not exp:
        raise HTTPException(status_code=400, detail="Invalid token")

    ttl = exp - int(time.time())
    if ttl < 0:
        raise HTTPException(status_code=400, detail="Token already expired")

    # 1 BLACKLIST THE ACCESS TOKEN
    await set_key(
        request=request,
        key=f"blacklist:{access_token}",
        value="blacklisted",
        exp=ttl
    )

    # 2 DELETE THE USER'S REFRESH TOKEN FROM REDIS
    refresh_key = f"refresh:{user['id']}"
    saved_refresh = await get_key(request, refresh_key)

    if saved_refresh:
        delete_key(request, refresh_key)


    return {"detail": "Successfully logged out"}



    
