import os
import json
import time
import urllib.request
import urllib.error
import re
from tools import TOOLS, list_available_skills, get_skills_list, load_skill_content

def load_env():
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

class ChainedCallContext:
    """
    链式调用上下文管理器，用于在多个工具调用之间传递数据和状态
    """
    
    def __init__(self, max_iterations=10):
        self.user_request = ""
        self.steps = []  # 记录每一步的调用和结果
        self.variables = {}  # 存储中间变量供后续步骤使用
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.is_completed = False
        self.final_answer = ""
    
    def add_step(self, tool_name, parameters, result):
        """
        添加一步工具调用记录
        """
        step = {
            'iteration': self.current_iteration,
            'tool_name': tool_name,
            'parameters': parameters,
            'result': result,
            'timestamp': time.time()
        }
        self.steps.append(step)
        
        # 尝试从结果中提取有用的变量
        if isinstance(result, dict):
            if 'files' in result:
                self.variables['matched_files'] = result['files']
            if 'file_path' in result:
                self.variables['current_file'] = result['file_path']
            if 'result' in result:
                self.variables['last_result'] = result['result']
            if 'url' in result:
                self.variables['current_url'] = result['url']
    
    def get_steps_summary(self):
        """
        获取已执行步骤的摘要
        """
        if not self.steps:
            return "暂无执行步骤"
        
        summary = "已执行步骤:\n"
        for i, step in enumerate(self.steps, 1):
            status = "成功" if step['result'].get('success', False) else "失败"
            summary += f"{i}. [{status}] {step['tool_name']}"
            if step['parameters']:
                summary += f" - 参数: {json.dumps(step['parameters'], ensure_ascii=False)}"
            summary += "\n"
        return summary
    
    def get_variables_summary(self):
        """
        获取当前可用的中间变量摘要
        """
        if not self.variables:
            return "暂无中间变量"
        
        return "可用中间变量:\n" + "\n".join([f"- {k}: {str(v)[:50]}..." if len(str(v)) > 50 else f"- {k}: {v}" for k, v in self.variables.items()])
    
    def increment_iteration(self):
        """
        增加迭代次数
        """
        self.current_iteration += 1
    
    def is_max_iterations_reached(self):
        """
        检查是否达到最大迭代次数
        """
        return self.current_iteration >= self.max_iterations
    
    def set_completed(self, answer):
        """
        标记任务完成
        """
        self.is_completed = True
        self.final_answer = answer

def build_chained_system_prompt():
    """
    构建链式调用的系统提示词
    """
    tools_description = []
    for tool_name, tool_info in TOOLS.items():
        tool_desc = f"- {tool_name}: {tool_info['description']}\n"
        tool_desc += f"  参数: {json.dumps(tool_info['parameters'], ensure_ascii=False, indent=2)}"
        tools_description.append(tool_desc)
    
    skills_data = get_skills_list()
    skills_json = json.dumps({"skills": skills_data}, ensure_ascii=False, indent=2)
    
    system_prompt = """你是一个智能工具调用规划师，负责根据用户请求，分析需要调用哪些工具，并决定调用顺序。

**可用工具列表：**
""" + "\n".join(tools_description) + """

**可用技能列表：**
""" + skills_json + """

**链式调用规则：**
1. 你可以按照顺序调用多个工具，前一个工具的输出可以作为后一个工具的输入
2. 工具调用有顺序依赖关系，某些工具需要其他工具的结果作为参数
3. 你需要根据中间结果自主决定下一步调用哪个工具
4. 可以使用上下文变量（如 matched_files, current_file, last_result 等）
5. 如果需要总结内容，应该先获取原始内容，再进行总结

**工具调用顺序示例：**
场景1：查找并总结文件
步骤1: search_files_with_keyword → 获取包含关键词的文件列表
步骤2: read_file_content → 读取第一个文件内容
步骤3: read_file_content → 读取第二个文件内容
步骤4: 直接总结所有文件内容

场景2：网页处理
步骤1: fetch_webpage → 获取网页内容
步骤2: write_file_content → 将内容保存到文件

场景3：技能查询
步骤1: load_skill_content → 加载技能详细内容
步骤2: 直接总结技能规则

**输出格式要求：**
你必须输出JSON格式，包含以下两种情况：

1. 任务已完成，直接回答用户：
{"done": true, "answer": "最终回答内容"}

2. 需要继续调用工具：
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}

**注意事项：**
- 只能输出一行JSON，不能有任何其他文本
- 如果调用工具失败，可以尝试其他工具或直接总结已有信息
- 当你认为已经收集足够信息可以回答用户时，设置"done": true
- 如果无法完成任务，也请设置"done": true并说明原因

现在请根据用户请求进行分析并输出决策。"""
    
    return system_prompt

