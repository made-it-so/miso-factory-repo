from pydantic import BaseModel
from typing import Optional
import uuid

class GenesisRequest(BaseModel):
    prompt: str
    config: Optional[dict] = None

class GenesisJob(BaseModel):
    job_id: str
    status: str
    message: str
