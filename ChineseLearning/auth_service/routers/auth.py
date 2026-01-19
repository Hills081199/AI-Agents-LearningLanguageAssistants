import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from database import get_supabase
from models import SignUpRequest, SignInRequest, AuthResponse, UserProfile
from dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/signup", response_model=AuthResponse)
def signup(request: SignUpRequest, supabase: Client = Depends(get_supabase)):
    """Register a new user with email and password."""
    try:
        # SignUp with Supabase Auth
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "username": request.username
                }
            }
        })
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account. Please check your email for confirmation."
            )
        
        return AuthResponse(
            access_token=response.session.access_token,
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "username": request.username
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/signin", response_model=AuthResponse)
def signin(request: SignInRequest, supabase: Client = Depends(get_supabase)):
    """Sign in with email and password."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user_meta = response.user.user_metadata or {}
        
        return AuthResponse(
            access_token=response.session.access_token,
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "username": user_meta.get("username")
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/signout")
def signout(supabase: Client = Depends(get_supabase), current_user = Depends(get_current_user)):
    """Sign out the current user."""
    try:
        supabase.auth.sign_out()
        return {"message": "Successfully signed out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me", response_model=UserProfile)
def get_me(current_user = Depends(get_current_user)):
    """Get the current user's profile."""
    user_meta = current_user.user_metadata or {}
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        username=user_meta.get("username")
    )


@router.post("/reset-password")
def reset_password(email: str, supabase: Client = Depends(get_supabase)):
    """Send a password reset email."""
    try:
        supabase.auth.reset_password_email(email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh")
def refresh_token(refresh_token: str, supabase: Client = Depends(get_supabase)):
    """Refresh the access token."""
    try:
        response = supabase.auth.refresh_session(refresh_token)
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# ============== Google OAuth ==============

@router.get("/google/url")
def get_google_oauth_url(redirect_url: str = "http://localhost:3000/auth/callback", supabase: Client = Depends(get_supabase)):
    """Get Google OAuth URL for login. Frontend redirects user to this URL."""
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        return {"url": response.url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/google/callback")
def google_callback(access_token: str, refresh_token: str = None, supabase: Client = Depends(get_supabase)):
    """Exchange OAuth tokens for user session. Called by frontend after Google redirect."""
    try:
        # Set the session with the tokens from Supabase OAuth callback
        response = supabase.auth.set_session(access_token, refresh_token or "")
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate with Google"
            )
        
        user_meta = response.user.user_metadata or {}
        
        return AuthResponse(
            access_token=response.session.access_token if response.session else access_token,
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "username": user_meta.get("full_name") or user_meta.get("name") or user_meta.get("email", "").split("@")[0],
                "avatar_url": user_meta.get("avatar_url") or user_meta.get("picture")
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/verify")
def verify_token(current_user = Depends(get_current_user)):
    """Verify if the current token is valid."""
    user_meta = current_user.user_metadata or {}
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "username": user_meta.get("full_name") or user_meta.get("name") or user_meta.get("username"),
            "avatar_url": user_meta.get("avatar_url") or user_meta.get("picture")
        }
    }

