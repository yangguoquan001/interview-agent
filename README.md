# Interview Agent

基于 LangGraph 的 AI 模拟面试工具，通过扫描本地知识库（Markdown 文件）自动生成面试问题，并评估用户的回答。

## 功能特性

- **知识库扫描**：自动扫描指定目录下的 `.md` 文件作为面试素材
- **智能出题**：根据文档内容生成不同难度（Easy/Medium/Hard）的面试题
- **回答评估**：基于参考文档对用户回答进行评分和反馈
- **追问答疑**：支持用户针对反馈进行追问，获得深度技术解答
- **进度保存**：使用 SQLite Checkpoint 保存面试进度，支持中断后恢复
- **Web 界面**：提供 Streamlit 图形化界面，支持历史记录查看

## 项目结构

```
interview-agent/
├── main.py                      # CLI 入口文件
├── web_app.py                   # Web 入口文件 (Streamlit)
├── pyproject.toml               # 项目依赖配置
├── .env                         # 环境变量配置
├── checkpoints.db               # SQLite 状态持久化
├── config/
│   ├── settings.py              # 配置管理 (文件目录、LLM、面试参数)
│   └── prompts.py               # 提示词模板 (出题、评估、追问)
├── src/
│   ├── graph/
│   │   └── workflow.py         # LangGraph 工作流定义
│   ├── nodes/
│   │   ├── scanner.py          # 扫描知识库文件
│   │   ├── questioner.py      # 生成面试问题
│   │   ├── evaluator.py       # 评估用户回答
│   │   ├── chatter.py         # 追答题疑
│   │   └── saver.py           # 保存面试记录
│   ├── schemas/
│   │   ├── states.py          # AgentState 定义
│   │   ├── data_models.py     # Pydantic 数据模型
│   │   └── enums.py           # 枚举类型 (难度等级)
│   ├── utils/
│   │   ├── llm_fatory.py      # LLM 实例工厂
│   │   ├── files_ops.py       # 文件操作工具
│   │   └── database.py        # 数据库工具
│   └── web/                   # Streamlit Web 模块
│       ├── services/
│       │   ├── records.py     # 历史记录读取服务
│       │   └── interview.py   # 面试服务封装
│       └── components/
│           ├── sidebar.py     # 左侧栏组件
│           └── chat.py        # 聊天窗口组件
└── records/                    # 面试记录输出目录
```

## 快速开始

### 1. 配置环境变量

创建 `.env` 文件：

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
```

### 2. 配置知识库目录

在 `.env` 中设置 `FILE_DIRS`（多个目录用逗号分隔）：

```env
FILE_DIRS = ["path/to/your/knowledge/docs1", "path/to/docs2"]
```

### 3. 运行

```bash
# CLI 模式
python main.py

# Web 模式
python -m streamlit run web_app.py
```

## 使用流程

### CLI 模式

1. **启动**：运行 `main.py`，自动扫描知识库
2. **答题**：根据 AI 提出的面试题输入回答
3. **评估**：AI 给出评分和改进建议
4. **追问**：可选择输入追问或输入 `next` 进入下一题
5. **记录**：每轮问答自动保存到 `records/` 目录

### Web 模式

1. **启动**：运行 `web_app.py`，打开浏览器访问
2. **Sidebar**：左侧显示历史面试记录（按日期分组）
3. **开始面试**：点击"开始面试"按钮
4. **答题**：在聊天窗口输入回答
5. **评估**：AI 流式输出评估反馈
6. **追问**：输入追问或输入 `next` 进入下一题

## 待优化项

- [ ] 优化用户输入展示延迟
- [ ] 实现 Agent 输出流式显示
- [ ] 修复侧边栏"开始新面试"按钮
- [ ] 每日定时自动生成面试清单
- [ ] 简历+JD 模拟面试功能