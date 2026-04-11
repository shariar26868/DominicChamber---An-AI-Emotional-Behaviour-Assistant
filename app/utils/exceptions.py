from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class ProfileNotFinalizedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Profile not finalized yet. Submit questionnaire answers first."
        )


class ProfileNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Profile not found")


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Email already registered")


class ConversationNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Conversation not found")


class RatingNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="No ratings found for this profile")


class InvalidObjectIdException(HTTPException):
    def __init__(self, id: str):
        super().__init__(status_code=400, detail=f"Invalid ID format: {id}")


# Global exception handler — main.py তে register করতে হবে
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )