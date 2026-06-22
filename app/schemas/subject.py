from pydantic import BaseModel, Field

class SubjectSchema(BaseModel):
    name: str = Field(min_length=2, max_length=50, examples=["Mathematics"])
    description: str | None = Field(default=None, examples=["Algebra and Geometry"])

class SubjectResponse(BaseModel):
    id: int
    name: str
    description: str | None

class AllSubjectResponse(BaseModel):
    subjects: list[SubjectResponse]
