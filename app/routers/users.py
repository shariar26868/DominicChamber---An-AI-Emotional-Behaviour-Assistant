from fastapi import APIRouter, HTTPException
from app.schemas.user import UserCreate, UserOut
from app.models.user import User
from app.utils.exceptions import InvalidObjectIdException, UserNotFoundException
from beanie import PydanticObjectId
from bson.errors import InvalidId

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut)
async def create_user(payload: UserCreate):
    existing = await User.find_one(User.email == payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email
    )
    await user.insert()

    return UserOut(
        id=str(user.id),
        name=user.name,
        email=user.email,
        created_at=user.created_at
    )


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    try:
        user = await User.get(PydanticObjectId(user_id))
    except InvalidId:
        raise InvalidObjectIdException(user_id)
    
    if not user:
        raise UserNotFoundException()

    return UserOut(
        id=str(user.id),
        name=user.name,
        email=user.email,
        created_at=user.created_at
    )