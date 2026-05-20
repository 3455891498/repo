# LLM Agent 项目函数索引

## 快速导航

| 模块 | 文件 | 函数数量 |
|------|------|----------|
| practice01 | [llm_client.py](practice01/llm_client.py) | 3 |
| practice01 | [llm_client_v2.py](practice01/llm_client_v2.py) | 4 |
| practice02 | [tools.py](practice02/tools.py) | 7 |
| practice02 | [llm_client_with_tools.py](practice02/llm_client_with_tools.py) | 6 |
| practice03 | [tools.py](practice03/tools.py) | 4 |
| practice03 | [llm_client_with_summary.py](practice03/llm_client_with_summary.py) | 5 |
| practice04 | [tools.py](practice04/tools.py) | 5 |
| practice04 | [llm_client_with_keyinfo.py](practice04/llm_client_with_keyinfo.py) | 5 |
| practice05 | [tools.py](practice05/tools.py) | 4 |
| practice05 | [chat_client.py](practice05/chat_client.py) | 6 |
| practice06 | [tools.py](practice06/tools.py) | 6 |
| practice06 | [chat_client.py](practice06/chat_client.py) | 6 |
| practice07 | [tools.py](practice07/tools.py) | 4 |
| practice07 | [chat_client.py](practice07/chat_client.py) | 6 |
| practice08 | [tools.py](practice08/tools.py) | 11 |
| practice08 | [chat_client.py](practice08/chat_client.py) | 9 |

---

## practice01 - 基础 LLM 客户端

### llm_client.py
- [load_env()](practice01/llm_client.py:11) - 加载环境变量配置
- [call_llm()](practice01/llm_client.py:31) - 调用LLM API
- [main()](practice01/llm_client.py:85) - 主函数

### llm_client_v2.py
- [load_env()](practice01/llm_client_v2.py:11) - 加载环境变量配置
- [call_llm_stream()](practice01/llm_client_v2.py:31) - 流式调用LLM API
- [main()](practice01/llm_client_v2.py:100) - 主函数（终端聊天）

---

## practice02 - 工具调用功能

### tools.py
- [list_files()](practice02/tools.py:11) - 列出目录文件
- [rename_file()](practice02/tools.py:35) - 重命名文件
- [delete_file()](practice02/tools.py:59) - 删除文件
- [create_file()](practice02/tools.py:83) - 创建文件
- [read_file()](practice02/tools.py:107) - 读取文件内容
- [search_internet()](practice02/tools.py:131) - 搜索互联网
- [TOOLS](practice02/tools.py:160) - 工具函数映射字典

### llm_client_with_tools.py
- [load_env()](practice02/llm_client_with_tools.py:18) - 加载环境变量配置
- [build_tools_system_prompt()](practice02/llm_client_with_tools.py:44) - 构建工具调用系统提示词
- [call_llm_stream()](practice02/llm_client_with_tools.py:91) - 流式调用LLM API
- [parse_tool_call()](practice02/llm_client_with_tools.py:167) - 解析工具调用
- [execute_tool_call()](practice02/llm_client_with_tools.py:187) - 执行工具调用
- [main()](practice02/llm_client_with_tools.py:210) - 主函数

---

## practice03 - 聊天记录总结

### tools.py
- [parse_chat_history()](practice03/tools.py:11) - 解析聊天记录
- [summarize_chat()](practice03/tools.py:35) - 总结聊天记录
- [extract_key_points()](practice03/tools.py:65) - 提取关键点
- [TOOLS](practice03/tools.py:95) - 工具函数映射字典

### llm_client_with_summary.py
- [load_env()](practice03/llm_client_with_summary.py:18) - 加载环境变量配置
- [build_summary_prompt()](practice03/llm_client_with_summary.py:44) - 构建总结提示词
- [call_llm_stream()](practice03/llm_client_with_summary.py:68) - 流式调用LLM API
- [main()](practice03/llm_client_with_summary.py:140) - 主函数

---

## practice04 - 关键信息提取

### tools.py
- [parse_chat_history()](practice04/tools.py:11) - 解析聊天记录
- [extract_key_info()](practice04/tools.py:35) - 提取关键信息
- [analyze_sentiment()](practice04/tools.py:65) - 情感分析
- [TOOLS](practice04/tools.py:95) - 工具函数映射字典

