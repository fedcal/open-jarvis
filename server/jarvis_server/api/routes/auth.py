"""HTTP routes for the identity / authentication layer.

Endpoints (mounted under ``/api/v1/auth``):

| Method | Path           | Purpose                                |
|--------|----------------|----------------------------------------|
| POST   | /register      | Create a brand-new user (open or invite) |
| POST   | /login         | Email + password login → tokens or MFA  |
| POST   | /refresh       | Rotate the refresh token                |
| POST   | /logout        | Revoke the current session              |
| GET    | /me            | Return the authenticated user profile   |
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.api.deps import (
    get_db,
    get_identity_service,
    require_access_token,
)
from jarvis_server.identity import tokens as tk
from jarvis_server.identity.orm import User
from jarvis_server.identity.schemas import (
    LoginRequest,
    MfaChallenge,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserPublic,
)
from jarvis_server.identity.service import (
    AccountDisabled,
    EmailAlreadyRegistered,
    IdentityService,
    InvalidCredentials,
    RefreshExpired,
    RefreshReuseDetected,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: RegisterRequest,
    service: Annotated[IdentityService, Depends(get_identity_service)],
) -> UserPublic:
    try:
        return await service.register(payload)
    except EmailAlreadyRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email already registered",
        ) from exc


@router.post(
    "/login",
    response_model=TokenPair | MfaChallenge,
    summary="Login with email + password",
)
async def login(
    payload: LoginRequest,
    request: Request,
    service: Annotated[IdentityService, Depends(get_identity_service)],
) -> TokenPair | MfaChallenge:
    try:
        return await service.login(
            payload,
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
        ) from exc
    except AccountDisabled as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account disabled",
        ) from exc


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Rotate the refresh token",
)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    service: Annotated[IdentityService, Depends(get_identity_service)],
) -> TokenPair:
    try:
        return await service.refresh(
            payload.refresh_token,
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
    except (InvalidCredentials, RefreshExpired) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired refresh token",
        ) from exc
    except RefreshReuseDetected as exc:
        # Defensive: every session in the family is now revoked
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="session family revoked due to suspected token reuse",
        ) from exc


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke the current session",
)
async def logout(
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    service: Annotated[IdentityService, Depends(get_identity_service)],
) -> None:
    await service.revoke_session(claims.jti)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Return the authenticated user profile",
)
async def me(
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    user = await db.scalar(select(User).where(User.id == UUID(claims.subject)))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    return UserPublic.model_validate(user, from_attributes=True)


__all__ = ["router"]