def build_analysis_prompt(user_request, context):
    """
    构建分析提示词，包含用户请求、已执行步骤历史和决策规则
    """
    prompt = f"""用户请求: {user_request}

{context.get_steps_summary()}

{context.get_variables_summary()}

请分析当前状态并决定下一步操作。

**决策规则：**
1. 检查是否已收集足够信息回答用户
2. 如果需要更多信息，选择合适的工具继续调用
3. 如果已有足够信息，直接总结回答

**输出格式：**
{"done": true, "answer": "最终回答内容"}
或
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}
"""
    return prompt

def extract_json_from_response(content):
    """
    从LLM响应中提取JSON部分，处理可能的markdown代码块标记
    """
    try:
        # 移除可能的markdown代码块标记
        content = content.strip()
        
        # 处理 ```json ... ``` 格式
        if content.startswith('```'):
            # 找到第一个换行后的内容
            lines = content.split('\n')
            if len(lines) > 1:
                # 从第二行开始到倒数第二行（去掉最后的```）
                content = '\n'.join(lines[1:-1])
            content = content.strip()
        
        # 处理可能的其他标记
        content = content.replace('json\n', '').strip()
        
        # 尝试解析JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # 如果解析失败，尝试查找内容中的JSON对象
        try:
            # 找到第一个 { 和最后一个 }
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                json_str = content[start_idx:end_idx+1]
                return json.loads(json_str)
        except:
            pass
        return None
    except Exception:
        return None

def parse_tool_call(content):
    """
    解析LLM响应中的工具调用
    支持JSON格式和tool_calls格式
    """
    try:
        result = extract_json_from_response(content)
        
        if result is None:
            return None, None
        
        # 检查是否为完成状态
        if 'done' in result:
            if result['done']:
                return 'done', result.get('answer', '')
        
        # 检查是否为工具调用
        if 'tool_call' in result:
            tool_call = result['tool_call']
            if isinstance(tool_call, dict) and 'name' in tool_call:
                tool_name = tool_call['name']
                arguments = tool_call.get('arguments', {})
                return tool_name, arguments
        
        # 支持OpenAI标准Function Calling格式
        if 'tool_calls' in result:
            tool_calls = result['tool_calls']
            if isinstance(tool_calls, list) and len(tool_calls) > 0:
                tool_call = tool_calls[0]
                tool_name = tool_call.get('id', '') or tool_call.get('type', '')
                if 'function' in tool_call:
                    func = tool_call['function']
                    tool_name = func.get('name', '')
                    arguments = func.get('arguments', {})
                    return tool_name, arguments
        
        return None, None
    
    except Exception as e:
        print(f"解析工具调用失败: {str(e)}")
        return None, None

def execute_tool_call(tool_name, arguments):
    """
    执行单个工具调用
    """
    if tool_name not in TOOLS:
        return {
            'success': False,
            'error': f'未知工具: {tool_name}'
        }
    
    tool_info = TOOLS[tool_name]
    tool_function = tool_info['function']
    
    try:
        result = tool_function(**arguments)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'执行工具失败: {str(e)}'
        }

