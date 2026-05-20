# LLM Agent 开发教学项目

## 项目大纲

---

### 一、项目概述

#### 1.1 项目简介
- 项目名称：LLM Agent 开发教学项目
- 项目目标：系统学习 LLM 工具调用、技能管理、链式调用等核心能力
- 技术栈：Python、LLM API、OpenAI 兼容接口

#### 1.2 学习路径
| 阶段 | 模块 | 核心能力 | 文件 |
|------|------|----------|------|
| 入门 | practice01 | 基础 LLM 客户端开发 | llm_client.py, llm_client_v2.py |
| 进阶 | practice02 | 工具调用机制 | llm_client_with_tools.py, tools.py |
| 高级 | practice03-04 | 聊天记录处理与关键信息提取 | llm_client_with_summary.py, llm_client_with_keyinfo.py |
| 技能 | practice05-07 | 技能管理与调用 | chat_client.py, tools.py |
| 专家 | practice08 | 链式工具调用 | chat_client.py, tools.py |

---

### 二、目录结构

```
d:\ai对话/
├── .agents/                    # 技能管理目录
│   └── skills/                # 技能仓库
│       ├── Notice/            # 通知撰写技能
│       │   └── SKILL.md       # 技能定义文件
│       └── weather/           # 天气查询技能
│           └── SKILL.md       # 技能定义文件
├── practice01/                # 基础 LLM 客户端
│   ├── llm_client.py          # 基础 API 调用
│   └── llm_client_v2.py       # 终端聊天增强版
├── practice02/                # 工具调用功能
│   ├── tools.py               # 文件操作工具
│   ├── llm_client_with_tools.py  # 工具调用客户端
│   └── test_*.py              # 测试文件
├── practice03/                # 聊天记录总结
│   ├── tools.py               # 工具函数
│   ├── llm_client_with_summary.py  # 总结功能
│   └── README.md              # 模块说明
├── practice04/                # 关键信息提取
│   ├── tools.py               # 工具函数
│   ├── llm_client_with_keyinfo.py  # 关键信息提取
│   └── README.md              # 模块说明
├── practice05/                # 文档仓库查询
│   ├── tools.py               # 工具函数(含AnythingLLM)
│   ├── chat_client.py         # 聊天客户端
│   └── README.md              # 模块说明
├── practice06/                # 技能调用与通知撰写
│   ├── tools.py               # 工具函数
│   ├── chat_client.py         # 聊天客户端
│   └── README.md              # 模块说明
├── practice07/                # 纯技能调用
│   ├── tools.py               # 工具函数
│   ├── chat_client.py         # 聊天客户端
│   └── README.md              # 模块说明
├── practice08/                # 链式工具调用
│   ├── tools.py               # 工具函数(含ChainedCallContext)
│   ├── chat_client.py         # 聊天客户端
│   ├── test01.txt             # 测试数据1
│   ├── test02.txt             # 测试数据2
│   └── README.md              # 模块说明
├── .env                       # 环境变量配置
├── env.example                # 环境变量示例
├── .gitignore                 # Git 忽略配置
└── README.md                  # 项目主文档
```

---

### 三、核心功能模块

#### 3.1 基础 LLM 客户端 (practice01)
- **功能**：基础 API 调用、流式输出、聊天历史管理
- **文件**：llm_client.py, llm_client_v2.py
- **学习目标**：理解 LLM API 调用原理

#### 3.2 工具调用系统 (practice02)
- **功能**：文件操作、互联网搜索
- **工具列表**：list_files, rename_file, delete_file, create_file, read_file, search_internet
- **学习目标**：掌握工具调用机制

#### 3.3 聊天记录处理 (practice03-04)
- **功能**：聊天记录总结、关键信息提取
- **学习目标**：掌握文本处理技巧

#### 3.4 文档仓库查询 (practice05)
- **功能**：AnythingLLM 集成、文档检索
- **学习目标**：掌握外部知识库集成

#### 3.5 技能管理系统 (practice06-07)
- **功能**：技能加载、技能调用、通知撰写
- **技能列表**：notice（通知撰写）、weather（天气查询）
- **学习目标**：掌握技能管理与调用

#### 3.6 链式工具调用 (practice08)
- **功能**：多工具顺序调用、中间结果传递、上下文管理
- **核心组件**：ChainedCallContext 链式调用上下文管理器
- **学习目标**：掌握复杂任务分解与执行

---

### 四、配置与运行

