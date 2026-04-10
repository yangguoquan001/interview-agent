# 项目架构与技术栈

## 技术栈

### 后端框架
- **Streamlit 1.56.0** - Web UI 框架
- **LangGraph 1.1.4** - Agent 工作流框架
- **LangChain OpenAI 1.1.12** - LLM 调用封装
- **Pydantic 2.12.5** - 数据模型验证

### 数据存储
- **SQLite** - 面试状态持久化 (checkpoints.db)
- **文件系统** - 面试记录存储 (records/*.md)

### 核心依赖
- langgraph-checkpoint-sqlite: 状态持久化
- langsmith: 运行时追踪
- pydantic-settings: 配置管理

## 项目结构

```
interview-agent/
├── web_app.py                 # Streamlit 入口
├── main.py                    # CLI 入口
├── config/
│   ├── settings.py            # 配置管理
│   └── prompts.py            # Prompt 模板
├── src/
│   ├── graph/
│   │   └── workflow.py       # LangGraph 工作流
│   ├── nodes/
│   │   ├── scanner.py        # 扫描知识库
│   │   ├── questioner.py     # 生成面试题
│   │   ├── evaluator.py      # 评估回答
│   │   ├── chatter.py        # 追问功能
│   │   └── saver.py          # 保存记录
│   ├── schemas/
│   │   ├── states.py         # AgentState 定义
│   │   ├── enums.py          # 枚举类型
│   │   └── data_models.py    # 数据模型
│   ├── utils/
│   │   ├── llm_fatory.py     # LLM 工厂
│   │   ├── database.py       # 数据库工具
│   │   └── files_ops.py      # 文件操作
│   └── web/
│       ├── components/
│       │   ├── chat.py       # 聊天界面
│       │   └── sidebar.py    # 侧边栏
│       └── services/
│           ├── interview.py  # 面试服务
│           └── records.py   # 记录服务
└── records/                  # 面试记录存储
    └── YYYYMMDD/
        └── *.md
```

## 工作流架构

```
scanner -> questioner -> evaluator <-> chat_node -> saver
                              ^                   |
                              |___________________|
```

- **scanner**: 扫描知识库文件
- **questioner**: 基于文档内容生成面试题
- **evaluator**: 评估用户回答
- **chat_node**: 追问环节
- **saver**: 保存面试记录