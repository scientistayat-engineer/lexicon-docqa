from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    mode: str = "role_based"


class BenchmarkRequest(BaseModel):
    questions: list[str]