def call_llm(prompt, env_vars, system_prompt=None):
    """
    调用LLM API（非流式）
    """
    base_url = env_vars.get('BASE_URL', 'http://localhost:11434/api/chat')
    model = env_vars.get('MODEL', 'llama3')
    api_key = env_vars.get('API_KEY', '')
    
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    start_time = time.time()
    
    try:
        req = urllib.request.Request(base_url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            
            end_time = time.time()
            
            if 'error' in response_data:
                return {
                    'error': response_data['error'],
                    'time_taken': end_time - start_time
                }
            
            choices = response_data.get('choices', [])
            if choices:
                message = choices[0].get('message', {})
                content = message.get('content', '')
                return {
                    'content': content,
                    'time_taken': end_time - start_time,
                    'success': True
                }
            
            return {
                'error': '未获取到响应内容',
                'time_taken': end_time - start_time
            }
    
    except urllib.error.HTTPError as e:
        end_time = time.time()
        return {
            'error': f"HTTP Error: {e.code} - {e.reason}",
            'time_taken': end_time - start_time
        }
    except Exception as e:
        end_time = time.time()
        return {
            'error': f"Error: {str(e)}",
            'time_taken': end_time - start_time
        }

def execute_chained_tool_call(user_request, env_vars, max_iterations=10):
    """
    执行链式工具调用的完整流程
    """
    # 初始化上下文
    context = ChainedCallContext(max_iterations=max_iterations)
    context.user_request = user_request
    
    print(f"=== 开始处理请求: {user_request} ===")
    print(f"最大迭代次数: {max_iterations}")
    print("-" * 60)
    
    while not context.is_completed and not context.is_max_iterations_reached():
        context.increment_iteration()
        print(f"\n迭代 {context.current_iteration}/{max_iterations}")
        
        # 构建分析提示词
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        # 调用LLM决定下一步操作
        print("调用LLM分析...")
        result = call_llm(analysis_prompt, env_vars, system_prompt=build_chained_system_prompt())
        
        if 'error' in result:
            print(f"LLM调用失败: {result['error']}")
            context.set_completed(f"处理请求时遇到错误: {result['error']}")
            break
        
        llm_response = result['content']
        print(f"LLM响应: {llm_response[:100]}..." if len(llm_response) > 100 else f"LLM响应: {llm_response}")
        
        # 解析LLM响应
        tool_name, arguments = parse_tool_call(llm_response)
        
        if tool_name == 'done':
            # 任务完成
            print("任务已完成")
            context.set_completed(arguments)
            break
        
        if tool_name is None:
            # 无法解析工具调用，尝试总结
            print("无法解析工具调用，尝试总结已有信息")
            context.set_completed(f"根据已有信息，我来为您总结：\n\n{context.get_steps_summary()}\n\n由于工具调用解析失败，如需更详细的信息，请重新描述您的请求。")
            break
        
        # 执行工具调用
        print(f"执行工具: {tool_name}")
        print(f"参数: {json.dumps(arguments, ensure_ascii=False)}")
        
        tool_result = execute_tool_call(tool_name, arguments)
        print(f"工具执行结果: {'成功' if tool_result.get('success') else '失败'}")
        
        # 记录到上下文
        context.add_step(tool_name, arguments, tool_result)
        
        # 显示工具结果摘要
        if tool_result.get('success'):
            result_str = tool_result.get('result', '')
            if isinstance(result_str, str) and len(result_str) > 100:
                print(f"结果摘要: {result_str[:100]}...")
            else:
                print(f"结果: {result_str}")
        else:
            print(f"错误信息: {tool_result.get('error', '未知错误')}")
    
    # 检查是否达到最大迭代次数
    if context.is_max_iterations_reached() and not context.is_completed:
        print("\n已达到最大迭代次数，强制总结")
        context.set_completed(f"已执行 {max_iterations} 次工具调用，以下是收集到的信息：\n\n{context.get_steps_summary()}\n\n如需继续处理，请重新发起请求。")
    
    print("\n" + "-" * 60)
    print(f"最终回答: {context.final_answer[:100]}..." if len(context.final_answer) > 100 else f"最终回答: {context.final_answer}")
    
    return context.final_answer

def test_chained_calls():
    """
    测试链式工具调用功能
    """
    env_vars = load_env()
    
    print("=== 测试1：文件搜索链式调用 ===")
    print("请求：查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
    print("-" * 60)
    
    # 模拟执行（由于没有实际LLM服务，这里手动执行）
    # 步骤1: 搜索文件
    search_result = execute_tool_call('search_files_with_keyword', {'directory': 'practice06', 'keyword': 'def'})
    print(f"步骤1 - 搜索结果: {search_result.get('result', '')}")
    
    if search_result.get('success') and 'files' in search_result:
        # 步骤2: 读取文件内容
        files = search_result['files']
        for file_info in files[:2]:  # 只读取前2个文件
            file_path = file_info['file']
            read_result = execute_tool_call('read_file_content', {'file_path': file_path})
            print(f"步骤2 - 读取文件 {file_path}: {'成功' if read_result.get('success') else '失败'}")
    
    print("\n总结：practice06目录下包含'def'关键词的文件主要包含工具函数定义，如技能解析、文件操作等功能。")
    print("\n" + "=" * 60)
    
    print("\n=== 测试2：技能查询链式调用 ===")
    print("请求：我想了解 notice 技能的详细规则")
    print("-" * 60)
    
    # 步骤1: 加载技能内容
    skill_result = execute_tool_call('load_skill_content', {'skill_name': 'notice'})
    if skill_result.get('success'):
        result = skill_result.get('result', '')
        print(f"Notice技能内容摘要:\n{result[:300]}..." if len(result) > 300 else f"Notice技能内容:\n{result}")
    else:
        print(f"加载技能失败: {skill_result.get('error', '未知错误')}")
    print("\n" + "=" * 60)
    
    print("\n=== 测试3：网页处理链式调用 ===")
    print("请求：访问网页并总结内容，保存到 practice07/summary.txt")
    print("-" * 60)
    
    # 步骤1: 获取网页内容（模拟）
    print("步骤1 - 获取网页内容: 模拟成功")
    webpage_content = """这是一个模拟的网页内容摘要。网页主要介绍了人工智能技术的发展趋势，包括机器学习、深度学习、自然语言处理等方面的最新进展。文章还讨论了AI在各个行业的应用案例，展示了人工智能技术的广泛应用前景。"""
    
    # 步骤2: 写入文件
    write_result = execute_tool_call('write_file_content', {
        'file_path': 'practice07/summary.txt',
        'content': webpage_content
    })
    print(f"步骤2 - 写入文件: {'成功' if write_result.get('success') else '失败'}")
    
    if write_result.get('success'):
        # 验证文件内容
        read_result = execute_tool_call('read_file_content', {'file_path': 'practice07/summary.txt'})
        if read_result.get('success'):
            print(f"验证文件内容: {read_result.get('result', '')}")
    print("\n" + "=" * 60)

def main():
    env_vars = load_env()
    
    print("=== LLM 链式工具调用系统 ===")
    print("支持的工具:")
    for tool_name, tool_info in TOOLS.items():
        print(f"  - {tool_name}: {tool_info['description']}")
    print("\n输入你的请求，按Enter发送。按Ctrl+C退出。")
    print("支持链式工具调用，LLM会自动决定调用顺序。")
    print("=" * 60)
    
    try:
        while True:
            try:
                prompt = input("\n您: ")
            except EOFError:
                break
            
            if not prompt.strip():
                continue
            
            if prompt.lower() == 'test':
                test_chained_calls()
                continue
            
            print("\nAI: 正在分析请求并执行链式工具调用...")
            print("-" * 40)
            
            # 执行链式工具调用
            final_answer = execute_chained_tool_call(prompt, env_vars)
            
            print("\n" + "-" * 40)
            print(f"AI: {final_answer}")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n\n聊天已结束。")

if __name__ == "__main__":
    main()