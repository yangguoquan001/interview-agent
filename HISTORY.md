# 决策记录与开发历史

## 2024-04-10 - 项目初始化

### 技术选型
- **Web 框架**: Streamlit - 快速构建数据应用 UI
- **Agent 框架**: LangGraph - 可视化 Agent 工作流，支持状态持久化
- **LLM**: OpenAI GPT-4 - 通过 langchain-openai 调用
- **状态存储**: SQLite - 轻量级，无需额外服务

### 架构决策

#### 工作流设计
采用 LangGraph 的 StateGraph:
```
scanner -> questioner -> evaluator <-> chat_node -> saver
```
- scanner 扫描知识库文件
- questioner 基于文档生成面试题
- evaluator 评估用户回答
- chat_node 处理追问
- saver 保存面试记录

#### 状态管理
- 使用 SqliteSaver 持久化 AgentState
- Web 端通过 thread_id 隔离不同会话

### 功能清单
1. 面试流程自动化
2. 历史记录查看
3. 按日期分组记录

---

## 待完成功能

详见 TODO.md