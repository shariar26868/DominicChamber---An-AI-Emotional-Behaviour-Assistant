from app.services.openai_client import client
from app.utils.prompt_templates import conversation_system_prompt
from app.models.person_profile import PersonProfile
from app.models.conversation import Message
from fastapi import HTTPException
from typing import List


async def get_ai_reply(profile: PersonProfile, messages: List[Message]) -> str:
    answers = [
        {
            "question": a.question,
            "selected_option": a.selected_option
        }
        for a in profile.questionnaire_answers
    ]

    system_prompt = conversation_system_prompt(
        name=profile.name,
        relationship=profile.relationship,
        traits=profile.personality_traits,
        answers=answers
    )

    # পুরো conversation history OpenAI কে পাঠাও
    history = [
        {"role": m.role, "content": m.content}
        for m in messages
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ],
            temperature=0.8
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )

    reply = response.choices[0].message.content
    
    if not reply:
        raise HTTPException(
            status_code=500,
            detail="Empty response from OpenAI API"
        )
    
    return reply