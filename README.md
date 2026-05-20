# LLM Client Project

## 项目结构

```
.
├── practice01/
│   ├── llm_client.py      # 基础 LLM API 客户端代码
│   └── llm_client_v2.py   # 终端聊天增强版客户端代码
├── practice02/
│   ├── tools.py           # 工具调用功能模块
│   └── llm_client_with_tools.py  # 支持工具调用的客户端代码
├── practice03/
│   ├── README.md          # 聊天记录总结工具说明
│   └── llm_client_with_summary.py  # 聊天记录总结客户端代码
├── practice04/
│   ├── README.md          # 关键信息提取工具说明
│   └── llm_client_with_keyinfo.py  # 关键信息提取客户端代码
├── practice05/
│   ├── README.md          # 文档仓库查询工具说明
│   ├── chat_client.py     # 文档仓库查询客户端代码
│   └── tools.py           # 工具函数定义
├── practice06/
│   ├── README.md          # 技能调用与通知撰写工具说明
│   ├── chat_client.py     # 技能调用客户端代码
│   └── tools.py           # 工具函数定义（包含anythingllm_query和技能函数）
├── practice07/
│   ├── README.md          # 链式工具调用说明
│   ├── chat_client.py     # 链式工具调用客户端代码
│   └── tools.py           # 工具函数定义（包含文件操作和网页处理工具）
├── practice08/
│   ├── README.md          # 高级链式工具调用说明
│   ├── chat_client.py     # 高级链式工具调用客户端代码
│   ├── tools.py           # 工具函数定义（支持变量引用）
│   ├── test01.txt         # 测试文件1
│   └── test02.txt         # 测试文件2
├── venv/                # Python 虚拟环境
├── .env                 # 环境变量配置文件
├── .gitignore           # Git 忽略文件配置
└── env.example          # 环境变量示例文件
```

## Python 代码功能说明

### practice01/llm_client.py

该文件实现了一个简单的 LLM (Large Language Model) API 客户端，主要功能如下：

1. **环境变量加载** (`load_env` 函数)
   - 从项目根目录的 `.env` 文件中读取环境变量
   - 支持的环境变量包括：
     - `BASE_URL`: API 基础 URL（默认值：`https://api.openai.com/v1`）
     - `MODEL`: 使用的模型（默认值：`gpt-4`）
     - `API_KEY`: API 密钥（必须）
   - 包含错误处理，当 .env 文件不存在或读取失败时给出提示

2. **LLM API 调用** (`call_llm` 函数)
   - 接受用户输入的 prompt 和环境变量作为参数
   - 构建 API 请求数据，包括模型、消息和温度参数
   - 发送 HTTP 请求到指定的 API 端点
   - 处理 API 响应，包括：
     - 提取响应内容
     - 计算 token 使用情况（提示词 token、完成 token、总 token）
     - 计算响应时间和 token 处理速度
     - 处理 HTTP 错误和其他异常

3. **主函数** (`main` 函数)
   - 加载环境变量
   - 使用测试 prompt（"请解释什么是人工智能"）调用 API
   - 显示 API 响应结果或错误信息
   - 显示统计信息，包括 token 使用情况、响应时间和处理速度

### practice01/llm_client_v2.py

该文件实现了一个增强版的终端聊天工具，在基础版的基础上添加了以下功能：

1. **终端界面输入**
   - 支持在终端中实时输入聊天内容
   - 按 Enter 发送消息，按 Ctrl+C 退出

2. **流式输出**
   - 启用 API 的流式输出功能
   - 实时显示 AI 的响应内容，模拟自然对话体验

3. **历史聊天记录管理**
   - 自动记录聊天历史
   - 在每次请求中自动添加上下文，实现连续对话
   - 支持多轮对话，保持上下文连贯性

4. **循环运行机制**
   - 持续运行，直到用户按 Ctrl+C 退出
   - 每次对话后显示统计信息

5. **增强的错误处理**
   - 处理 HTTP 错误和其他异常
   - 在出错时保持聊天历史的一致性

### practice02/tools.py

该文件实现了6个工具，用于支持LLM的工具调用功能：

1. **list_files(directory)**
   - 列出指定目录下的所有文件和子目录
   - 返回文件列表和文件数量
   - 包含错误处理，检查目录是否存在

2. **rename_file(directory, old_name, new_name)**
   - 修改指定目录下文件的名字
   - 检查原文件是否存在，目标文件是否已存在
   - 返回操作结果和相关信息

