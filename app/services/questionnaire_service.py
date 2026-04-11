import json
import re
from app.services.openai_client import client
from app.utils.prompt_templates import questionnaire_prompt
from app.schemas.questionnaire import QuestionItem, QuestionOption
from fastapi import HTTPException
from typing import List


def clean_json_response(response: str) -> str:
    """Remove markdown code blocks from JSON response"""
    # Remove ```json and ``` markers
    response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
    return response.strip()


async def generate_questions(name: str, relationship: str, description: str) -> List[QuestionItem]:
    prompt = questionnaire_prompt(name, relationship, description)

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

    questions = []
    for q in data["questions"]:
        questions.append(
            QuestionItem(
                question_id=q["question_id"],
                question=q["question"],
                options=[
                    QuestionOption(label=o["label"], value=o["value"])
                    for o in q["options"]
                ]
            )
        )

    return questions