### llm_client_with_keyinfo.py
- [load_env()](practice04/llm_client_with_keyinfo.py:18) - 加载环境变量配置
- [build_keyinfo_prompt()](practice04/llm_client_with_keyinfo.py:44) - 构建关键信息提取提示词
- [call_llm_stream()](practice04/llm_client_with_keyinfo.py:68) - 流式调用LLM API
- [main()](practice04/llm_client_with_keyinfo.py:140) - 主函数

---

## practice05 - 文档仓库查询

### tools.py
- [anythingllm_query()](practice05/tools.py:11) - 查询AnythingLLM文档仓库
- [TOOLS](practice05/tools.py:85) - 工具函数映射字典

### chat_client.py
- [load_env()](practice05/chat_client.py:18) - 加载环境变量配置
- [build_tools_system_prompt()](practice05/chat_client.py:44) - 构建工具调用系统提示词
- [call_llm_stream()](practice05/chat_client.py:85) - 流式调用LLM API
- [parse_tool_call()](practice05/chat_client.py:160) - 解析工具调用
- [execute_tool_call()](practice05/chat_client.py:180) - 执行工具调用
- [main()](practice05/chat_client.py:200) - 主函数

---

## practice06 - 技能调用与通知撰写

### tools.py
- [parse_skill_md()](practice06/tools.py:11) - 解析SKILL.md文件
- [get_skills_list()](practice06/tools.py:55) - 获取技能列表
- [list_available_skills()](practice06/tools.py:85) - 列出可用技能
- [load_skill_content()](practice06/tools.py:110) - 加载技能内容
- [anythingllm_query()](practice06/tools.py:190) - 查询AnythingLLM
- [TOOLS](practice06/tools.py:260) - 工具函数映射字典

### chat_client.py
- [load_env()](practice06/chat_client.py:18) - 加载环境变量配置
- [build_tools_system_prompt()](practice06/chat_client.py:44) - 构建工具调用系统提示词
- [call_llm_stream()](practice06/chat_client.py:90) - 流式调用LLM API
- [parse_tool_call()](practice06/chat_client.py:170) - 解析工具调用
- [execute_tool_call()](practice06/chat_client.py:190) - 执行工具调用
- [main()](practice06/chat_client.py:210) - 主函数

---

## practice07 - 纯技能调用

### tools.py
- [parse_skill_md()](practice07/tools.py:11) - 解析SKILL.md文件
- [get_skills_list()](practice07/tools.py:55) - 获取技能列表
- [list_available_skills()](practice07/tools.py:85) - 列出可用技能
- [load_skill_content()](practice07/tools.py:110) - 加载技能内容
- [TOOLS](practice07/tools.py:190) - 工具函数映射字典

### chat_client.py
- [load_env()](practice07/chat_client.py:18) - 加载环境变量配置
- [build_tools_system_prompt()](practice07/chat_client.py:44) - 构建工具调用系统提示词
- [call_llm_stream()](practice07/chat_client.py:75) - 流式调用LLM API
- [parse_tool_call()](practice07/chat_client.py:150) - 解析工具调用
- [execute_tool_call()](practice07/chat_client.py:170) - 执行工具调用
- [main()](practice07/chat_client.py:190) - 主函数

---

## practice08 - 链式工具调用（重点）

### tools.py
- **ChainedCallContext 类** - 链式调用上下文管理器
  - [__init__()](practice08/tools.py:25) - 初始化上下文
  - [add_call()](practice08/tools.py:43) - 记录工具调用
  - [get_variable()](practice08/tools.py:75) - 获取变量值
  - [set_variable()](practice08/tools.py:97) - 设置变量值
  - [get_last_result()](practice08/tools.py:116) - 获取最后结果
  - [get_call_chain()](practice08/tools.py:137) - 获取调用链描述
  - [should_continue()](practice08/tools.py:159) - 检查是否继续迭代
  - [increment_iteration()](practice08/tools.py:188) - 增加迭代计数
  - [set_complete()](practice08/tools.py:204) - 设置完成标记
  - [get_summary()](practice08/tools.py:225) - 获取摘要信息
