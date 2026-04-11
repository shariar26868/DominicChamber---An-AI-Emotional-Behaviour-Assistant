from app.database import init_db
from fastapi import HTTPException
from beanie import PydanticObjectId


def validate_object_id(id: str) -> PydanticObjectId:
    try:
        return PydanticObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {id}")