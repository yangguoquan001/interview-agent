# AI 模拟面试 Agent

基于 LangGraph 和 Streamlit 构建的 AI 模拟面试系统，可根据知识库文档生成面试题并评估用户回答。

## 功能特性

- 🎯 **智能出题**: 基于知识库文档自动生成面试题
- 📊 **多难度级别**: 支持 Easy/Medium/Hard 难度
- 💬 **交互式面试**: 评估回答并支持追问
- 🔄 **连续面试**: 支持连续进行多轮面试
- 📚 **历史记录**: 自动保存面试记录，支持回顾和删除
- 🔒 **状态持久化**: 使用 SQLite 存储面试状态，断点续面

## 技术栈

- **Streamlit** - Web UI
- **LangGraph** - Agent 工作流
- **LangChain OpenAI** - LLM 调用
- **SQLite** - 状态持久化

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

创建 `.env` 文件，添加 OpenAI API Key:

```env
OPENAI_API_KEY=your_api_key_here
```

### 3. 运行应用

```bash
uv run streamlit run web_app.py
```

## 项目结构

```
interview-agent/
├── web_app.py                 # Streamlit 入口
├── main.py                    # CLI 入口
├── config/
│   ├── settings.py            # 配置管理
│   └── prompts.py             # Prompt 模板
├── src/
│   ├── graph/
│   │   └── workflow.py        # LangGraph 工作流
│   ├── nodes/
│   │   ├── scanner.py         # 扫描知识库
│   │   ├── questioner.py      # 生成面试题
│   │   ├── evaluator.py       # 评估回答
│   │   ├── chatter.py         # 追问功能
│   │   └── saver.py           # 保存记录
│   ├── schemas/
│   │   ├── states.py          # AgentState 定义
│   │   ├── enums.py           # 枚举类型
│   │   └── data_models.py     # 数据模型
│   ├── utils/
│   │   ├── llm_fatory.py      # LLM 工厂
│   │   ├── database.py        # 数据库工具
│   │   └── files_ops.py       # 文件操作
│   └── web/
│       ├── components/
│       │   ├── chat.py        # 聊天界面
│       │   └── sidebar.py      # 侧边栏
│       └── services/
│           ├── interview.py   # 面试服务
│           └── records.py     # 记录服务
└── records/                   # 面试记录存储
```

## 使用方法

1. 点击"开始面试"按钮
2. 系统从知识库读取文档并生成面试题
3. 输入你的回答
4. 面试官评估后可能会追问
5. 可选择"下一题"继续面试，或"结束面试"保存记录
6. 在左侧查看历史记录，可回顾或删除

## 开发说明

### 代码规范

```bash
uv run ruff check .
```