#### 4.1 环境配置
```bash
# 复制环境变量示例
cp env.example .env

# 编辑 .env 文件，添加 API 密钥
# BASE_URL=http://localhost:11434/api/chat
# MODEL=llama3
# API_KEY=your_api_key
```

#### 4.2 运行各模块

| 模块 | 命令 | 功能描述 |
|------|------|----------|
| 基础聊天 | `python practice01/llm_client_v2.py` | 基础终端聊天 |
| 工具调用 | `python practice02/llm_client_with_tools.py` | 文件操作与搜索 |
| 文档查询 | `python practice05/chat_client.py` | AnythingLLM 查询 |
| 技能调用 | `python practice06/chat_client.py` | 技能调用与通知撰写 |
| 链式调用 | `python practice08/chat_client.py` | 链式工具调用 |

---

### 五、工具函数清单

#### 5.1 文件操作工具 (practice02)
| 工具名 | 功能 | 参数 |
|--------|------|------|
| list_files | 列出目录文件 | directory (str) |
| rename_file | 重命名文件 | directory, old_name, new_name |
| delete_file | 删除文件 | directory, filename |
| create_file | 创建文件 | directory, filename, content |
| read_file | 读取文件 | directory, filename |
| search_internet | 搜索互联网 | query (str) |

#### 5.2 技能相关工具 (practice06-08)
| 工具名 | 功能 | 参数 |
|--------|------|------|
| list_available_skills | 列出可用技能 | 无 |
| load_skill_content | 加载技能内容 | skill_name (str) |

#### 5.3 链式调用工具 (practice08)
| 工具名 | 功能 | 参数 |
|--------|------|------|
| read_file | 读取文件内容 | file_path (str) |
| extract_info | 提取信息 | text (str), pattern (str) |
| format_data | 格式化数据 | data, format_type (str) |

---

### 六、技能定义规范

#### 6.1 SKILL.md 格式
```markdown
---
name: notice
description: 撰写、修改、润色通知
---

## 通知撰写规范

### 基本要求
1. 通知标题不能只有"通知"二字
2. 必须冠以"某某部"的前缀

### 规范格式
#### 标题
某某部通知

#### 正文
- **开头**：称呼（如"全体员工"）
- **正文内容**：清晰表达通知事项
- **结尾**：发布部门
```

#### 6.2 技能开发步骤
1. 在 `.agents/skills/` 下创建技能目录
2. 创建 `SKILL.md` 文件
3. 在 `YAML front matter` 中定义 `name` 和 `description`
4. 在正文部分编写技能执行说明

---

### 七、链式调用示例

#### 7.1 调用格式
```json
{"tool_calls": [
  {"tool_name": "read_file", "parameters": {"file_path": "practice08/test01.txt"}},
  {"tool_name": "extract_info", "parameters": {"text": "$read_file_result", "pattern": "姓名"}},
  {"tool_name": "format_data", "parameters": {"data": "$extract_info_result", "format_type": "json"}}
]}
```

#### 7.2 执行流程
1. **步骤1**：read_file 读取文件 → 结果存储到 `read_file_result`
2. **步骤2**：extract_info 使用 `$read_file_result` 作为输入 → 结果存储到 `extract_info_result`
3. **步骤3**：format_data 使用 `$extract_info_result` 作为输入 → 最终结果

---

### 八、学习路径建议

| 阶段 | 学习内容 | 实践任务 |
|------|----------|----------|
| 第1周 | practice01 | 完成基础聊天客户端 |
| 第2周 | practice02 | 实现工具调用功能 |
| 第3周 | practice03-04 | 掌握文本处理技巧 |
| 第4周 | practice05 | 集成外部知识库 |
| 第5周 | practice06-07 | 开发技能管理系统 |
| 第6周 | practice08 | 实现链式工具调用 |

---

### 九、常见问题

#### 9.1 环境变量配置
- 确保 `.env` 文件存在于项目根目录
- API_KEY 需要正确配置
- BASE_URL 根据使用的 LLM 服务调整

#### 9.2 工具调用失败
- 检查工具名称是否正确
- 检查参数是否完整
- 检查文件路径是否正确

#### 9.3 链式调用问题
- 确保变量引用格式正确（使用 `$变量名`）
- 前一个工具必须成功执行才能传递结果
- 最大迭代次数为 10 次，防止无限循环

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-04-29 | v1.0 | 初始化项目结构 |
| 2026-05-06 | v1.1 | 添加链式工具调用功能 |