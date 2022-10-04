from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

class JsonDatatype(BaseModel):
    data: Any

class HookDatatype(BaseModel):
    id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    method: str
    url: str
    body: Optional[str]
    cron: str
    headers: Optional[Dict]
    last_hit: Optional[str]
    user_id: Optional[str]

