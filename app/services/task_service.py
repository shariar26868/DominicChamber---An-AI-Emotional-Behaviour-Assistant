from app.models.person_profile import PersonProfile
from app.schemas.task import RecommendedAction
from app.services.openai_client import client
from app.utils.prompt_templates import recommended_actions_prompt
from fastapi import HTTPException
from typing import List
import json


async def generate_recommended_actions(profile: PersonProfile) -> List[RecommendedAction]:
    """Use AI to generate recommended actions based on profile personality and traits."""

    answers = [
        {"question": a.question, "selected_option": a.selected_option}
        for a in profile.questionnaire_answers
    ]

    prompt = recommended_actions_prompt(
        name=profile.name,
        relationship=profile.relationship,
        traits=profile.personality_traits,
        answers=answers
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a relationship and communication coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    content = response.choices[0].message.content
    if not content:
        raise HTTPException(status_code=500, detail="Empty response from OpenAI API")

    # Strip markdown code fences if present
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.rsplit("```", 1)[0].strip()

    try:
        data = json.loads(cleaned)
        return [RecommendedAction(title=item["title"]) for item in data["actions"]]
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
