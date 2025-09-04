"""
Security utilities: password hashing/verification and JWT token management.
"""
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt, JWTError  # python-jose
from ..core.config import get_settings

# Simple salted hashing (for demo). In production, use passlib/bcrypt.
SALT_LENGTH = 16


def _get_salt() -> bytes:
    return os.urandom(SALT_LENGTH)


def _hash_password_with_salt(password: str, salt: bytes) -> str:
    """Hash password with salt using PBKDF2-HMAC-SHA256."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt.hex() + ":" + dk.hex()


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a plaintext password and return salted hash string."""
    salt = _get_salt()
    return _hash_password_with_salt(password, salt)


# PUBLIC_INTERFACE
def verify_password(password: str, salted_hash: str) -> bool:
    """Verify a plaintext password against a salted hash."""
    try:
        salt_hex, hash_hex = salted_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()
        return hmac.compare_digest(check, hash_hex)
    except Exception:
        return False


# PUBLIC_INTERFACE
def create_access_token(subject: str, extra_claims: Dict[str, Any] | None = None) -> str:
    """Create a signed JWT access token for the given subject (e.g., user_id)."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token, returning its payload."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