3. **delete_file(directory, filename)**
   - 删除指定目录下的文件
   - 检查文件是否存在，确保不是目录
   - 返回操作结果

4. **create_file(directory, filename, content)**
   - 在指定目录下创建新文件并写入内容
   - 检查目录是否存在，文件是否已存在
   - 返回操作结果和内容长度信息

5. **read_file(directory, filename)**
   - 读取指定目录下文件的内容
   - 检查文件是否存在，确保不是目录
   - 返回文件内容和长度信息

6. **search_internet(query)**
   - 根据用户对话的内容搜索互联网
   - 使用DuckDuckGo Instant Answer API，不需要API密钥
   - 不需要复杂的登录流程，直接使用公开API
   - 返回真实的搜索结果，包含标题、URL和摘要
   - 当API调用失败时，返回模拟结果

**TOOLS字典**
- 包含所有工具的元数据
- 每个工具包含函数引用、描述和参数定义
- 用于LLM理解和调用这些工具

### practice02/llm_client_with_tools.py

该文件实现了支持工具调用的LLM客户端，在llm_client_v2.py的基础上添加了工具调用功能：

1. **工具调用系统提示词构建**
   - 自动生成包含所有工具描述的系统提示词
   - 定义工具调用的格式和规则
   - 提供工具调用示例

2. **工具调用解析**
   - 从LLM响应中识别JSON格式的工具调用
   - 提取工具名称和参数
   - 验证工具调用的有效性

3. **工具执行**
   - 根据工具名称调用相应的函数
   - 传递参数并执行工具操作
   - 处理工具执行结果和错误

4. **交互式工具调用流程**
   - 用户输入请求
   - LLM分析请求并生成工具调用
   - 执行工具操作
   - 将工具结果反馈给LLM
   - LLM根据工具结果生成最终回复

5. **增强的终端界面**
   - 显示可用的工具列表
   - 显示工具调用过程和结果
   - 保持流式输出的用户体验

## 使用方法

### 基础版（llm_client.py）

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥
3. 运行 `llm_client.py` 文件：
   ```bash
   python practice01/llm_client.py
   ```

### 终端聊天版（llm_client_v2.py）

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥
3. 运行 `llm_client_v2.py` 文件：
   ```bash
   python practice01/llm_client_v2.py
   ```
4. 在终端中输入你的问题，按 Enter 发送
5. 查看 AI 的实时响应
6. 按 Ctrl+C 退出聊天

### 工具调用版（llm_client_with_tools.py）

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥
3. 运行 `llm_client_with_tools.py` 文件：
   ```bash
   python practice02/llm_client_with_tools.py
   ```
4. 在终端中输入文件操作或互联网搜索请求，例如：
   - "列出当前目录的文件"
   - "创建一个名为test.txt的文件，内容为Hello World"
   - "读取test.txt文件的内容"
   - "将test.txt重命名为hello.txt"
   - "删除hello.txt文件"
   - "搜索Python的最新版本"
   - "搜索如何使用Git"
   - "搜索今天的新闻"
5. 查看 AI 的实时响应和工具执行结果
6. 按 Ctrl+C 退出聊天

### 文档仓库查询版（chat_client.py）

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥和 AnythingLLM 配置：
   ```
   ANYTHINGLLM_API_KEY="your_anythingllm_api_key"
   ANYTHINGLLM_WORKSPACE_SLUG="your_workspace_slug"
   ```
3. 运行 `chat_client.py` 文件：
   ```bash
   python practice05/chat_client.py
   ```
4. 在终端中输入文档查询请求，例如：
   - "在文档仓库中查找关于机器学习的内容"
   - "仓库中有关于Python的教程吗？"
   - "文件仓库中关于数据结构的资料"
5. 查看 AI 的实时响应和工具执行结果
6. 按 Ctrl+C 退出聊天

### 技能调用与通知撰写版（practice06）

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥和 AnythingLLM 配置（如需查询文档仓库）
3. 运行 `chat_client.py` 文件：
   ```bash
   python practice06/chat_client.py
   ```
4. 在终端中输入请求，例如：
   - "在文档仓库中查找关于机器学习的内容" - 自动查询AnythingLLM
   - "我是销售部的，帮我写一个关于五一放假的通知" - 自动加载Notice技能并生成通知
   - "有哪些可用技能？" - 显示所有可用技能列表
5. 查看 AI 的实时响应和工具执行结果
6. 按 Ctrl+C 退出聊天

### 链式工具调用版（practice07）

该版本实现了链式工具调用功能，LLM可以根据中间结果自主决定下一步工具调用顺序。

