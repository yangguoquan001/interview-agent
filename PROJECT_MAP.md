# Interview Agent - 项目架构与技术栈

## 1. 项目概述

**项目名称**: Interview Agent  
**项目类型**: AI 模拟面试工具  
**核心功能**: 基于 LangGraph 的智能面试系统，自动扫描本地知识库生成面试题并评估用户回答

## 2. 技术栈

| 层级 | 技术 | 版本要求 |
|------|------|----------|
| **LLM 框架** | langchain-openai | >=1.1.12 |
| **工作流框架** | langgraph | >=1.1.4 |
| **状态持久化** | langgraph-checkpoint-sqlite | >=3.0.3 |
| **应用监控** | langsmith | >=0.7.23 |
| **数据校验** | pydantic | >=2.12.5 |
| **配置管理** | pydantic-settings | >=2.13.1 |
| **Web UI** | streamlit | >=1.56.0 (待开发) |
| **Python 版本** | Python | >=3.12 |

## 3. 项目结构

```
interview-agent/
├── main.py                      # CLI 入口文件
├── pyproject.toml               # 项目依赖配置
├── .env                         # 环境变量配置
├── checkpoints.db               # SQLite 状态持久化
├── config/
│   ├── settings.py              # 配置管理 (文件目录、LLM、面试参数)
│   └── prompts.py               # 提示词模板 (出题、评估、追问)
├── src/
│   ├── graph/
│   │   └── workflow.py          # LangGraph 工作流定义
│   ├── nodes/
│   │   ├── scanner.py           # 扫描知识库文件
│   │   ├── questioner.py        # 生成面试问题
│   │   ├── evaluator.py         # 评估用户回答
│   │   ├── chatter.py           # 追答题疑
│   │   └── saver.py             # 保存面试记录
│   ├── schemas/
│   │   ├── states.py            # AgentState 定义
│   │   ├── data_models.py       # Pydantic 数据模型
│   │   └── enums.py             # 枚举类型 (难度等级)
│   └── utils/
│       ├── llm_fatory.py        # LLM 实例工厂
│       ├── files_ops.py         # 文件操作工具
│       └── database.py          # 数据库工具
└── records/                     # 面试记录输出目录
```

## 4. 核心模块

### 4.1 工作流 (workflow.py)
- **框架**: LangGraph StateGraph
- **节点**: scanner → questioner → evaluator → chat_node → saver
- **条件边**: evaluator 和 chat_node 循环处理追问

### 4.2 节点说明

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **scanner** | 扫描知识库，随机选择文件 | 无 | files_to_read |
| **questioner** | 根据文档内容生成面试题 | files_to_read | question, topic, difficulty |
| **evaluator** | 评估用户回答，给出评分和反馈 | question, answer | feedback |
| **chat_node** | 处理追问，提供深度技术解答 | 用户追问 | 技术回答 |
| **saver** | 持久化面试记录到 Markdown | 完整 state | 文件保存 |

### 4.3 数据模型

**AgentState**:
```python
- files_to_read: List[Path]   # 待面试的文件列表
- current_file: Path          # 当前使用的文件
- question: str               # 面试问题
- answer: str                 # 用户回答
- feedback: str               # 评估反馈
- topic: str                  # 面试主题
- difficulty: str             # 难度 (简单/中等/困难)
- thread_id: str              # 线程标识
- messages: List[BaseMessage] # 消息历史
```

## 5. 配置文件

### 环境变量 (.env)
```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
```

### 知识库配置 (settings.py)
- `FILE_DIRS`: 知识库目录列表
- `EXCLUDED_DIRS`: 排除目录 (.git, node_modules 等)
- `EXCLUDED_FILES`: 排除文件 (README.md 等)
- `NUM_QUESTIONS`: 每次面试题目数量 (默认 2)

## 6. 数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  scanner    │ ──▶ │ questioner  │ ──▶ │ evaluator   │
│  扫描文件   │     │ 生成问题    │     │ 评估回答    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌─────────────┐     ┌──────▼──────┐
                    │   saver     │ ◀── │ chat_node   │
                    │ 保存记录    │     │ 追问解答    │
                    └─────────────┘     └─────────────┘
```

## 7. 状态持久化

- **方案**: SQLite Checkpoint (langgraph-checkpoint-sqlite)
- **数据库文件**: `checkpoints.db`
- **恢复机制**: 支持中断后通过 thread_id 恢复面试进度