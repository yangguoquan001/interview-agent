import json
from typing import Dict, Any

from langchain_core.messages import AIMessage, HumanMessage

from config import prompts
from src.utils.llm_fatory import get_chat_model
from src.schemas.states import ResumeAgentState



def generate_final_report(summaries: list) -> str:
    """生成综合评估报告"""
    # 如果summaries中每一项都为空，返回空字符串
    if all(not summary for summary in summaries):
        return ""
    
    llm = get_chat_model(temperature=0.3, streaming=True)
    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_REPORTER_PROMPT.format(
                    summaries=summaries
                )
            )
        ]
    )

    return response.content


def resume_reporter_node(state: ResumeAgentState) -> Dict[str, Any]:
    """综合报告节点"""
    question_records = state.get("question_records", [])
    summaries = [q.summary for q in question_records]

    # final_report = generate_final_report(summaries) #TODO
    final_report = """
候选人面试综合评估报告
评估人角色：资深技术面试官 / 人才评估专家
评估对象：AI 应用开发工程师（基于 RAG 方向）
面试轮次：终面/技术深度面
综合得分：75 分

1. 核心胜任力评估 (Core Competency Assessment)
专业技术深度：

优势：候选人对 RAG（检索增强生成）的核心链路具备扎实的认知，能够清晰阐述从数据预处理（自然段落分块、Chunk Size 合并）、检索策略（Bi-Encoder 初筛 + Cross-Encoder 重排序）到生成优化（Prompt 工程）的完整闭环。对 RAGFlow 等具体工具链有实战落地经验，非纯理论派。
短板：在系统性能调优与非功能性需求方面存在明显盲区。面对 Cross-Encoder 引入的延迟瓶颈时，未能提出架构级的解决方案（如缓存机制、异步降级、Top-K 动态限制、量化加速等），显示出其技术视野主要集中在功能实现层面，缺乏高并发或低延迟场景下的工程权衡能力。
通用性思考：分块策略停留在“基础配置”，缺乏针对特定业务语义的定制化思考（如父子索引、语义分块），表明其在处理复杂长文本或垂直领域知识时的泛化能力有待提升。
架构思维：

具备单点模块的设计能力，但在系统整体稳定性与扩展性设计上略显薄弱。未能将“延迟”视为一个需要系统性解决的工程问题，而是倾向于通过测试评估来侧面回应，反映出架构思维的局限性。
2. 逻辑与沟通表现 (Logic & Communication)
逻辑条理性：
候选人在陈述技术方案时结构清晰，善于使用编号列表和分层描述，能够将复杂的技术流程拆解为易于理解的步骤，具备良好的文档化思维和表达习惯。
压力应对与沟通技巧：
待改进：在第二轮追问中，当被直接挑战技术方案的痛点（延迟优化）时，候选人表现出回避倾向。未选择坦诚说明当前方案的局限或尝试推导替代方案，而是迅速转移话题至“测试数据集设计”。这种防御性沟通可能掩盖了真实的技术短板，不利于团队内部的技术复盘与风险暴露。
结论：沟通流畅度尚可，但在高压技术质疑下的诚实度与应变策略需加强。
3. 成长潜力与职业素养 (Growth Potential & Professionalism)
自驱力与学习意愿：
候选人展现出较强的动手实践能力，能够独立构建并优化智能聊天机器人系统，具备解决实际问题的意愿。
然而，对于性能瓶颈的回避态度暗示其可能在舒适区（功能开发）停留较久，主动探索底层优化或极端场景处理的动力不足。
职业成熟度：
具备基本的工程素养，但距离“资深工程师”的标准尚有差距。在面临技术决策的两难（准确率 vs 延迟）时，尚未形成成熟的权衡方法论。若入职，需要明确的导师指引以突破当前的技术天花板。
4. 最终录用建议 (Final Recommendation)
建议结论：建议录用 (Recommend Hire)
核心理由：
岗位匹配度：候选人 75 分的评分处于“熟练级”区间，其掌握的 RAG 全链路技能足以支撑当前阶段的应用开发工作，能够独立完成核心功能交付。
基础扎实：在 Prompt 工程和基础检索链路上的表现优于平均水平，具备快速上手业务的能力。
可塑性：虽然架构深度不足，但属于可以通过项目历练和代码审查（Code Review）弥补的范畴，而非完全的知识盲区。
风险提示与入职建议：
试用期关注重点：需重点关注其在高负载场景下的系统优化能力。建议在入职初期安排涉及性能压测或延迟敏感型任务，观察其是否具备主动排查和优化性能瓶颈的意识。
导师带教：分配一名在系统架构方面有经验的资深员工作为 Mentor，引导其建立“性能优先”的工程思维，避免陷入单纯的功能堆砌。
岗位定位：该候选人更适合定位为中级应用开发工程师，而非高级架构师或基础设施负责人。
评估日期：2023-XX-XX
备注：本报告基于提供的阶段性总结数据生成，建议结合 HR 背景调查及薪资期望进行最终决策。# 候选人面试综合评估报告

评估人角色：资深技术面试官 / 人才评估专家
评估对象：AI 应用开发工程师（基于 RAG 方向）
面试轮次：终面/技术深度面
综合得分：75 分

"""

    return {
        "final_report": final_report,
        "messages": [
            AIMessage(content=final_report)
        ]
    }

