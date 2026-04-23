from app.models.rating import Rating
from app.models.conversation import Conversation
from app.schemas.rating import RatingQuestion
from app.services.openai_client import client
from app.utils.prompt_templates import rating_questions_prompt
from beanie import PydanticObjectId
from fastapi import HTTPException
from typing import List
import json


async def get_all_ratings(profile_id: str) -> List[Rating]:
    return await Rating.find(
        Rating.profile_id == PydanticObjectId(profile_id)
    ).to_list()


async def calculate_average(ratings: List[Rating]) -> float:
    if not ratings:
        return 0.0
    return round(sum(r.score for r in ratings) / len(ratings), 2)


async def generate_rating_questions(conversation_id: str) -> List[RatingQuestion]:
    """Fetch conversation and use AI to generate rating questions based on it."""
    try:
        conversation = await Conversation.get(PydanticObjectId(conversation_id))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.messages:
        raise HTTPException(status_code=400, detail="Conversation has no messages")

    # Build conversation text for the prompt
    conversation_text = "\n".join(
        f"{m.role.upper()}: {m.content}" for m in conversation.messages
    )

    prompt = rating_questions_prompt(conversation_text)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates rating questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    content = response.choices[0].message.content
    if not content:
        raise HTTPException(status_code=500, detail="Empty response from OpenAI API")

    try:
        # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]  # remove opening ```
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]             # remove "json" language tag
            cleaned = cleaned.rsplit("```", 1)[0] # remove closing ```
            cleaned = cleaned.strip()

        data = json.loads(cleaned)
        questions = [
            RatingQuestion(
                question_number=i + 1,
                question=q["question"]
            )
            for i, q in enumerate(data["questions"])
        ]
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")

    return questions
