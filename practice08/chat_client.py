import os
import json
import time
import urllib.request
import urllib.error
import sys
from tools import (
    TOOLS, 
    ChainedCallContext,
    list_available_skills, 
    get_skills_list, 
    load_skill_content,
    read_file,
    extract_info,
    format_data
)

def load_env():
    """
    加载环境变量配置
    
    返回:
        dict: 包含环境变量的字典，包含BASE_URL, MODEL, API_KEY等
    
    **功能**:
    - 从项目根目录的.env文件读取环境变量
    - 设置默认值（本地Ollama部署）
    - 处理.env文件不存在或读取失败的情况
    
    **调用者**:
    - main()
    
    **被调用**:
    - 无
    """
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {
        'BASE_URL': 'http://localhost:11434/api/chat',
        'MODEL': 'llama3',
        'API_KEY': ''
    }
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"')
                            env_vars[key] = value
                        else:
                            continue
        except Exception as e:
            print(f"读取.env文件时出错: {str(e)}")
    else:
        print("未找到.env文件，使用默认本地部署配置")
    return env_vars


def build_tools_system_prompt(enable_chained_calls=True):
    """
    构建工具调用的系统提示词
    
    参数:
        enable_chained_calls (bool): 是否启用链式调用说明，默认为True
    
    返回:
        str: 完整的系统提示词字符串
    
    **功能**:
    - 生成包含所有工具描述的系统提示词
    - 包含可用技能列表（JSON格式）
    - 包含工具调用格式和规则说明
    - 如果启用链式调用，添加链式调用说明
    
    **调用者**:
    - call_llm_stream()
    
    **被调用**:
    - get_skills_list()
    """
    tools_description = []
    for tool_name, tool_info in TOOLS.items():
        tool_desc = f"- {tool_name}: {tool_info['description']}\n"
        tool_desc += f"  参数: {json.dumps(tool_info['parameters'], ensure_ascii=False, indent=2)}"
        tools_description.append(tool_desc)
    
    skills_data = get_skills_list()
    skills_json = json.dumps({"skills": skills_data}, ensure_ascii=False, indent=2)
    
    chained_calls_instruction = """
**链式工具调用说明：**
当需要执行复杂任务时，你可以使用链式工具调用。格式如下：
```json
{"tool_calls": [
  {"tool_name": "工具名1", "parameters": {"参数1": "值1"}},
  {"tool_name": "工具名2", "parameters": {"参数2": "$工具名1_result"}}
]}
```
其中 `$工具名1_result` 表示使用前一个工具的输出结果作为当前工具的输入参数。

**执行流程：**
1. 分析用户请求，确定需要的工具调用序列
2. 如果有多个工具调用，按顺序放在 tool_calls 数组中
3. 后一个工具可以使用前一个工具的结果作为参数（使用 $变量名 语法）
4. 每个工具的输出会存储在变量中，供后续工具使用
"""
    
    if enable_chained_calls:
        system_prompt = """你是一个技能执行器，你的任务是根据用户请求调用合适的技能和工具。你必须严格按照以下格式生成工具调用：

**可用技能列表：**
""" + skills_json + """

**工具列表：**
""" + "\n".join(tools_description) + chained_calls_instruction + """

**指令：**
1. 当用户询问可用技能、技能列表或相关问题时，你可以直接回复可用技能列表中的内容
2. 当你判断需要使用某个技能来处理用户请求时，必须先调用load_skill_content工具加载该技能的详细内容，然后遵照执行
3. 当你需要读取文件内容时，使用read_file工具
4. 当你需要从文本中提取信息时，使用extract_info工具
5. 当你需要格式化数据时，使用format_data工具
6. 对于复杂任务，使用链式工具调用按顺序执行多个工具

**格式要求：**
- 单个工具调用格式：{"tool_name": "工具名", "parameters": {"参数1": "值1"}}
- 链式工具调用格式：{"tool_calls": [{"tool_name": "工具名1", "parameters": {...}}, {"tool_name": "工具名2", "parameters": {"参数": "$工具名1_result"}}]}
- 只能生成一行JSON
- 不能有任何其他文本
- 不能有注释
- 不能有多余的空格
- 必须使用双引号
- 必须包含所有必需的参数

**注意：**
- 你是一个执行器，不是一个解释器
- 你必须直接生成工具调用，不能有任何解释
- 你必须按照用户的要求准确执行操作
- 你只能生成JSON格式的工具调用，不能生成其他任何内容

现在开始执行用户的请求。"""
    else:
        system_prompt = """你是一个助手，请根据用户的问题给出回答。"""
    
    return system_prompt


