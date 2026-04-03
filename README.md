# Interview Agent

基于 LangGraph 的 AI 模拟面试工具，通过扫描本地知识库（Markdown 文件）自动生成面试问题，并评估用户的回答。

## 功能特性

- **知识库扫描**：自动扫描指定目录下的 `.md` 文件作为面试素材
- **智能出题**：根据文档内容生成不同难度（Easy/Medium/Hard）的面试题
- **回答评估**：基于参考文档对用户回答进行评分和反馈
- **追问答疑**：支持用户针对反馈进行追问，获得深度技术解答
- **进度保存**：使用 SQLite Checkpoint 保存面试进度，支持中断后恢复

## 项目结构

```
interview-agent/
├── config/
│   ├── prompts.py      # 提示词模板
│   └── settings.py    # 配置文件
├── src/
│   ├── graph/
│   │   └── workflow.py    # LangGraph 工作流定义
│   ├── nodes/
│   │   ├── scanner.py    # 扫描知识库文件
│   │   ├── questioner.py # 生成面试问题
│   │   ├── evaluator.py  # 评估用户回答
│   │   ├── chatter.py    # 追问答疑
│   │   └── saver.py      # 保存记录
│   ├── schemas/
│   │   ├── data_models.py
│   │   ├── states.py
│   │   └── enums.py
│   └── utils/
├── main.py             # 入口文件
└── .env               # 环境变量配置
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

在 `config/settings.py` 中设置 `FILE_DIRS`：

```python
FILE_DIRS = ["path/to/your/knowledge/docs"]
```

### 3. 运行

```bash
python main.py
```

## 使用流程

1. **启动**：运行 `main.py`，自动扫描知识库
2. **答题**：根据 AI 提出的面试题输入回答
3. **评估**：AI 给出评分和改进建议
4. **追问**：可选择输入追问或输入 `next` 进入下一题
5. **记录**：每轮问答自动保存到 `records/` 目录

## TODO

- [ ] **Web 界面**：开发图形化界面，提升用户体验
- [ ] **每日定时自动生成面试清单**：配置定时任务，每日自动生成面试题并通知用户
- [ ] **简历+JD 模拟面试**：根据用户简历和目标职位 JD 生成针对性面试问题
