# LLM 链式工具调用工具

本目录实现了链式工具调用（Chained Tool Calls）功能，允许前一个工具的输出作为后一个工具的输入参数，让LLM能够根据中间结果自主决定下一步工具调用。

## 主要功能

### 1. ChainedCallContext 链式调用上下文管理器

创建了 `ChainedCallContext` 类，用于在多个工具调用之间传递数据和状态：

**核心功能：**
- **记录调用历史**：记录每一步的调用工具、参数和结果
- **存储中间变量**：每个工具的输出结果都存储在变量中，供后续工具使用
- **最大迭代次数**：设置 `max_iterations=10`，防止无限循环
- **变量引用解析**：支持使用 `$变量名` 语法引用前一个工具的输出

**主要方法：**
- `add_call()` - 记录一次工具调用
- `get_variable()` - 获取变量值
- `set_variable()` - 设置变量值
- `get_last_result()` - 获取最后一次工具调用的结果
- `get_call_chain()` - 获取调用链的描述
- `should_continue()` - 检查是否应该继续迭代
- `get_summary()` - 获取链式调用的摘要信息

### 2. 链式工具调用格式

LLM可以生成两种格式的工具调用：

**单个工具调用：**
```json
{"tool_name": "工具名", "parameters": {"参数1": "值1"}}
```

**链式工具调用：**
```json
{"tool_calls": [
  {"tool_name": "read_file", "parameters": {"file_path": "practice08/test01.txt"}},
  {"tool_name": "extract_info", "parameters": {"text": "$read_file_result", "pattern": "姓名"}}
]}
```

其中 `$read_file_result` 表示使用前一个工具（read_file）的输出结果作为当前工具（extract_info）的输入参数。

### 3. 新增工具函数

在原有技能函数的基础上，新增了以下工具函数：

#### read_file
读取指定路径的文件内容。

**参数：**
- `file_path`: 文件路径（绝对路径或相对于项目根目录的路径）

**返回：**
- `success`: 是否成功
- `result`: 文件内容
- `file_name`: 文件名
- `file_size`: 文件大小

#### extract_info
从文本中提取符合指定模式的信息。

**参数：**
- `text`: 要提取信息的文本内容
- `pattern`: 提取模式（预定义：姓名、部门、职位、日期、数字、邮箱、电话）或正则表达式

**返回：**
- `success`: 是否成功
- `result`: 提取结果列表
- `count`: 提取数量

#### format_data
格式化数据为指定格式。

**参数：**
- `data`: 要格式化的数据
- `format_type`: 格式化类型（json、text、table）

**返回：**
- `success`: 是否成功
- `result`: 格式化后的字符串

## 使用方法

### 运行程序

```bash
python practice08/chat_client.py
```

### 功能测试

1. **查看可用技能**
   - 输入：有哪些可用技能？
   - 输出：显示所有可用技能列表

2. **撰写通知**
   - 输入：我是销售部的，帮我写一个关于五一放假的通知
   - 输出：自动加载Notice技能并生成符合规范的通知

3. **链式工具调用 - 读取文件并提取信息**
   - 输入：读取test01.txt文件，提取其中的姓名和部门信息
   - 系统会：
     - 步骤1：调用 read_file 读取 test01.txt
     - 步骤2：调用 extract_info 从文件内容中提取姓名和部门
   - 支持前一个工具的输出作为后一个工具的输入

4. **链式工具调用 - 读取文件、提取信息、格式化**
   - 输入：读取test02.txt文件，提取其中的表格数据并格式化为JSON
   - 系统会：
     - 步骤1：调用 read_file 读取 test02.txt
     - 步骤2：调用 extract_info 提取表格数据
     - 步骤3：调用 format_data 格式化为JSON

### 链式调用示例

当用户请求复杂任务时，LLM会自动生成链式调用。例如：

```
读取practice08/test01.txt文件，提取其中的销售数据并格式化为JSON
```

LLM会生成：
```json
{"tool_calls": [
  {"tool_name": "read_file", "parameters": {"file_path": "practice08/test01.txt"}},
  {"tool_name": "extract_info", "parameters": {"text": "$read_file_result", "pattern": "销售额"}},
  {"tool_name": "format_data", "parameters": {"data": "$extract_info_result", "format_type": "json"}}
]}
```

执行流程：
1. 步骤1：read_file 读取 test01.txt 内容
2. 步骤2：extract_info 从内容中提取销售额数据
3. 步骤3：format_data 将数据格式化为JSON

## 技术实现

### 变量引用解析
```python
def resolve_parameters(parameters, context):
    """
    解析参数中的变量引用，将$变量名替换为实际值
    """
    resolved = {}
    for key, value in parameters.items():
        if isinstance(value, str) and value.startswith('$'):
            var_name = value[1:]
            resolved_value = context.get_variable(var_name)
            if resolved_value is not None:
                resolved[key] = resolved_value
            else:
                resolved[key] = value
        else:
            resolved[key] = value
    return resolved
```

### 链式调用执行
```python
def execute_chained_calls(tool_calls, context=None):
    """
    执行链式工具调用
    """
    results = []
    
    for i, tool_call in enumerate(tool_calls):
        tool_name = tool_call['tool_name']
        parameters = tool_call.get('parameters', {})
        
        print(f"\n[链式调用 {i+1}/{len(tool_calls)}] 执行: {tool_name}")
        
        result = execute_tool_call(tool_call, context)
        results.append(result)
        
        if context:
            context.add_call(tool_name, parameters, result)
        
        if not result.get('success'):
            print(f"  失败: {result.get('error', '未知错误')}")
            break
    
    return results
```

## 安全机制

1. **最大迭代次数限制**：默认 `max_iterations=10`，防止无限循环
2. **错误中断**：某个工具执行失败时，会中断链式调用并返回错误
3. **变量存在性检查**：引用不存在的变量时，会使用空值或默认值

## 文件结构

```
practice08/
├── README.md          # 本说明文件
├── chat_client.py     # 聊天客户端（支持链式调用）
├── tools.py           # 工具函数定义和ChainedCallContext
├── test01.txt         # 测试文件1（用户和销售数据）
└── test02.txt         # 测试文件2（通知模板和表格）
```

## 依赖项

- Python 3.7+
- urllib.request（标准库）
- json（标准库）
- re（标准库）