# 链式工具调用（Chained Tool Calls）

## 概述

本目录实现了链式工具调用功能，让LLM能够根据中间结果自主决定下一步工具调用顺序，实现复杂任务的自动化处理。

## 核心功能

### 1. ChainedCallContext 上下文管理器

用于在多个工具调用之间传递数据和状态：
- 记录每一步的调用和结果
- 存储中间变量供后续步骤使用
- 设置最大迭代次数（默认10次），防止无限循环

### 2. execute_chained_tool_call 执行函数

实现链式工具调用的完整流程：
- 初始化消息历史，包含system prompt
- 循环最多max_iterations次：
  - 构建分析提示词（包含用户请求和已执行步骤历史）
  - 调用LLM决定下一步操作
  - 解析LLM响应（支持JSON格式和tool_calls格式）
  - 如果任务完成，返回最终回答
  - 如果需继续调用，执行工具并记录到上下文
  - 将结果添加到消息历史，继续下一轮

### 3. build_analysis_prompt 提示词构建函数

构建结构化提示词，包含：
- 用户原始请求
- 已执行的工具调用历史（工具名、参数、结果）
- 决策规则说明
- JSON输出格式要求

## 支持的工具

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `search_files_with_keyword` | 在指定目录搜索包含关键词的文件 | `directory`, `keyword` |
| `read_file_content` | 读取指定文件的内容 | `file_path` |
| `fetch_webpage` | 获取指定网页的内容 | `url` |
| `write_file_content` | 将内容写入指定文件 | `file_path`, `content` |
| `list_available_skills` | 列出所有可用技能 | 无 |
| `load_skill_content` | 加载指定技能的内容 | `skill_name` |

## 输出格式要求

LLM需要按照以下JSON格式返回决策：

### 完成任务时：
```json
{"done": true, "answer": "最终回答内容"}
```

### 继续调用工具时：
```json
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}
```

## 链式调用规则

1. 工具调用有顺序依赖关系，某些工具需要其他工具的结果作为参数
2. LLM需要根据中间结果自主决定下一步调用哪个工具
3. 可以使用上下文变量（如 `matched_files`, `current_file`, `last_result` 等）
4. 如果需要总结内容，应该先获取原始内容，再进行总结

## 使用示例

### 测试1：文件搜索链式调用
```
用户请求：请查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容

步骤：
1. search_files_with_keyword → 获取包含关键词的文件列表
2. read_file_content → 读取文件内容
3. 直接总结所有文件内容
```

### 测试2：技能查询链式调用
```
用户请求：我想了解 notice 技能的详细规则

步骤：
1. load_skill_content → 加载技能详细内容
2. 直接总结技能规则
```

### 测试3：网页处理链式调用
```
用户请求：访问网页并总结页面内容，保存到 practice07/summary.txt

步骤：
1. fetch_webpage → 获取网页内容
2. write_file_content → 将内容保存到文件
```

## 使用方法

```bash
# 运行主程序
python chat_client.py

# 输入请求示例
请查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容

# 运行测试
输入 test 可运行内置测试用例
```

## 错误处理

- JSON解析失败处理：支持从markdown代码块中提取JSON
- 工具调用格式兼容：同时支持JSON格式和OpenAI标准tool_calls格式
- LLM响应为None处理：设置默认响应
- 工具执行异常处理：捕获并记录错误信息
- 防止无限循环：设置max_iterations限制（默认10次）
