# TODO - 待办事项清单

## 优先级 P0 - 必须完成

| 序号 | 任务描述 | 状态 | 备注 |
|------|----------|------|------|
| T001 | 完善 CLI 交互体验 (输入验证、错误处理) | pending | main.py |
| T002 | 添加日志系统 (结构化日志) | pending | src/utils |
| T003 | 完善单元测试 | pending | tests/ |

## 优先级 P1 - 重要功能

| 序号 | 任务描述 | 状态 | 备注 |
|------|----------|------|------|
| T004 | ~~开发 Streamlit Web 界面~~ | ~~completed~~ | web_app.py |
| T005 | 支持多文件知识库管理界面 | pending | config/settings.py |
| T006 | ~~面试记录历史查看功能~~ | ~~completed~~ | src/web/components/sidebar.py |
| T009 | 优化用户输入展示延迟 | pending | src/web/components/chat.py |
| T010 | ~~实现 Agent 输出流式显示~~ | ~~completed~~ | src/web/components/chat.py |
| T015 | 可以中断 Agent 的输出 | pending | src/web/components/chat.py |
| T011 | 修复侧边栏"开始新面试"按钮无反应 | pending | src/web/components/sidebar.py |
| T012 | 添加终止当前面试按钮 (终止后不保存) | pending | src/web/components/chat.py |
| T013 | 将"下一题"从输入改为按钮 | pending | src/web/components/chat.py |
| T014 | 支持跳过当前问题 (不消耗次数) | pending | src/web/components/chat.py |

## 优先级 P2 - 规划中

| 序号 | 任务描述 | 状态 | 备注 |
|------|----------|------|------|
| T007 | 每日定时自动生成面试清单 | pending | 定时任务 |
| T008 | 简历+JD 模拟面试功能 | pending | 需要简历解析 |

---

## 使用说明

- **pending**: 待开始
- **in_progress**: 进行中
- **completed**: 已完成
- **cancelled**: 已取消