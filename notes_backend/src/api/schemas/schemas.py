"""
Pydantic schemas for API requests and responses.
"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class Message(BaseModel):
    """Generic message schema."""
    message: str = Field(..., description="Informational message")


# Auth
class RegisterRequest(BaseModel):
    """Payload to register a new user."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Account password")


class LoginRequest(BaseModel):
    """Payload to request a login token."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Account password")


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type, always bearer")


class UserOut(BaseModel):
    """Public user details."""
    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


# Notes
class NoteBase(BaseModel):
    """Common fields for notes."""
    title: str = Field(..., description="Title of the note")
    content: Optional[str] = Field(default="", description="Body content of the note")


class NoteCreate(NoteBase):
    """Request body to create a note."""
    pass


class NoteUpdate(BaseModel):
    """Request body to update a note."""
    title: Optional[str] = Field(default=None, description="Title of the note")
    content: Optional[str] = Field(default=None, description="Body content of the note")


class NoteOut(NoteBase):
    """Note representation in responses."""
    id: int = Field(..., description="Note ID")
    owner_id: int = Field(..., description="ID of the owning user")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
