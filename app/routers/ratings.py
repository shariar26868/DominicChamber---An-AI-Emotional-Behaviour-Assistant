from fastapi import APIRouter, HTTPException
from app.schemas.rating import RatingCreate, RatingOut, AverageRating
from app.models.rating import Rating
from app.models.person_profile import PersonProfile
from app.utils.exceptions import InvalidObjectIdException
from beanie import PydanticObjectId
from bson.errors import InvalidId
from typing import List

router = APIRouter(prefix="/profiles", tags=["Ratings"])


@router.post("/{profile_id}/ratings", response_model=RatingOut)
async def submit_rating(profile_id: str, user_id: str, payload: RatingCreate):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        rating = Rating(
            profile_id=PydanticObjectId(profile_id),
            user_id=PydanticObjectId(user_id),
            score=payload.score,
            note=payload.note
        )
    except InvalidId:
        raise InvalidObjectIdException(user_id)
    
    await rating.insert()

    return RatingOut(
        id=str(rating.id),
        profile_id=str(rating.profile_id),
        score=rating.score,
        note=rating.note,
        created_at=rating.created_at
    )


@router.get("/{profile_id}/ratings/average", response_model=AverageRating)
async def get_average_rating(profile_id: str):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        ratings = await Rating.find(
            Rating.profile_id == PydanticObjectId(profile_id)
        ).to_list()
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    if not ratings:
        raise HTTPException(status_code=404, detail="No ratings found for this profile")

    avg = sum(r.score for r in ratings) / len(ratings)

    return AverageRating(
        profile_id=profile_id,
        person_name=profile.name,
        average_score=round(avg, 2),
        total_ratings=len(ratings)
    )
