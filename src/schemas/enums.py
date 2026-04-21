from enum import Enum


class DifficultyLevel(Enum):
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"


class InterviewMode(Enum):
    KNOWLEDGE = "knowledge"
    RESUME = "resume"
    