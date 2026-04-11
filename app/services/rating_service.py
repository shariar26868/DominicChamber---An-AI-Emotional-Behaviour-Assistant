from app.models.rating import Rating
from beanie import PydanticObjectId
from typing import List


async def get_all_ratings(profile_id: str) -> List[Rating]:
    return await Rating.find(
        Rating.profile_id == PydanticObjectId(profile_id)
    ).to_list()


async def calculate_average(ratings: List[Rating]) -> float:
    if not ratings:
        return 0.0
    return round(sum(r.score for r in ratings) / len(ratings), 2)