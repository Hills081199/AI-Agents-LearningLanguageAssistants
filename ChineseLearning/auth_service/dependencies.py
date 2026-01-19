from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from database import get_supabase

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), supabase: Client = Depends(get_supabase)):
    """Verify JWT token and return current user."""
    token = credentials.credentials
    try:
        # Verify the token with Supabase
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)), supabase: Client = Depends(get_supabase)):
    """Optional authentication - returns None if no valid token provided."""
    if not credentials:
        return None
    try:
        user_response = supabase.auth.get_user(credentials.credentials)
        return user_response.user if user_response.user else None
    except:
        return None
