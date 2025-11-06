"""
API routes for clan management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from api.auth import verify_api_key
from modules.clans.service import ClanService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/clans", tags=["clans"])


class ClanMemberResponse(BaseModel):
    """Response model for clan member"""

    user_id: int
    clan_id: str
    role: int
    joined_at: datetime


class ClanChannelResponse(BaseModel):
    """Response model for clan channel"""

    channel_id: int
    name: str
    type: str
    clan_id: str
    created_at: datetime


class ClanResponse(BaseModel):
    """Response model for clan"""

    id: str
    name: str
    role_id: int
    created_at: datetime
    member_count: int
    max_members: int
    max_text_channels: int
    max_voice_channels: int
    members: Optional[List[ClanMemberResponse]] = None
    channels: Optional[List[ClanChannelResponse]] = None


@router.get("/", response_model=List[ClanResponse])
async def list_clans(_: str = Depends(verify_api_key)):
    """
    Get list of all clans.

    Returns:
        List of all clans with their members and channels
    """
    service = ClanService()
    clans, error = await service.get_all_clans()

    if error:
        raise HTTPException(status_code=500, detail=error)

    if not clans:
        return []

    return [
        ClanResponse(
            id=clan.id,
            name=clan.name,
            role_id=clan.role_id,
            created_at=clan.created_at,
            member_count=clan.member_count,
            max_members=clan.max_members,
            max_text_channels=clan.max_text_channels,
            max_voice_channels=clan.max_voice_channels,
            members=(
                [
                    ClanMemberResponse(
                        user_id=m.user_id, clan_id=m.clan_id, role=m.role, joined_at=m.joined_at
                    )
                    for m in clan.members
                ]
                if clan.members
                else []
            ),
            channels=(
                [
                    ClanChannelResponse(
                        channel_id=c.channel_id,
                        name=c.name,
                        type=c.type,
                        clan_id=c.clan_id,
                        created_at=c.created_at,
                    )
                    for c in clan.channels
                ]
                if clan.channels
                else []
            ),
        )
        for clan in clans
    ]


@router.get("/{clan_id}", response_model=ClanResponse)
async def get_clan(clan_id: str, _: str = Depends(verify_api_key)):
    """
    Get details of a specific clan.

    Args:
        clan_id: The ID of the clan

    Returns:
        Clan details with members and channels
    """
    service = ClanService()
    clan, error = await service.get_clan_by_id(clan_id)

    if error:
        raise HTTPException(status_code=404, detail=error)

    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")

    return ClanResponse(
        id=clan.id,
        name=clan.name,
        role_id=clan.role_id,
        created_at=clan.created_at,
        member_count=clan.member_count,
        max_members=clan.max_members,
        max_text_channels=clan.max_text_channels,
        max_voice_channels=clan.max_voice_channels,
        members=(
            [
                ClanMemberResponse(
                    user_id=m.user_id, clan_id=m.clan_id, role=m.role, joined_at=m.joined_at
                )
                for m in clan.members
            ]
            if clan.members
            else []
        ),
        channels=(
            [
                ClanChannelResponse(
                    channel_id=c.channel_id,
                    name=c.name,
                    type=c.type,
                    clan_id=c.clan_id,
                    created_at=c.created_at,
                )
                for c in clan.channels
            ]
            if clan.channels
            else []
        ),
    )


@router.get("/{clan_id}/members", response_model=List[ClanMemberResponse])
async def get_clan_members(clan_id: str, _: str = Depends(verify_api_key)):
    """
    Get members of a specific clan.

    Args:
        clan_id: The ID of the clan

    Returns:
        List of clan members
    """
    service = ClanService()
    clan, error = await service.get_clan_by_id(clan_id)

    if error:
        raise HTTPException(status_code=404, detail=error)

    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")

    return [
        ClanMemberResponse(user_id=m.user_id, clan_id=m.clan_id, role=m.role, joined_at=m.joined_at)
        for m in (clan.members or [])
    ]
