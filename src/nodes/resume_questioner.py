from typing import Dict, Any, List

from langchain_core.messages import HumanMessage

from config import prompts
from src.schemas.states import ResumeAgentState
from src.schemas.resume_models import QuestionRecord, QuestionsOutput
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
                    resume_info=resume_str, job_description=jd_str
                )
            ),
        ]
    )
    
    return result.questions


def resume_questioner_node(state: ResumeAgentState) -> Dict[str, Any]:
    """生成面试问题节点"""
    resume_info = state.get("resume_info")
    job_description = state.get("job_description")

    if not resume_info or not job_description:
        return {"error": "缺少简历或JD信息"}

    # questions = generate_questions(
    #     resume_info.model_dump() if hasattr(resume_info, "model_dump") else resume_info,
    #     job_description.model_dump()
    #     if hasattr(job_description, "model_dump")
    #     else job_description,
    # )
    # 使用以上数据mock生成的面试问题 TODO: 实际使用时，需要从数据库中获取简历和JD
    questions = [QuestionRecord(topic='RAG 架构设计与知识库落地', question='在‘智能聊天机器人系统’项目中，你提到构建了基于大模型 + 知识库的对话系统。请详细描述一下你的 RAG（检索增强生成）流程设计：\n1. 你是如何进行文档切片和向量索引的？有没有尝试过混合检索（如关键词 + 向量）或重排序（Re-ranking）策略来提升召回精度？\n2. 在多轮对话场景下，如何管理上下文窗口以平衡成本与效果？如果检索到的信息与大模型幻觉冲突，你设计了什么机制来抑制幻觉？', answer='', follow_ups=[], summary='', score=0, feedback='', is_terminated=False, follow_up_count=0), QuestionRecord(topic='Agent 工具调用与任务编排能力', question='JD 中强调 Agent 的工具调用与自主执行能力。在‘咨询师培训系统’项目中，你结合了 functioncall 模拟用户角色。请分享一个复杂的任务编排案例：\n1. Agent 是如何决定调用哪个工具的？如果工具返回了错误数据或超时，Agent 是否有重试或降级逻辑？\n2. 在实现多步骤任务自动化时，你是如何设计 Prompt 或状态机来确保 Agent 按照预期流程执行，而不是陷入死循环或跳过关键步骤？', answer='', follow_ups=[], summary='', score=0, feedback='', is_terminated=False, follow_up_count=0), QuestionRecord(topic='后端架构稳定性与异步处理', question='项目经验中提到引入消息队列（Kafka/RocketMQ）实现异步收发，且 JD 要求具备后端开发及稳定性保障能力。\n1. 在大模型推理耗时较长的情况下，你是如何利用消息队列解耦请求与响应的？前端如何感知处理进度？\n2. 如果消息消费失败或积压，你设计了哪些监控告警和补偿机制来保证系统最终一致性？结合 FastAPI 和 Redis，你是如何优化接口响应延迟的？', answer='', follow_ups=[], summary='', score=0, feedback='', is_terminated=False, follow_up_count=0), QuestionRecord(topic='Embedding 模型优化与检索性能', question="你在‘GithubRepoTagSystem'和‘CommitQualityEvaluation'项目中涉及了 Embedding 模型的微调与优化。针对企业级 RAG 系统的落地需求：\n1. 你是如何解决 Embedding 模型在小样本或特定领域下的过拟合问题的？\n2. 当向量库数据量增长到百万/千万级时，你会考虑哪些架构调整（如分片、近似搜索算法选择）来维持检索效率？请结合你使用过的技术栈谈谈实际调优经验。", answer='', follow_ups=[], summary='', score=0, feedback='', is_terminated=False, follow_up_count=0)]
    print("生成面试问题:", questions)
    return {
        "questions": questions,
        "current_question_index": 0,
    }
