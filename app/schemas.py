import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    wants_product_updates: Optional[bool] = False


class UserCreate(schemas.BaseUserCreate):
    wants_product_updates: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    wants_product_updates: Optional[bool] = False
