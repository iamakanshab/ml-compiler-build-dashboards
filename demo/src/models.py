from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import enum

class StatusEnum(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"
    WARNING = "warning"

@dataclass
class Job:
    name: str
    status: StatusEnum
    duration: str
    error: Optional[str] = None

@dataclass
class Workflow:
    id: str
    name: str
    branch: str
    commit: str
    author: str
    status: StatusEnum
    start_time: datetime
    duration: str
    jobs: List[Job]