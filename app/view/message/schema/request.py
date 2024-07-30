from enum import Enum

from pydantic import BaseModel


class Feedback(int, Enum):
    good = 1
    bad = -1


class FeedbackRequest(BaseModel):
    feedback: Feedback
