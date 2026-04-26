from fastapi import APIRouter, HTTPException
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskListResponse, RecommendedActionsResponse
from app.models.task import Task
from app.models.person_profile import PersonProfile
from app.services.task_service import generate_recommended_actions
from app.utils.exceptions import InvalidObjectIdException
from beanie import PydanticObjectId
from bson.errors import InvalidId
from datetime import datetime

router = APIRouter(prefix="/profiles", tags=["Tasks"])


@router.get("/{profile_id}/tasks/recommended", response_model=RecommendedActionsResponse)
async def get_recommended_actions(profile_id: str):
    """Get AI-generated recommended actions based on profile personality."""
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    actions = await generate_recommended_actions(profile)

    return RecommendedActionsResponse(
        profile_id=profile_id,
        recommended_actions=actions
    )


@router.get("/{profile_id}/tasks", response_model=TaskListResponse)
async def get_tasks(profile_id: str, user_id: str):
    """Get all tasks for a profile."""
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        tasks = await Task.find(
            Task.profile_id == PydanticObjectId(profile_id),
            Task.user_id == PydanticObjectId(user_id)
        ).sort("+created_at").to_list()
    except InvalidId:
        raise InvalidObjectIdException(user_id)

    completed = sum(1 for t in tasks if t.is_completed)

    return TaskListResponse(
        profile_id=profile_id,
        total=len(tasks),
        completed=completed,
        tasks=[_task_out(t) for t in tasks]
    )


@router.post("/{profile_id}/tasks", response_model=TaskOut)
async def create_task(profile_id: str, user_id: str, payload: TaskCreate):
    """Add a new task (manually or from recommended actions)."""
    try:
        profile = await PersonProfile.get(PydanticObjectId(profile_id))
    except InvalidId:
        raise InvalidObjectIdException(profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        task = Task(
            profile_id=PydanticObjectId(profile_id),
            user_id=PydanticObjectId(user_id),
            title=payload.title,
            source=payload.source
        )
    except InvalidId:
        raise InvalidObjectIdException(user_id)

    await task.insert()
    return _task_out(task)


@router.patch("/{profile_id}/tasks/{task_id}", response_model=TaskOut)
async def update_task(profile_id: str, task_id: str, payload: TaskUpdate):
    """Update a task (edit title or mark complete/incomplete)."""
    try:
        task = await Task.get(PydanticObjectId(task_id))
    except InvalidId:
        raise InvalidObjectIdException(task_id)

    if not task or str(task.profile_id) != profile_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.title is not None:
        task.title = payload.title
    if payload.is_completed is not None:
        task.is_completed = payload.is_completed

    task.updated_at = datetime.utcnow()
    await task.save()
    return _task_out(task)


@router.delete("/{profile_id}/tasks/{task_id}")
async def delete_task(profile_id: str, task_id: str):
    """Delete a task."""
    try:
        task = await Task.get(PydanticObjectId(task_id))
    except InvalidId:
        raise InvalidObjectIdException(task_id)

    if not task or str(task.profile_id) != profile_id:
        raise HTTPException(status_code=404, detail="Task not found")

    await task.delete()
    return {"message": "Task deleted successfully"}


def _task_out(task: Task) -> TaskOut:
    return TaskOut(
        id=str(task.id),
        profile_id=str(task.profile_id),
        user_id=str(task.user_id),
        title=task.title,
        is_completed=task.is_completed,
        source=task.source,
        created_at=task.created_at,
        updated_at=task.updated_at
    )
