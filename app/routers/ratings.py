from fastapi import APIRouter, HTTPException
from app.schemas.rating import RatingCreate, RatingOut, RatingBulkResponse, AverageRating, RatingQuestionsRequest, RatingQuestionsResponse
from app.models.rating import Rating
from app.models.person_profile import PersonProfile
from app.services.rating_service import generate_rating_questions
from app.utils.exceptions import InvalidObjectIdException
from beanie import PydanticObjectId
from bson.errors import InvalidId
from typing import List

router = APIRouter(prefix="/profiles", tags=["Ratings"])


@router.post("/{profile_id}/ratings/questions", response_model=RatingQuestionsResponse)
async def get_rating_questions(profile_id: str, payload: RatingQuestionsRequest):
    """Generate AI rating questions based on a conversation."""
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    questions = await generate_rating_questions(payload.conversation_id)

    return RatingQuestionsResponse(
        profile_id=profile_id,
        conversation_id=payload.conversation_id,
        questions=questions
    )


@router.post("/{profile_id}/ratings", response_model=RatingBulkResponse)
async def submit_ratings(profile_id: str, user_id: str, payload: List[RatingCreate]):
    """Submit ratings for multiple questions at once."""
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        profile_oid = PydanticObjectId(profile_id)
        user_oid = PydanticObjectId(user_id)
    except InvalidId:
        raise InvalidObjectIdException(user_id)

    saved = []
    for item in payload:
        rating = Rating(
            profile_id=profile_oid,
            user_id=user_oid,
            question_number=item.question_number,
            score=item.score,
            note=item.note
        )
        await rating.insert()
        saved.append(RatingOut(
            id=str(rating.id),
            profile_id=str(rating.profile_id),
            question_number=rating.question_number,
            score=rating.score,
            note=rating.note,
            created_at=rating.created_at
        ))

    return RatingBulkResponse(profile_id=profile_id, ratings=saved)


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
