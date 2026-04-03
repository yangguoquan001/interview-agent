# HISTORY - 决策记录与开发历史

## 2024-04-02 - 项目初始化

### 技术选型决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| **LLM 框架** | langchain-openai | 与 OpenAI API 集成成熟，支持结构化输出 |
| **工作流框架** | langgraph | 提供 DAG 编排 + 状态持久化，适合复杂对话流程 |
| **状态存储** | langgraph-checkpoint-sqlite | 轻量级，支持断点恢复，无需额外服务 |
| **数据校验** | pydantic | 类型安全，自动校验，与 langchain 集成好 |
| **配置管理** | pydantic-settings | 从 .env 加载配置，支持多格式 |

### 架构决策

1. **节点设计**: 采用单职责节点 (scanner/questioner/evaluator/chatter/saver)，每个节点独立可测试
2. **状态管理**: 使用 LangGraph 内置的 AgentState，继承 MessagesState 保留消息历史
3. **提示词分离**: 提示词模板统一放在 config/prompts.py，便于维护和调整
4. **LLM 工厂模式**: llm_factory.py 统一创建 LLM 实例，支持结构化输出配置

### 文件结构决策

```
src/
├── graph/     # 工作流编排
├── nodes/     # 节点实现
├── schemas/   # 数据模型
└── utils/     # 工具函数
```

---

## 2024-04-02 - 功能迭代

### 难度分级实现

- **Easy**: 基础概念、基本用法
- **Medium**: 实战应用、性能优化
- **Hard**: 底层原理、架构设计

### 追问功能实现

- 使用 chat_node 单独处理追问
- 循环边连接 evaluator → chat_node → router
- 用户输入 "next" 进入下一题，否则继续追问

### 记录持久化

- Markdown 格式保存到 records/日期/ 目录
- 包含主题、难度、来源文件、完整对话历史

---

## 2024-04-03 - Streamlit Web UI 开发

### Web 模块架构

```
src/web/
├── services/
│   ├── records.py     # 历史记录读取服务
│   └── interview.py  # 面试服务封装 (复用 LangGraph)
└── components/
    ├── sidebar.py     # 左侧栏 - 按日期显示历史记录
    └── chat.py        # 右侧聊天窗口 - 流式输出
```

### 功能实现

- **Sidebar**: 按日期分组显示 `records/` 目录下的 .md 文件
- **聊天窗口**: Agent 左，用户右，支持流式打字效果 (st.empty() + 增量更新)
- **模式切换**: 支持"查看历史记录"和"开始新面试"两种模式
- **状态管理**: 复用 Streamlit session_state 存储消息和服务实例

### 技术决策

1. **复用现有 workflow**: InterviewService 封装 LangGraph 工作流，零业务逻辑改动
2. **流式输出**: 使用 st.empty() 占位符 + 增量 markdown 更新实现打字机效果
3. **记录服务**: RecordService 独立于面试流程，按日期聚合历史 .md 文件

---

## 未来规划

- ~~Web UI: Streamlit~~ 已实现
- 定时任务: 每日面试提醒
- 简历面试: JD 匹配