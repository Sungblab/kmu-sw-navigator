from typing import Literal

from pydantic import BaseModel, Field

Department = Literal["software", "ai", "unknown", "other"]
CurriculumYear = Literal["2023", "2024", "2025", "unknown"]


class ProfileUpsertRequest(BaseModel):
    department: Department = "unknown"
    grade: int = Field(default=1, ge=1, le=4)
    curriculum_year: CurriculumYear = "unknown"


class ProfileResponse(ProfileUpsertRequest):
    id: str
    exists: bool = True