- [parse_skill_md()](practice08/tools.py:253) - 解析SKILL.md文件
- [get_skills_list()](practice08/tools.py:319) - 获取技能列表
- [list_available_skills()](practice08/tools.py:367) - 列出可用技能
- [load_skill_content()](practice08/tools.py:401) - 加载技能内容
- [read_file()](practice08/tools.py:502) - 读取文件内容
- [extract_info()](practice08/tools.py:552) - 提取文本信息
- [format_data()](practice08/tools.py:605) - 格式化数据
- [TOOLS](practice08/tools.py:655) - 工具函数映射字典

### chat_client.py
- [load_env()](practice08/chat_client.py:18) - 加载环境变量配置
- [build_tools_system_prompt()](practice08/chat_client.py:62) - 构建工具调用系统提示词
- [call_llm_stream()](practice08/chat_client.py:151) - 流式调用LLM API
- [parse_tool_calls()](practice08/chat_client.py:283) - 解析工具调用（支持链式）
- [resolve_parameters()](practice08/chat_client.py:325) - 解析变量引用
- [execute_tool_call()](practice08/chat_client.py:361) - 执行单个工具调用
- [execute_chained_calls()](practice08/chat_client.py:410) - 执行链式工具调用
- [execute_tool_call_with_context()](practice08/chat_client.py:443) - 带上下文的工具调用（兼容性别名）
- [main()](practice08/chat_client.py:447) - 主函数

---

## 函数调用关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          main() 入口                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   load_env()    │     │call_llm_stream()│     │execute_tool_call│
│  加载环境变量   │     │   调用LLM API   │     │    执行工具调用   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                   │                      │
                                   ▼                      ▼
                         ┌─────────────────┐    ┌─────────────────┐
                         │build_tools_prompt│    │parse_tool_calls │
                         │  构建系统提示词   │    │   解析工具调用   │
                         └─────────────────┘    └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │execute_chained_ │
                                               │   calls()       │
                                               │  链式工具调用    │
                                               └────────┬────────┘
                                                        │
                     ┌───────────────────────────────────┼───────────────────────────────────┐
                     ▼                                   ▼                                   ▼
           ┌─────────────────┐                 ┌─────────────────┐                 ┌─────────────────┐
           │   read_file()   │                 │  extract_info() │                 │  format_data()  │
           │    读取文件     │                 │    提取信息      │                 │    格式化数据    │
           └─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

---

## 工具函数分类

### 文件操作工具
| 函数 | 文件 | 功能 |
|------|------|------|
| [list_files()](practice02/tools.py:11) | practice02/tools.py | 列出目录文件 |
| [rename_file()](practice02/tools.py:35) | practice02/tools.py | 重命名文件 |
| [delete_file()](practice02/tools.py:59) | practice02/tools.py | 删除文件 |
| [create_file()](practice02/tools.py:83) | practice02/tools.py | 创建文件 |
| [read_file()](practice08/tools.py:502) | practice08/tools.py | 读取文件内容 |

### 技能管理工具
| 函数 | 文件 | 功能 |
|------|------|------|
| [parse_skill_md()](practice08/tools.py:253) | practice08/tools.py | 解析SKILL.md |
| [get_skills_list()](practice08/tools.py:319) | practice08/tools.py | 获取技能列表 |
| [list_available_skills()](practice08/tools.py:367) | practice08/tools.py | 列出可用技能 |
| [load_skill_content()](practice08/tools.py:401) | practice08/tools.py | 加载技能内容 |

### 链式调用工具
| 函数 | 文件 | 功能 |
|------|------|------|
| [resolve_parameters()](practice08/chat_client.py:325) | practice08/chat_client.py | 解析变量引用 |
| [execute_chained_calls()](practice08/chat_client.py:410) | practice08/chat_client.py | 链式工具调用 |

### 数据处理工具
| 函数 | 文件 | 功能 |
|------|------|------|
| [extract_info()](practice08/tools.py:552) | practice08/tools.py | 提取文本信息 |
| [format_data()](practice08/tools.py:605) | practice08/tools.py | 格式化数据 |

---

## 快捷键导航

在支持Markdown链接的编辑器中，您可以：

1. **点击链接** - 直接跳转到对应的函数定义位置
2. **Ctrl+点击** - 在新窗口中打开链接
3. **搜索函数名** - 使用编辑器的搜索功能快速定位

---

> **提示**: 在VS Code等现代编辑器中，点击这些链接会直接跳转到对应的代码位置，方便您快速查看和编辑代码。