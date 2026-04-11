import json
import re
from app.services.openai_client import client
from app.schemas.message_rewrite import MessageRewriteOut, Improvement
from fastapi import HTTPException


def clean_json_response(response: str) -> str:
    """Remove markdown code blocks from JSON response"""
    response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
    return response.strip()


async def rewrite_message(message: str, context: str = "") -> MessageRewriteOut:
    prompt = f"""
You are a communication expert helping improve messages.

Original message: "{message}"
{f'Context: {context}' if context else ''}

Rewrite the message to be more clear, empathetic, and effective. Then provide exactly 2 key improvements and 2 suggestions.

Respond ONLY in this JSON format, no extra text:
{{
  "rewritten_message": "The improved version of the message",
  "key_improvements": [
    {{
      "title": "Improvement 1 title",
      "description": "Why this improvement was made"
    }},
    {{
      "title": "Improvement 2 title",
      "description": "Why this improvement was made"
    }}
  ],
  "suggestions": [
    {{
      "title": "Suggestion 1 title",
      "description": "How to implement this suggestion"
    }},
    {{
      "title": "Suggestion 2 title",
      "description": "How to implement this suggestion"
    }}
  ]
}}
"""

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

    return MessageRewriteOut(
        original_message=message,
        rewritten_message=data["rewritten_message"],
        key_improvements=[
            Improvement(title=imp["title"], description=imp["description"])
            for imp in data["key_improvements"]
        ],
        suggestions=[
            Improvement(title=sug["title"], description=sug["description"])
            for sug in data["suggestions"]
        ]
    )
