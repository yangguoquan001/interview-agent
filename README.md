# AI 模拟面试 Agent

基于 LangGraph 和 Streamlit 的 AI 模拟面试系统，可根据知识库文档生成面试题并评估用户回答。

## 功能特性

- 🎯 **智能出题**: 基于知识库文档自动生成面试题
- 📊 **多难度级别**: 支持 Easy/Medium/Hard 难度
- 💬 **交互式面试**: 评估回答并追问
- 📚 **历史记录**: 自动保存面试记录，支持回顾
- 🔄 **工作流持久化**: 使用 SQLite 存储面试状态

## 技术栈

- **Streamlit** - Web UI
- **LangGraph** - Agent 工作流
- **LangChain OpenAI** - LLM 调用
- **SQLite** - 状态持久化

## 快速开始

### 1. 安装依赖

```bash
cd D:\MyRepos\interview-agent
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
├── web_app.py              # Streamlit 入口
├── src/
│   ├── graph/workflow.py  # LangGraph 工作流
│   ├── nodes/             # 节点实现
│   ├── web/               # Web 组件
│   └── schemas/           # 数据模型
├── records/               # 面试记录
└── config/                # 配置
```

## 使用方法

1. 点击"开始面试"按钮
2. 系统从知识库读取文档并生成面试题
3. 输入你的回答
4. 面试官评估后可能会追问
5. 面试结束后自动保存记录
6. 可在左侧查看历史记录

## 开发说明

### 后端测试

```bash
cd backend/app
PYTHONPATH=. uv run pytest -v
```

### 代码规范

使用 ruff 进行 linting:

```bash
uv run ruff check .
```