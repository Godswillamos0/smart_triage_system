from jose import ExpiredSignatureError, jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class TokenData:
    def __init__(self, username: str):
        self.username = username
        
    def create_token(self, expires: timedelta, user_id: str, name: str):
        expire_time = datetime.utcnow() + expires
        
        encode = {
            "sub": self.username,
            "id": user_id,
            "name": name,
            "exp": expire_time
        }
        
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    
    #decode token
    @staticmethod
    def decode_token(token: str):
        credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            return {
                "sub": username,
                "id": payload.get("id"),
                "name": payload.get("name"),
                "exp": payload.get("exp")
            }
            
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")

        except JWTError:
            raise credentials_exception
    
    
    # Add token to cookies
    @staticmethod
    def add_token_to_cookies(token: str, token_key: str, message= None, response=None):
        if response is None:
            response = JSONResponse(content={"message": f"{message}" or "Token set in cookies"})
        
        response.set_cookie(
            key=token_key,
            value=token,
            httponly=False,
            # max_age=3600,
            # expires=3600,
            secure=False,
            samesite="none"
        )
        
        return response
    
    # Remove token from cookies
    @staticmethod
    def remove_token_from_cookies():
        response = JSONResponse(content={"message": "Successfully logged out"})
        
        for key in ["access_token", "refresh_token"]:
            response.delete_cookie(key)
        return response
    