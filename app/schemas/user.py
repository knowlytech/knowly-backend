from pydantic import BaseModel, EmailStr
from typing import Optional
class SignupSchema(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str





class LoginSchema(BaseModel):
    email: EmailStr
    password: str





class VerifyEmailSchema(BaseModel):
    email: EmailStr
    otp: str




class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str



class ResendOTPSchema(BaseModel):
    email: EmailStr



class UpdateProfileSchema(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None