"""
OAuth2/JWT authentication module for peopleOS eBusiness Suite

Provides JWT token generation, validation, and refresh token management.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from jwt import PyJWTError as JWTError
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    """JWT token data payload"""

    user_id: int
    username: str
    email: str
    roles: list[str]
    exp: datetime


class Token(BaseModel):
    """Token response model"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def create_access_token(
    user_id: int, username: str, email: str, roles: list[str], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User identifier
        username: Username
        email: User email
        roles: List of user roles
        expires_delta: Token expiration time (defaults to 24 hours)

    Returns:
        JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "roles": roles,
        "type": "access",
        "exp": datetime.utcnow() + expires_delta,
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: int, username: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.

    Args:
        user_id: User identifier
        username: Username
        expires_delta: Token expiration time (defaults to 7 days)

    Returns:
        JWT token string
    """
    import uuid
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "user_id": user_id,
        "username": username,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "exp": datetime.utcnow() + expires_delta,
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        TokenData with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        roles: list[str] = payload.get("roles", [])
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))

        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        return TokenData(
            user_id=user_id, username=username, email=email, roles=roles, exp=exp
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency for extracting current user from token.

    Args:
        token: Bearer token from Authorization header

    Returns:
        TokenData for current user

    Raises:
        HTTPException: If token is invalid or expired
    """
    return verify_token(token, token_type="access")


def refresh_access_token(refresh_token: str, user_id: int, username: str, email: str, roles: list[str]) -> Token:
    """
    Generate new access token from refresh token.

    Args:
        refresh_token: Valid refresh token
        user_id: User identifier
        username: Username
        email: User email
        roles: User roles

    Returns:
        New Token with access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    new_access_token = create_access_token(user_id, username, email, roles)
    new_refresh_token = create_refresh_token(user_id, username)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)
