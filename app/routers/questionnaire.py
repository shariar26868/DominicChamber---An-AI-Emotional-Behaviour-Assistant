from fastapi import APIRouter, HTTPException
from app.schemas.questionnaire import QuestionnaireResponse, AnswerSubmit
from app.models.person_profile import PersonProfile, QuestionAnswer
from app.services.questionnaire_service import generate_questions
from app.utils.exceptions import InvalidObjectIdException
from beanie import PydanticObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/profiles", tags=["Questionnaire"])


@router.get("/{profile_id}/questions", response_model=QuestionnaireResponse)
async def get_questions(profile_id: str):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    questions = await generate_questions(
        name=profile.name,
        relationship=profile.relationship,
        description=profile.description
    )

    return QuestionnaireResponse(
        profile_id=profile_id,
        questions=questions
    )


@router.post("/{profile_id}/answers")
async def submit_answers(profile_id: str, payload: AnswerSubmit):
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.questionnaire_answers = [
        QuestionAnswer(
            question=a.question,
            selected_option=a.selected_option
        )
        for a in payload.answers
    ]
    profile.profile_finalized = True
    await profile.save()

    return {"message": "Answers saved successfully", "profile_id": profile_id}