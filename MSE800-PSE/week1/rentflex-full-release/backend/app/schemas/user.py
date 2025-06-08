from typing import Optional
from pydantic import BaseModel, EmailStr, model_validator, field_validator
import enum

class UserRole(str, enum.Enum):
    admin = "admin"
    customer = "customer"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.customer
    blocked: bool = False

class UserCreate(UserBase):
    password: str

    @field_validator('email', mode="before")
    @classmethod
    def email_required(cls, v):
        if v is None or v == "":
            raise ValueError("email field required")
        return v

    @field_validator('password', mode="before")
    @classmethod
    def password_required(cls, v):
        if v is None or v == "":
            raise ValueError("password field required")
        return v
    
    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        if len(v) < 6:
            raise ValueError("password too short")
        if not any(char in "!@#$%^&*()-_" for char in v):
            raise ValueError("password without special_char")
        return v

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def check_required_fields(self):
        if not self.email and not self.name:
            raise ValueError("Either email or name must be provided")
        return self

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # v2必须写这个

class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
