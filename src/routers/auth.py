# src/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from starlette.concurrency import run_in_threadpool

from ..auth.auth import auth_handler, JWT_EXP_HOURS, REFRESH_TOKEN_EXP_DAYS
from ..resources.database import get_app_db_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api", tags=["Authentication"])

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = Form(False),
    db: AsyncSession = Depends(get_app_db_session)
):
    """
    Logs in a user, returns a JWT access token, and optionally sets an HttpOnly refresh token cookie.
    """
    try:
        user = await run_in_threadpool(auth_handler.authenticate_user, form_data.username, form_data.password)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

    access_token_expires = timedelta(minutes=15) if remember_me else timedelta(hours=JWT_EXP_HOURS)
    access_token = auth_handler.create_access_token(
       data=user,
       expires_delta=access_token_expires
   )

    if remember_me:
        refresh_token = await auth_handler.create_refresh_token(user_id=user["username"], groups=user["groups"], db=db)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            secure=True, # Should be True in production with HTTPS
            max_age=REFRESH_TOKEN_EXP_DAYS * 24 * 60 * 60 # Convert days to seconds
        )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token/refresh")
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_app_db_session)):
    """
    Refreshes the access token using a valid refresh token from an HttpOnly cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")

    token_obj = await auth_handler.verify_refresh_token(refresh_token, db)
    # Re-fetch full user data to ensure the new token has all AD attributes
    try:
       user_full_info = await run_in_threadpool(auth_handler.authenticate_user, token_obj.user_id, None) # Pass None for password as we are re-authenticating
    except HTTPException as e:
        # Handle cases where the user might not exist in AD anymore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Failed to re-authenticate user: {e.detail}")

    # Invalidate the old refresh token (optional: implement rotation for better security)
    await auth_handler.invalidate_refresh_token(refresh_token, db)

    # Create a new access token (short-lived)
    new_access_token = auth_handler.create_access_token(
        data=user_full_info,
        expires_delta=timedelta(minutes=15)
    )

    # Create a new refresh token and set it as a new HttpOnly cookie

    new_refresh_token = await auth_handler.create_refresh_token(
        user_id=user_full_info["username"], 
        groups=user_full_info.get("groups", []), 
        db=db
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=True, # Should be True in production with HTTPS
        max_age=REFRESH_TOKEN_EXP_DAYS * 24 * 60 * 60
    )

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncSession = Depends(get_app_db_session)):
    """
    Logs out the user by invalidating the refresh token and clearing the HttpOnly cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_handler.invalidate_refresh_token(refresh_token, db)
    
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax", secure=True)
    return {"message": "Logged out successfully"}

from sqlalchemy import select
from ..models.usuario_sistema import UsuarioSistema

@router.get("/users/me")
async def read_users_me(
    current_user: dict = Depends(auth_handler.decode_token),
    db: AsyncSession = Depends(get_app_db_session),
):
    """
    Returns the current user's information enriched with local RBAC profile and assigned project.
    """
    username = current_user.get("username", "")
    stmt = select(UsuarioSistema).where(UsuarioSistema.username == username, UsuarioSistema.ativo == True)
    res = await db.execute(stmt)
    user_db = res.scalars().first()

    if user_db:
        current_user["perfil"] = user_db.perfil
        current_user["projeto_atribuido"] = user_db.projeto_atribuido
    else:
        if "GLO-SEC-HCPE-SETISD" in current_user.get("groups", []) or username == "admin":
            current_user["perfil"] = "ADMINISTRADOR"
            current_user["projeto_atribuido"] = None
        else:
            current_user["perfil"] = "CONSULTA"
            current_user["projeto_atribuido"] = None

    return current_user