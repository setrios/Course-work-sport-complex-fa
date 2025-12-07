from __future__ import annotations

import secrets
from typing import List, Optional

from fastapi import Depends, Header, HTTPException, status

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
    "IPP": {"password": "111111", "role": "user"},
}
TOKENS = {}


class AuthService:
    def register(self, username: str, password: str, email: Optional[str] = None) -> dict:
        """Register new user with validation."""
        if not username or not username.strip():
            raise ValueError("Username is required")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if username in USERS:
            raise ValueError(f"Username '{username}' already exists")
        
        if not password or not password.strip():
            raise ValueError("Password is required")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        USERS[username] = {
            "password": password,
            "role": "user",
            "email": email
        }
        return {"status": "registered", "username": username, "role": "user"}

    def login(self, username: str, password: str) -> dict:
        """Login user with credentials validation."""
        if not username or not password:
            raise ValueError("Username and password are required")
        
        user = USERS.get(username)

        # Lazy sync from sport_data.json if user not in in-memory store
        if not user:
            try:
                import json
                from pathlib import Path
                sport_data_path = Path("data/sport_data.json")
                if sport_data_path.exists():
                    with open(sport_data_path, "r", encoding="utf-8") as f:
                        sport_data = json.load(f)
                    for client in sport_data.get("clients", []):
                        if client.get("username") == username and client.get("password"):
                            USERS[username] = {
                                "password": client.get("password"),
                                "role": "user",
                                "email": client.get("contact_info", {}).get("email"),
                            }
                            user = USERS[username]
                            break
            except Exception:
                # Ignore sync errors; will fall back to invalid creds
                pass

        if not user:
            raise ValueError("Invalid username or password")
        if user.get("password") != password:
            raise ValueError("Invalid username or password")
        
        token = secrets.token_urlsafe(32)
        TOKENS[token] = {"username": username, "role": user["role"]}
        return {"access_token": token, "token_type": "bearer", "role": user["role"]}

    def logout(self, authorization: Optional[str]) -> dict:
        """Logout user by invalidating token."""
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1]
            TOKENS.pop(token, None)
        return {"status": "logged_out"}

    def me(self, user: dict) -> dict:
        """Get current user information."""
        return {"username": user["username"], "role": user["role"]}


def require_user(authorization: Optional[str] = Header(None)):
    """Validate user token and return user info."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization format")
    
    try:
        token = authorization.split(" ", 1)[1]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
    
    user = TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    return user


def require_role(roles: List[str]):
    """Validate user has required role."""
    def checker(user=Depends(require_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied. Required roles: {', '.join(roles)}")
        return user
    return checker
