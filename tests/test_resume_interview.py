import pytest
from schemas.data_models import ResumeInfo, JobDescription, QuestionRecord


def test_resume_info_model():
    resume = ResumeInfo(
        candidate_name="张三",
        years_experience=3,
        current_company="字节跳动",
        skills=["Python", "Go", "MySQL"],
        project_experience=["电商平台", "即时通讯"],
        education="本科",
    )
    assert resume.candidate_name == "张三"
    assert resume.years_experience == 3


def test_question_record_model():
    q = QuestionRecord(
        question="请介绍一下你的项目经验",
        answer="我参与了一个电商平台开发...",
        follow_ups=[],
        summary="项目经验介绍详细",
        score=8,
        is_terminated=False,
        follow_up_count=0,
    )
    assert q.score == 8
