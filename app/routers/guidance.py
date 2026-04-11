from fastapi import APIRouter, HTTPException
from app.schemas.guidance import GuidanceOut, TraitsOut
from app.models.person_profile import PersonProfile
from app.services.guidance_service import generate_guidance
from app.services.profile_service import extract_traits
from app.utils.exceptions import InvalidObjectIdException
from beanie import PydanticObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/profiles", tags=["Guidance"])


@router.get("/{profile_id}/guidance", response_model=GuidanceOut)
async def get_guidance(profile_id: str):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if not profile.profile_finalized:
        raise HTTPException(
            status_code=400,
            detail="Profile not finalized yet. Submit questionnaire answers first."
        )

    # Extract traits if not already present
    if not profile.personality_traits:
        traits = await extract_traits(profile=profile)
        profile.personality_traits = traits
        await profile.save()

    guidance = await generate_guidance(profile=profile)
    return guidance


@router.get("/{profile_id}/traits", response_model=TraitsOut)
async def get_traits(profile_id: str):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if not profile.profile_finalized:
        raise HTTPException(
            status_code=400,
            detail="Profile not finalized yet. Submit questionnaire answers first."
        )

    if not profile.personality_traits:
        traits = await extract_traits(profile=profile)
        profile.personality_traits = traits
        await profile.save()

    return TraitsOut(
        profile_id=profile_id,
        person_name=profile.name,
        personality_traits=profile.personality_traits
    )