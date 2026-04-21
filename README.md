# AI 模拟面试 Agent

基于 LangGraph 和 Streamlit 构建的 AI 模拟面试系统，支持两种面试模式。

## 功能特性

### 知识面试模式
- 🎯 **智能出题**: 基于知识库文档自动生成面试题
- 📊 **多难度级别**: 支持 Easy/Medium/Hard 难度
- 💬 **交互式面试**: 评估回答并支持追问
- 🔄 **连续面试**: 支持连续进行多轮面试
- 📚 **历史记录**: 自动保存面试记录，支持回顾和删除

### 简历面试模式
- 📄 **简历解析**: 自动解析候选人简历关键信息
- 🎯 **JD 匹配**: 根据职位描述生成针对性问题
- 💬 **深度追问**: 支持多轮追问挖掘技术细节
- 📊 **综合评估**: 生成面试评估报告和能力分析

### 通用功能
- 🔒 **状态持久化**: 使用 SQLite 存储面试状态，断点续面
- 📖 **历史记录**: 支持历史面试记录查看和删除

## 技术栈

- **Streamlit** - Web UI
- **LangGraph** - Agent 工作流
- **LangChain** - LLM 调用
- **SQLite** - 状态持久化
- **pydantic** - 数据验证

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

创建 `.env` 文件，配置 LLM API:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
```

### 3. 运行应用

```bash
uv run streamlit run web_app.py
```

## 项目结构

```
interview-agent/
├── web_app.py                 # Streamlit 入口
├── config/
│   ├── settings.py           # 配置管理
│   └── prompts.py            # Prompt 模板
├── src/
│   ├── graph/
│   │   ├── knowledge_graph.py    # 知识面试工作流
│   │   └── resume_graph.py       # 简历面试工作流
│   ├── nodes/
│   │   ├── knowledge_*.py        # 知识面试节点
│   │   ├── resume_*.py           # 简历面试节点
│   │   └── resume_parser.py      # 简历解析
│   ├── schemas/
│   │   ├── states.py            # AgentState 定义
│   │   ├── enums.py             # 枚举类型
│   │   └── data_models.py       # 数据模型
│   ├── utils/
│   │   ├── llm_factory.py       # LLM 工厂
│   │   ├── database.py          # 数据库工具
│   │   ├── files_ops.py         # 文件操作
│   │   └── pdf_reader.py       # PDF 读取
│   └── web/
│       ├── components/
│       │   ├── knowledge_chat.py   # 知识面试界面
│       │   ├── resume_chat.py       # 简历面试界面
│       │   └── sidebar.py          # 侧边栏
│       └── services/
│           ├── interview.py        # 面试服务
│           └── records.py          # 记录服务
└── records/                   # 面试记录存储
```

## 使用方法

### 知识面试
1. 点击"💬 知识面试"标签页
2. 点击"开始面试"按钮
3. 系统从知识库读取文档并生成面试题
4. 输入你的回答
5. 面试官评估后可能会追问
6. 可选择"下一题"继续，或"结束面试"保存记录

### 简历面试
1. 点击"📄 简历面试"标签页
2. 粘贴你的简历内容
3. 粘贴目标职位描述 (JD)
4. 系统生成针对性面试问题
5. 回答问题，支持多轮追问
6. 面试结束生成综合评估报告

### 查看历史记录
- 点击左侧边栏"📚 历史记录"
- 选择记录查看详情
- 可删除不需要的记录

## 开发说明

### 代码检查

```bash
uv run ruff check .
```