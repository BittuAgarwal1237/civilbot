from pydantic import BaseModel, Field,field_validator

class ClassifierOutput(BaseModel):
    issue_type: str
    category: str
    urgency: int = Field(ge=1, le=5)
    severity_reason: str

    @field_validator("urgency", mode="before")
    @classmethod
    def convert_urgency(cls, value):
        return int(value)


class EvidenceOutput(BaseModel):
    location: str
    issue: str
    duration: str
    landmarks: list[str] = Field(default_factory=list)

class RouterOutput(BaseModel):
    department: str
    routing_reason: str

class ResponseOutput(BaseModel):
    citizen_response: str

class TaskOutput(BaseModel):
    task_title: str
    priority: str
    estimated_resolution: str

class LetterOutput(BaseModel):
    subject: str
    letter: str    

    