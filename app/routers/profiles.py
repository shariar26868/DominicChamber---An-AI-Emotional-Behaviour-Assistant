from fastapi import APIRouter, HTTPException
from app.schemas.person_profile import ProfileCreate, ProfileOut, ProfileUpdate
from app.models.person_profile import PersonProfile
from app.models.user import User
from app.utils.exceptions import InvalidObjectIdException, UserNotFoundException
from beanie import PydanticObjectId
from bson.errors import InvalidId
from typing import List

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post("/", response_model=ProfileOut)
async def create_profile(payload: ProfileCreate):
    user = await User.get(PydanticObjectId(payload.user_id))
    if not user:
        raise UserNotFoundException()

    profile = PersonProfile(
        user_id=PydanticObjectId(payload.user_id),
        name=payload.name,
        relationship=payload.relationship,
        description=payload.description
    )
    await profile.insert()

    return _profile_out(profile)


@router.get("/user/{user_id}", response_model=List[ProfileOut])
async def get_user_profiles(user_id: str):
    try:
        profiles = await PersonProfile.find(
            PersonProfile.user_id == PydanticObjectId(user_id)
        ).to_list()
    except InvalidId:
        raise InvalidObjectIdException(user_id)

    return [_profile_out(p) for p in profiles]


@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: str):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return _profile_out(profile)


@router.patch("/{profile_id}", response_model=ProfileOut)
async def update_profile(profile_id: str, payload: ProfileUpdate):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = payload.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await profile.save()
    return _profile_out(profile)


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    await profile.delete()
    return {"message": "Profile deleted successfully"}


def _profile_out(profile: PersonProfile) -> ProfileOut:
    return ProfileOut(
        id=str(profile.id),
        user_id=str(profile.user_id),
        name=profile.name,
        relationship=profile.relationship,
        description=profile.description,
        personality_traits=profile.personality_traits,
        profile_finalized=profile.profile_finalized,
        created_at=profile.created_at
    )