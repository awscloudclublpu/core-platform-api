from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class QuizScheduleResponse(BaseModel):
    start_time: datetime = Field(
        description="Quiz availability start time"
    )
    end_time: datetime = Field(
        description="Quiz availability end time"
    )


class QuizSettingsResponse(BaseModel):
    question_timer_seconds: int = Field(
        description="Uniform timer applied to each question"
    )
    shuffle_questions: bool
    shuffle_options: bool
    allow_multiple_attempts: bool
    passing_score_percentage: Optional[int] = Field(
        default=None,
        description="Passing percentage if configured"
    )


class QuizCreationResponse(BaseModel):
    quiz_id: str = Field(
        description="Unique identifier of the created quiz"
    )

    title: str = Field(
        description="Quiz title"
    )

    description: Optional[str] = Field(
        default=None,
        description="Quiz description"
    )

    created_by: EmailStr = Field(
        description="Email of the quiz creator"
    )

    created_at: datetime = Field(
        description="Timestamp when quiz was created"
    )

    schedule: QuizScheduleResponse = Field(
        description="Quiz availability window"
    )

    settings: QuizSettingsResponse = Field(
        description="Quiz configuration settings"
    )

    total_questions: int = Field(
        description="Total number of questions in the quiz"
    )