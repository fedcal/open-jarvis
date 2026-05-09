"""HTTP routes for device pairing (`/api/v1/pairing/*`)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis_server.api.deps import (
    get_db,
    get_identity_service,
    get_jwt_keys,
    require_access_token,
)
from jarvis_server.identity import tokens as tk
from jarvis_server.identity.enums import DevicePlatform
from jarvis_server.identity.orm import Device, Session, User
from jarvis_server.identity.pairing import (
    PairingAlreadyUsed,
    PairingExpired,
    PairingService,
)
from jarvis_server.identity.schemas import TokenPair, UserPublic
from jarvis_server.identity.service import IdentityService, JwtKeys

router = APIRouter(prefix="/api/v1/pairing", tags=["pairing"])


class PairingInitiateResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str  # 6-digit human-friendly
    raw_token: str  # what the QR encodes
    expires_in: int
    qr_payload: str  # otpauth-like URI for QR generation


class PairingRedeemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    raw_token: Annotated[str, Field(min_length=16, max_length=128)]
    device_name: Annotated[str, Field(min_length=1, max_length=128)]
    device_platform: DevicePlatform = DevicePlatform.MOBILE_ANDROID


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post(
    "/initiate",
    response_model=PairingInitiateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def initiate(
    claims: Annotated[tk.AccessTokenClaims, Depends(require_access_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PairingInitiateResponse:
    service = PairingService(session=db)
    row, raw_token = await service.initiate(user_id=UUID(claims.subject))
    expires_in = int((row.expires_at.replace(tzinfo=UTC) - datetime.now(tz=UTC)).total_seconds())
    qr_payload = f"jarvispair://v1?token={raw_token}&code={row.code}"
    return PairingInitiateResponse(
        code=row.code,
        raw_token=raw_token,
        expires_in=max(0, expires_in),
        qr_payload=qr_payload,
    )


@router.post(
    "/redeem",
    response_model=TokenPair,
)
async def redeem(
    payload: PairingRedeemRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    identity: Annotated[IdentityService, Depends(get_identity_service)],
    keys: Annotated[JwtKeys, Depends(get_jwt_keys)],
) -> TokenPair:
    pairing = PairingService(session=db)
    try:
        row = await pairing.redeem(
            raw_token=payload.raw_token,
            device_name=payload.device_name,
            device_platform=payload.device_platform,
        )
    except PairingExpired as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pairing code expired or unknown",
        ) from exc
    except PairingAlreadyUsed as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="pairing code already redeemed",
        ) from exc

    user = await db.get(User, row.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    # Create a brand-new device + issue a fresh token pair scoped to it
    device = Device(
        user_id=user.id,
        name=payload.device_name,
        platform=payload.device_platform.value,
        is_trusted=True,
    )
    db.add(device)
    await db.flush()

    refresh = tk.new_refresh_token()
    access_token, access_exp = tk.issue_access_token(
        user_id=str(user.id),
        role=user.role,
        jti=refresh.jti,
        family_id=refresh.family_id,
        private_key_pem=keys.private_pem,
        device_id=str(device.id),
    )
    db.add(
        Session(
            user_id=user.id,
            device_id=device.id,
            jti=refresh.jti,
            family_id=refresh.family_id,
            refresh_token_hash=refresh.hashed,
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            expires_at=refresh.expires_at,
        ),
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh.raw,
        expires_in=int((access_exp - datetime.now(tz=UTC)).total_seconds()),
        user=UserPublic.model_validate(user, from_attributes=True),
    )


__all__ = ["router"]
