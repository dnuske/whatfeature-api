from fastapi import APIRouter, Depends
from app.db import api
from app.utils import HookDatatype
from app.users import fastapi_users, current_active_user
from app.models import User

router = APIRouter(prefix="")

current_user = fastapi_users.current_user()

@router.get("/", tags=["hooks"])
async def get_hooks(user: User = Depends(current_active_user)):
    return await api.get_all_hooks(user.id)


@router.post("/", tags=["hooks"])
async def create_hook(hook: HookDatatype, user: User = Depends(current_active_user)):
    return await api.create_hook(hook, user.id)


@router.get("/{id}", tags=["hooks"])
async def get_hook(id: str, user: User = Depends(current_active_user)):
    if api.hook_belongs_to_user(id, user.id):
        return await api.get_hook(id)


@router.put("/{id}", tags=["hooks"])
async def update_hook(id: str, hook: HookDatatype, user: User = Depends(current_active_user)):
    hook.id = id
    # TODO: validate only url, cron,
    if api.hook_belongs_to_user(id, user.id):
        return await api.update_hook(hook)


@router.delete("/{id}", tags=["hooks"])
async def delete_hook(id: str, user: User = Depends(current_active_user)):
    if api.hook_belongs_to_user(id, user.id):
        return await api.delete_hook(id)


@router.get("/{id}/hits", tags=["hooks"])
async def get_hook_hits(id: str, user: User = Depends(current_active_user)):
    if api.hook_belongs_to_user(id, user.id):
        return await api.get_all_hook_hits(id)

