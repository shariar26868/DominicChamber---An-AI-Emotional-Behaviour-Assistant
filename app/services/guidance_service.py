import json
import re
from app.services.openai_client import client
from app.utils.prompt_templates import guidance_prompt
from app.schemas.guidance import GuidanceOut
from app.models.person_profile import PersonProfile
from fastapi import HTTPException


def clean_json_response(response: str) -> str:
    """Remove markdown code blocks from JSON response"""
    response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
    return response.strip()


async def generate_guidance(profile: PersonProfile) -> GuidanceOut:
    answers = [
        {
            "question": a.question,
            "selected_option": a.selected_option
        }
        for a in profile.questionnaire_answers
    ]

    prompt = guidance_prompt(
        name=profile.name,
        relationship=profile.relationship,
        description=profile.description,
        traits=profile.personality_traits,
        answers=answers
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )

    raw = response.choices[0].message.content
    
    if not raw:
        raise HTTPException(
            status_code=500,
            detail="Empty response from OpenAI API"
        )
    
    # Clean markdown code blocks
    raw = clean_json_response(raw)
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON response from OpenAI: {str(e)}. Response: {raw[:100]}"
        )

    return GuidanceOut(
        profile_id=str(profile.id),
        person_name=profile.name,
        personality_traits=profile.personality_traits,
        summary=data["summary"],
        key_points=data["key_points"],
        expected_outcome=data["expected_outcome"]
    )