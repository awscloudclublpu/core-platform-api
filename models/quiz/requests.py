from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional
from uuid import UUID


# ----------------------------
# Question + Options
# ----------------------------

class OptionSchema(BaseModel):
    id: str = Field(description="Unique option identifier (A, B, C, D etc.)")
    text: str = Field(description="Option text")


class QuestionSchema(BaseModel):
    question: str = Field(
        description="The question text",
        min_length=1
    )

    options: List[OptionSchema] = Field(
        description="List of answer options (minimum 2)"
    )

    correct_option_id: str = Field(
        description="ID of the correct option"
    )

    explanation: Optional[str] = Field(
        default=None,
        description="Optional explanation shown after submission"
    )

    @validator("options")
    def validate_options(cls, value):
        if len(value) < 2:
            raise ValueError("A question must have at least 2 options")
        return value


# ----------------------------
# Quiz Settings
# ----------------------------

class QuizSettings(BaseModel):
    question_timer_seconds: int = Field(
        description="Uniform timer per question in seconds",
        gt=0
    )

    shuffle_questions: bool = Field(
        default=False,
        description="Shuffle questions for each attempt"
    )

    shuffle_options: bool = Field(
        default=False,
        description="Shuffle options order"
    )

    allow_multiple_attempts: bool = Field(
        default=False,
        description="Whether users can retry the quiz"
    )

    passing_score_percentage: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Passing percentage (optional)"
    )


# ----------------------------
# Quiz Window (Availability)
# ----------------------------

class QuizSchedule(BaseModel):
    start_time: datetime = Field(
        description="Quiz becomes available at this time (UTC recommended)"
    )

    end_time: datetime = Field(
        description="Quiz closes at this time"
    )

    @validator("end_time")
    def validate_time_window(cls, end_time, values):
        start_time = values.get("start_time")
        if start_time and end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        return end_time


# ----------------------------
# Main Quiz Create Schema
# ----------------------------

class QuizCreateRequest(BaseModel):
    title: str = Field(
        max_length=255,
        description="Quiz title"
    )

    description: Optional[str] = Field(
        default=None,
        description="Quiz description"
    )

    schedule: QuizSchedule

    settings: QuizSettings

    questions: List[QuestionSchema] = Field(
        description="List of quiz questions",
        min_items=1
    )