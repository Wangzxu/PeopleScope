from pydantic import BaseModel, Field


class QuestionTraitCreate(BaseModel):
    question_id: int = Field(..., description="问题id")
    question: str = Field(..., example="你更喜欢独处还是社交？")
    trait_score: int = Field(..., ge=1, le=10, example=5)
