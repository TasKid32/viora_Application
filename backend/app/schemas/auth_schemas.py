"""Auth schemas — User registration, login, and token models."""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    language: str = "en"
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
