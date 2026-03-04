from fastapi import APIRouter
from app.schemas.auth import LoginResponse, register_responses
from app.services.v1.auth import (
    create_agent,
    login,
    send_verification_otp,
    verify_user_otp,
    send_forgot_password_otp,
    reset_password_with_otp,
    logout,
    refresh_tokens,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


router.post("/register", summary="Register a new agent",
            status_code=201,
            responses=register_responses)(create_agent)

router.post("/login", summary="Login a agent", status_code=200,
            response_model=LoginResponse)(login)

router.post("/send-verification-otp", summary="Send verification OTP",
            status_code=200)(send_verification_otp)

router.post("/verify-otp", summary="Verify OTP", status_code=200)(verify_user_otp)
