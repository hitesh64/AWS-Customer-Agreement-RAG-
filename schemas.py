from pydantic import BaseModel, Field
from typing import List

class AskRequest(BaseModel):
    question: str = Field(..., description="The user's query.")

class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    response_time: float
    confidence: float

class AnalyticsResponse(BaseModel):
    total_queries: int
    most_frequent_questions: List[dict]
    no_answer_queries: int
    average_latency: float
    found_vs_not_found: List[dict]