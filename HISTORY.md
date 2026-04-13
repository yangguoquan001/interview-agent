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

## 2026-04-13 - 删除记录功能

### 功能新增
- 增加删除面试记录功能
- RecordService 新增 delete_record 方法
- 侧边栏每条记录增加删除按钮 🗑️

### UI 优化
- 调整列比例 [4, 0.6] 解决窄屏下 emoji 按钮溢出问题

---

## 2026-04-13 - 下一题功能

### 功能新增
- 面试过程中增加"下一题"按钮
- 点击后保存当前面试状态，重新生成下一题
- 使用三列布局 [8, 1, 1] 优化按钮排列

### UI 优化
- 调整按钮布局为三列，更清晰简洁

---

## 2026-04-13 - 返回按钮功能

### 功能新增
- 记录查看页面增加"← 返回"按钮
- 点击后切回聊天界面

---

## 待完成功能

详见 TODO.md