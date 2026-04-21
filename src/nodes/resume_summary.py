from langchain_core.messages import AIMessage, HumanMessage
from typing import Dict, Any

from config import prompts
from src.schemas.states import ResumeAgentState
from src.utils.llm_fatory import get_chat_model


def generate_summary(
    questions: list, answers: list
) -> str:
    """生成问题总结"""
    llm = get_chat_model(temperature=0.3, streaming=True)
    question_answer_pairs = []
    for i in range(len(questions)):
        question = questions[i]
        answer = answers[i]
        question_answer_pairs.append({"role": "assistant", "content": question})
        question_answer_pairs.append({"role": "user", "content": answer})

    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_SUMMARY_PROMPT.format(
                    chat_history=question_answer_pairs
                )
            )
        ]
    )

    return response.content


def resume_summary_node(state: ResumeAgentState) -> Dict[str, Any]:
    """问题总结节点"""
    current_index = state.get("current_question_index", 0)
    question_records = state["question_records"]
    curr_question_record = question_records[current_index]
    current_questions = curr_question_record.questions
    current_answers = curr_question_record.answers

    summary = generate_summary(
        current_questions,
        current_answers
    )
    # 以下为模拟数据，用于测试。
    # summary = """
    # #### 1. 总结 (Summary)
    # 候选人基于 RAGFlow 构建了智能聊天机器人系统。在技术方案上，采用了自然段落分块与 Chunk Size 合并的策略；检索阶段使用 Bi-Encoder 初筛后接 Cross-Encoder 重排序以提升准确率；针对低相关性回答，通过提示词工程（拒答机制、Few-Shot、思维链）进行优化。但在面对性能瓶颈（延迟）的追问时，未能给出具体的架构级优化方案（如缓存、降级、Top-K 限制），转而讨论了测试数据集的设计。

    # #### 2. 评分 (Score)
    # **75 分**
    # （属于熟练级。候选人对 RAG 核心组件有清晰的认知和实战经验，逻辑自洽，但在系统性能调优的深度权衡上略显不足，未直接回应面试官关于延迟优化的具体技术细节。）

    # #### 3. 反馈 (Feedback)
    # *   **闪光点 (Strengths)**：
    #     *   **技术栈清晰**：准确描述了从分块、检索到重排序的完整 RAG 链路，提到了 RAGFlow、Cross-Encoder 等具体工具/算法。
    #     *   **Prompt 工程扎实**：针对幻觉和低相关性场景，提出了具体的三种策略（拒答、Few-Shot、CoT），具备实际落地经验。
    #     *   **结构清晰**：回答问题条理分明，使用了编号列表，便于理解。
    # *   **待改进点 (Weaknesses)**：
    #     *   **性能优化深度不足**：在第二轮追问中，面试官明确询问了如何处理 Cross-Encoder 带来的延迟瓶颈（如 Top-K 限制、缓存、降级），候选人回避了这些具体的工程手段，仅重复了 Bi-Encoder 流程并转向了测试评估话题。
    #     *   **分块策略通用性**：提到的分块策略为“基础配置”，缺乏针对特定业务场景的定制化优化思考（如语义分块、父子索引等）。

    # #### 4. 终止状态 (Terminated)
    # **答完当前问题**
    # （候选人完成了对话轮次的回答，未出现因知识盲区导致的无法作答或强行跳过，但第二问的回答质量存在偏离主题的情况。）

    # """

    curr_question_record.summary = summary

    return {
        "question_records": question_records,
        "current_question_index": current_index+1,
        "last_answer": "",
        "messages": [
            AIMessage(content=summary)
        ]
    }
