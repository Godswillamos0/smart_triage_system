from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    user_id: Optional[str] = None
    role: Optional[str] = None


class ResetPasswordWithOTP(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class SendOTP(BaseModel):
    email: EmailStr


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


register_responses = {
    201: {
        "description": "User successfully registered",
        "content": {
            "application/json": {
                "example": {
                    "id": "27975a3b-092c-41d1-b39b-812acbbf76c4",
                    "email": "user@example.com",
                    "is_verified": False,
                },
            },
        },
    },
    400: {
        "description": "User already verified",
        "content": {
            "application/json": {
                "example": {"detail": "User already verified"}
            }
        }
    },
    401: {
        "description": "Invalid credentials",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid credentials"}
            }
        }
    },
}
