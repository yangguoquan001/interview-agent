from typing import Dict, Any, List

from langchain_core.messages import HumanMessage

from config import prompts
from src.schemas.states import ResumeAgentState
from schemas.data_models import QuestionRecord, QuestionsOutput
from src.utils.llm_fatory import get_chat_model


def generate_questions(
    resume_info: dict, job_description: dict
) -> List[QuestionRecord]:
    """根据简历和JD生成面试问题"""
    resume_str = f"姓名: {resume_info.get('candidate_name', '')}\n"
    resume_str += f"工作年限: {resume_info.get('years_experience', '')}\n"
    resume_str += f"技能: {', '.join(resume_info.get('skills', []))}\n"
    resume_str += f"项目经验: {'; '.join(resume_info.get('project_experience', []))}"

    jd_str = f"职位: {job_description.get('job_title', '')}\n"
    jd_str += f"必需技能: {', '.join(job_description.get('required_skills', []))}\n"
    jd_str += f"加分技能: {', '.join(job_description.get('preferred_skills', []))}\n"
    jd_str += f"岗位职责: {'; '.join(job_description.get('responsibilities', []))}"

    llm = get_chat_model(temperature=0.7, structured_output_schema=QuestionsOutput)

    result = llm.invoke(
        [
            HumanMessage(content=prompts.RESUME_QUESTIONER_SYSTEM_PROMPT),
            HumanMessage(
                content=prompts.RESUME_QUESTIONER_PROMPT_TEMPLATE.format(
                    resume_info=resume_str,
                    job_description=jd_str,
                    ),
                )
        ]
    )
    
    return result.question_list


def resume_questioner_node(state: ResumeAgentState) -> Dict[str, Any]:
    """生成面试问题节点"""
    resume_info = state.get("resume_info")
    job_description = state.get("job_description")

    if not resume_info or not job_description:
        return {"error": "缺少简历或JD信息"}

    # question_list = generate_questions(
    #     resume_info.model_dump() if hasattr(resume_info, "model_dump") else resume_info,
    #     job_description.model_dump()
    #     if hasattr(job_description, "model_dump")
    #     else job_description,
    # )
    # 使用以上数据mock生成的面试问题 TODO: 实际使用时，需要从数据库中获取简历和JD
    question_list = ['在“智能聊天机器人系统”项目中，你提到构建了基于大模型的知识库问答。请具体说明你在向量检索阶段采用了何种分块（Chunking）策略来处理长文档？在面对检索结果与用户问题相关性不高的情况时，你是如何通过重排序（Re-ranking）或提示词工程来优化最终回答质量的？', '针对 JD 中强调的“工具调用与 API 对接”，在“咨询师培训系统”中你使用了 functioncall 能力。当大模型生成的参数与实际 API 接口定义不一致导致调用失败时，你设计了怎样的重试机制或错误恢复流程（例如：是否引入中间校验层或让模型自我修正），以保证对话链路的稳定性？']
    question_records = []
    for question in question_list:
        question_records.append(QuestionRecord(questions=[question]))
    return {
        "question_list": question_list,
        "question_records": question_records,
        "current_question_index": 0,
    }