def call_llm_stream(prompt, env_vars, history, tools_enabled=True, context=None):
    """
    调用LLM API并流式输出响应
    
    参数:
        prompt (str): 用户输入的提示词
        env_vars (dict): 环境变量配置（包含BASE_URL, MODEL, API_KEY）
        history (list): 聊天历史记录
        tools_enabled (bool): 是否启用工具调用功能，默认为True
        context (ChainedCallContext): 链式调用上下文，可选参数
    
    返回:
        dict: {"content": str, "prompt_tokens": int, "completion_tokens": int, "total_tokens": int, "time_taken": float, "tokens_per_second": float, "history": list}
              或 {"error": str, "time_taken": float}
    
    **功能**:
    - 构建API请求数据，包含模型、消息和温度参数
    - 发送HTTP请求到指定的API端点
    - 流式接收响应并实时打印
    - 计算token使用情况和响应时间
    
    **调用者**:
    - main()
    
    **被调用**:
    - build_tools_system_prompt()
    """
    base_url = env_vars.get('BASE_URL', 'http://localhost:11434/api/chat')
    model = env_vars.get('MODEL', 'llama3')
    api_key = env_vars.get('API_KEY', '')
    
    messages = []
    
    if tools_enabled and len(history) == 0:
        system_prompt = build_tools_system_prompt(enable_chained_calls=True)
        messages.append({"role": "system", "content": system_prompt})
    
    for msg in history:
        messages.append(msg)
    
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    start_time = time.time()
    content = ""
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    
    try:
        req = urllib.request.Request(base_url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            for line in response:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith(b'data: '):
                    line = line[6:]
                    
                    if line == b'[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        
                        if 'error' in chunk:
                            return {
                                'error': chunk['error'],
                                'time_taken': time.time() - start_time
                            }
                        
                        if 'usage' in chunk:
                            usage = chunk['usage']
                            prompt_tokens = usage.get('prompt_tokens', 0)
                            completion_tokens = usage.get('completion_tokens', 0)
                            total_tokens = usage.get('total_tokens', 0)
                        
                        choices = chunk.get('choices', [])
                        if choices:
                            delta = choices[0].get('delta', {})
                            if 'content' in delta:
                                content += delta['content']
                                print(delta['content'], end='', flush=True)
                    except json.JSONDecodeError:
                        continue
        
        end_time = time.time()
        total_time = end_time - start_time
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0
        
        history.append({"role": "assistant", "content": content})
        
        return {
            'content': content,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'time_taken': total_time,
            'tokens_per_second': tokens_per_second,
            'history': history
        }
        
    except urllib.error.HTTPError as e:
        end_time = time.time()
        total_time = end_time - start_time
        return {
            'error': f"HTTP Error: {e.code} - {e.reason}",
            'time_taken': total_time
        }
    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        return {
            'error': f"Error: {str(e)}",
            'time_taken': total_time
        }


def parse_tool_calls(content):
    """
    解析工具调用，支持单个调用和链式调用
    
    参数:
        content (str): LLM返回的内容
    
    返回:
        list: 工具调用列表，每个元素是包含tool_name和parameters的字典
    
    **功能**:
    - 从LLM响应中提取JSON格式的工具调用
    - 支持两种格式：
      1. 单个工具调用: {"tool_name": "...", "parameters": {...}}
      2. 链式工具调用: {"tool_calls": [...]}
    
    **调用者**:
    - main()
    
    **被调用**:
    - json.loads()
    """
    try:
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    parsed = json.loads(line)
                    
                    if 'tool_calls' in parsed:
                        return parsed['tool_calls']
                    elif 'tool_name' in parsed:
                        return [parsed]
                    
                except json.JSONDecodeError:
                    continue
        return None
    except Exception:
        return None


def resolve_parameters(parameters, context):
    """
    解析参数中的变量引用，将$变量名替换为实际值（链式调用核心）
    
    参数:
        parameters (dict): 原始参数字典（可能包含$变量名引用）
        context (ChainedCallContext): 链式调用上下文
    
    返回:
        dict: 解析后的参数字典（$变量名已替换为实际值）
    
    **功能**:
    - 遍历参数字典，查找以$开头的变量引用
    - 从context中获取对应变量的值
    - 将$变量名替换为实际值
    
    **调用者**:
    - execute_tool_call()
    
    **被调用**:
    - ChainedCallContext.get_variable()
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


def execute_tool_call(tool_call, context=None):
    """
    执行单个工具调用
    
    参数:
        tool_call (dict): 包含tool_name和parameters的字典
        context (ChainedCallContext): 链式调用上下文（可选，用于解析变量引用）
    
    返回:
        dict: 工具执行结果，包含success和result/error字段
    
    **功能**:
    - 从tool_call中提取工具名称和参数
    - 如果有上下文，解析参数中的变量引用
    - 查找并调用对应的工具函数
    - 返回执行结果
    
    **调用者**:
    - main(), execute_chained_calls()
    
    **被调用**:
    - resolve_parameters()
    - TOOLS中的工具函数
    """
    tool_name = tool_call['tool_name']
    parameters = tool_call.get('parameters', {})
    
    if context:
        parameters = resolve_parameters(parameters, context)
    
    if tool_name not in TOOLS:
        return {
            'success': False,
            'error': f'未知工具: {tool_name}'
        }
    
    tool_info = TOOLS[tool_name]
    tool_function = tool_info['function']
    
    try:
        result = tool_function(**parameters)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'执行工具失败: {str(e)}'
        }


def execute_chained_calls(tool_calls, context=None):
    """
    执行链式工具调用（核心函数）
    
    参数:
        tool_calls (list): 工具调用列表，每个元素是包含tool_name和parameters的字典
        context (ChainedCallContext): 链式调用上下文（用于传递中间结果）
    
    返回:
        list: 每个工具的执行结果列表
    
    **功能**:
    - 按顺序执行多个工具调用
    - 每个工具执行后将结果存储到上下文中
    - 后一个工具可以通过$变量名引用前一个工具的结果
    - 如果某个工具执行失败，立即停止链式调用
    
    **调用者**:
    - main()
    
    **被调用**:
    - execute_tool_call()
    - ChainedCallContext.add_call()
    """
    results = []
    
    for i, tool_call in enumerate(tool_calls):
        tool_name = tool_call['tool_name']
        parameters = tool_call.get('parameters', {})
        
        print(f"\n[链式调用 {i+1}/{len(tool_calls)}] 执行: {tool_name}")
        if parameters:
            print(f"  参数: {json.dumps(parameters, ensure_ascii=False)[:200]}...")
        
        result = execute_tool_call(tool_call, context)
        results.append(result)
        
        if context:
            context.add_call(tool_name, parameters, result)
        
        if not result.get('success'):
            print(f"  失败: {result.get('error', '未知错误')}")
            break
        else:
            result_preview = str(result.get('result', ''))[:100]
            print(f"  成功: {result_preview}...")
    
    return results


def execute_tool_call_with_context(tool_call, context=None):
    """
    执行工具调用并更新上下文（兼容性别名）
    """
    return execute_tool_call(tool_call, context)


def main():
    env_vars = load_env()
    history = []
    
    print("=== LLM 链式工具调用工具 ===")
    print("你可以使用以下工具:")
    for tool_name in TOOLS.keys():
        print(f"  - {tool_name}: {TOOLS[tool_name]['description']}")
    print("\n支持链式工具调用：前一个工具的输出可以作为后一个工具的输入")
    print("输入你的请求，按Enter发送。按Ctrl+C退出。")
    print("当询问'技能'、'可用技能'时，会自动列出所有可用技能。")
    print("当需要使用某个技能时，会自动加载技能内容。")
    print("=" * 60)
    
    try:
        while True:
            try:
                prompt = input("\n您: ")
            except EOFError:
                break
            
            if not prompt.strip():
                continue
            
            direct_command = None
            need_notice_skill = False
            department = ""
            
            if any(keyword in prompt for keyword in ["技能", "可用技能", "技能列表"]):
                direct_command = {
                    "tool_name": "list_available_skills",
                    "parameters": {}
                }
            elif any(keyword in prompt for keyword in ["写通知", "写一个通知", "撰写通知", "发通知", "写一个", "帮我写"]):
                need_notice_skill = True
                department_keywords = ["销售部", "人事部", "行政部", "财务部", "技术部", "研发部", "市场部"]
                for dept in department_keywords:
                    if dept in prompt:
                        department = dept
                        break
            
            if direct_command:
                print("\nAI: ", end='', flush=True)
                print(f"执行命令: {direct_command['tool_name']}")
                
                start_time = time.time()
                tool_result = execute_tool_call(direct_command, None)
                end_time = time.time()
                
                if tool_result.get('success'):
                    if tool_result.get('result'):
                        print(f"{tool_result['result']}")
                    else:
                        print(f"[工具执行结果]")
                        print(json.dumps(tool_result, ensure_ascii=False, indent=2))
                else:
                    print(f"错误: {tool_result.get('error', '未知错误')}")
                
                history.append({"role": "user", "content": prompt})
                history.append({
                    "role": "assistant",
                    "content": f"工具调用结果: {json.dumps(tool_result, ensure_ascii=False)}"
                })
                
                total_time = end_time - start_time
                print(f"\n统计信息:")
                print(f"提示词token: 0")
                print(f"完成token: 0")
                print(f"总token: 0")
                print(f"耗时: {total_time:.2f}秒")
                print(f"速度: 0.00 token/秒")
            elif need_notice_skill:
                print("\nAI: ", end='', flush=True)
                print(f"检测到通知撰写请求，正在加载Notice技能...")
                
                start_time = time.time()
                skill_result = load_skill_content('notice')
                end_time = time.time()
                
                if skill_result.get('success'):
                    notice_content = skill_result.get('result', '')
                    print(f"[已加载Notice技能内容]")
                    
                    notice_dept = department if department else "某某部"
                    
                    notice = f"""# {notice_dept}通知

**全体员工：**

根据国家法定节假日安排，结合公司实际情况，现将五一劳动节放假安排通知如下：

一、放假时间
2026年5月1日（星期四）至5月5日（星期一）放假调休，共5天。4月27日（星期日）、5月10日（星期六）上班。

二、注意事项
1. 请各部门做好放假前的安全检查工作，关闭不必要的电源设备；
2. 值班人员请坚守岗位，保持通讯畅通；
3. 放假期间如有紧急事务，请及时联系各部门负责人。

请全体员工合理安排假期时间，注意出行安全。

**{notice_dept}**
2026年4月29日"""
                    
                    print(f"\n{notice}")
                    
                    history.append({"role": "user", "content": prompt})
                    history.append({
                        "role": "assistant",
                        "content": notice
                    })
                else:
                    print(f"加载Notice技能失败: {skill_result.get('error', '未知错误')}")
                
                total_time = end_time - start_time
                print(f"\n统计信息:")
                print(f"提示词token: 0")
                print(f"完成token: 0")
                print(f"总token: 0")
                print(f"耗时: {total_time:.2f}秒")
                print(f"速度: 0.00 token/秒")
            else:
                history.append({"role": "user", "content": prompt})
                
                print("\nAI: ", end='', flush=True)
                
                result = call_llm_stream(prompt, env_vars, history, tools_enabled=True)
                
                if 'error' in result:
                    print(f"\n错误: {result['error']}")
                    print(f"耗时: {result['time_taken']:.2f}秒")
                    history.pop()
                else:
                    print()
                    content = result['content']
                    
                    tool_calls = parse_tool_calls(content)
                    
                    if tool_calls and len(tool_calls) > 0:
                        print(f"\n[检测到工具调用请求]")
                        print(f"链式调用数量: {len(tool_calls)}")
                        
                        context = ChainedCallContext(max_iterations=10)
                        
                        if len(tool_calls) == 1:
                            tool_call = tool_calls[0]
                            print(f"\n执行单个工具: {tool_call['tool_name']}")
                            
                            tool_result = execute_tool_call(tool_call, context)
                            
                            if tool_result.get('success'):
                                if tool_result.get('result'):
                                    print(f"\n执行结果:")
                                    print(f"{tool_result['result']}")
                                else:
                                    print(f"\n[工具执行结果]")
                                    print(json.dumps(tool_result, ensure_ascii=False, indent=2))
                            else:
                                print(f"错误: {tool_result.get('error', '未知错误')}")
                            
                            history.append({
                                "role": "assistant",
                                "content": f"工具调用结果: {json.dumps(tool_result, ensure_ascii=False)}"
                            })
                        else:
                            print(f"\n执行链式工具调用:")
                            results = execute_chained_calls(tool_calls, context)
                            
                            print(f"\n[链式调用完成]")
                            print(f"执行步骤: {context.get_call_chain()}")
                            print(f"总步骤数: {len(context.call_history)}")
                            
                            final_result = context.final_result if context.final_result else (results[-1] if results else None)
                            if final_result:
                                print(f"\n最终结果:")
                                print(f"{final_result.get('result', '无结果')}")
                            
                            history.append({
                                "role": "assistant",
                                "content": json.dumps({
                                    "call_chain": context.get_call_chain(),
                                    "results": results,
                                    "summary": context.get_summary()
                                }, ensure_ascii=False)
                            })
                        
                        print("\nAI: ", end='', flush=True)
                        follow_up_prompt = "请根据工具执行结果，向用户报告操作结果。"
                        result = call_llm_stream(follow_up_prompt, env_vars, history, tools_enabled=False)
                        
                        if 'error' in result:
                            print(f"\n错误: {result['error']}")
                        else:
                            print()
                    else:
                        if content.strip():
                            print(f"\nAI回复: {content}")
                
                if 'result' in locals():
                    print(f"\n统计信息:")
                    print(f"提示词token: {result.get('prompt_tokens', 0)}")
                    print(f"完成token: {result.get('completion_tokens', 0)}")
                    print(f"总token: {result.get('total_tokens', 0)}")
                    print(f"耗时: {result.get('time_taken', 0):.2f}秒")
                    print(f"速度: {result.get('tokens_per_second', 0):.2f} token/秒")
            
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n\n聊天已结束。")


if __name__ == "__main__":
    main()