**主要功能：**
- **ChainedCallContext 上下文管理器**：管理链式调用状态、步骤记录和中间变量存储
- **execute_chained_tool_call 执行函数**：实现链式工具调用的完整流程，支持最多10次迭代
- **build_analysis_prompt 提示词构建**：构建包含用户请求、已执行步骤历史和决策规则的提示词
- **工具扩展**：新增文件搜索、文件读取、网页获取和内容写入工具

**支持的工具：**
- `search_files_with_keyword`: 在指定目录搜索包含关键词的文件
- `read_file_content`: 读取指定文件的内容
- `fetch_webpage`: 获取指定网页的内容
- `write_file_content`: 将内容写入指定文件
- `list_available_skills`: 列出所有可用技能
- `load_skill_content`: 加载指定技能的内容

**使用方法：**

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥
3. 运行 `chat_client.py` 文件：
   ```bash
   python practice07/chat_client.py
   ```
4. 在终端中输入请求，例如：
   - "查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容" - 文件搜索链式调用
   - "我想了解 notice 技能的详细规则" - 技能查询链式调用
   - "访问 `https://www.example.com` 并总结页面内容，保存到 practice07/summary.txt" - 网页处理链式调用
5. 输入 `test` 可运行内置测试用例
6. 查看 AI 的实时响应和工具执行结果
7. 按 Ctrl+C 退出聊天

**链式调用流程：**
1. 初始化消息历史和上下文
2. 循环最多10次迭代：
   - 构建分析提示词（包含用户请求和已执行步骤）
   - 调用LLM决定下一步操作
   - 解析LLM响应（支持JSON格式和tool_calls格式）
   - 如果任务完成，返回最终回答
   - 如果需要继续调用，执行工具并记录到上下文
   - 将结果添加到消息历史，继续下一轮

**输出格式要求：**
- 完成任务：`{"done": true, "answer": "最终回答内容"}`
- 继续调用工具：`{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}`

### 高级链式工具调用版（practice08）

该版本实现了高级链式工具调用功能，支持变量引用和多步骤链式调用。

**主要功能：**
- **ChainedCallContext 上下文管理器**：支持变量引用解析（`$变量名`语法）
- **链式调用格式**：支持单工具调用和多工具链式调用
- **变量传递**：前一个工具的输出可以作为后一个工具的输入参数

**支持的工具：**
- `read_file`: 读取指定路径的文件内容
- `extract_info`: 从文本中提取符合指定模式的信息
- `format_data`: 格式化数据为指定格式（json、text、table）
- `list_available_skills`: 列出所有可用技能
- `load_skill_content`: 加载指定技能的内容

**使用方法：**

1. 复制 `env.example` 文件为 `.env`
2. 在 `.env` 文件中填写你的 API 密钥
3. 运行 `chat_client.py` 文件：
   ```bash
   python practice08/chat_client.py
   ```
4. 在终端中输入请求，例如：
   - "读取test01.txt文件，提取其中的姓名和部门信息" - 链式调用示例
   - "读取test02.txt文件，提取其中的表格数据并格式化为JSON" - 多步骤链式调用
   - "我是销售部的，帮我写一个关于五一放假的通知" - 技能调用

**链式调用格式示例：**

```json
{"tool_calls": [
  {"tool_name": "read_file", "parameters": {"file_path": "practice08/test01.txt"}},
  {"tool_name": "extract_info", "parameters": {"text": "$read_file_result", "pattern": "姓名"}}
]}
```

**技术特点：**
- **变量引用解析**：支持使用 `$变量名` 语法引用前一个工具的输出
- **最大迭代次数限制**：默认10次，防止无限循环
- **错误中断**：某个工具执行失败时，会中断链式调用并返回错误

## 依赖项

- Python 3.x
- 标准库：os, json, time, urllib, sys

## 注意事项

- 确保在 `.env` 文件中正确设置 API_KEY
- 对于 `llm_client_v2.py` 和 `llm_client_with_tools.py`，建议使用支持流式输出的 API 端点，默认使用 `https://api.openai.com/v1/chat/completions`
- 根据使用的 LLM 服务，可能需要调整 `BASE_URL` 和 `MODEL` 参数
- 该代码默认使用 OpenAI API 格式，如需使用其他 LLM 服务，可能需要修改请求格式
- 长时间运行可能会累积大量聊天历史，注意 token 使用量
- 工具调用功能需要 LLM 能够理解并生成正确的工具调用格式
- 文件操作工具会对实际文件系统进行操作，请谨慎使用
