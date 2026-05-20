import os
import json
import time
import urllib.request
import urllib.error
import sys

class ChainedCallContext:
    """
    链式调用上下文管理器，用于在多个工具调用之间传递数据和状态
    
    **功能说明**:
    - 记录每一步工具调用的详细信息
    - 在多个工具之间传递中间变量
    - 控制最大迭代次数，防止无限循环
    - 提供调用链摘要信息
    
    **调用者**: 
    - chat_client.py: execute_chained_calls(), execute_tool_call()
    
    **被调用**:
    - 无（这是一个数据类，不调用其他函数）
    """
    
    def __init__(self, max_iterations=10):
        """
        初始化链式调用上下文
        
        参数:
            max_iterations (int): 最大迭代次数，默认10次，防止无限循环
        
        **调用者**:
        - chat_client.py: main()
        """
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.call_history = []
        self.variables = {}
        self.final_result = None
        self.is_complete = False
        self.error = None
    
    def add_call(self, tool_name, parameters, result):
        """
        记录一次工具调用
        
        参数:
            tool_name (str): 工具名称
            parameters (dict): 调用参数
            result (dict): 调用结果（包含success和result字段）
        
        **功能**:
        - 将调用记录添加到call_history列表
        - 如果调用成功，自动将结果存储到variables中，变量名为{tool_name}_result
        
        **调用者**:
        - chat_client.py: execute_chained_calls(), execute_tool_call()
        
        **被调用**:
        - 无
        """
        call_record = {
            "step": len(self.call_history) + 1,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "timestamp": time.time()
        }
        self.call_history.append(call_record)
        
        if result.get('success') and result.get('result'):
            var_name = f"{tool_name}_result"
            self.variables[var_name] = result['result']
    
    def get_variable(self, name):
        """
        获取变量值（用于链式调用中传递中间结果）
        
        参数:
            name (str): 变量名称，格式为{tool_name}_result
        
        返回:
            变量值，如果不存在返回None
        
        **功能**:
        - 从variables字典中获取指定变量
        - 用于解析$变量名格式的参数引用
        
        **调用者**:
        - chat_client.py: resolve_parameters()
        
        **被调用**:
        - 无
        """
        return self.variables.get(name)
    
    def set_variable(self, name, value):
        """
        设置变量值（用于手动设置中间变量）
        
        参数:
            name (str): 变量名称
            value: 变量值
        
        **功能**:
        - 手动设置变量，用于特殊场景下的数据传递
        
        **调用者**:
        - 内部使用或外部手动调用
        
        **被调用**:
        - 无
        """
        self.variables[name] = value
    
    def get_last_result(self):
        """
        获取最后一次工具调用的结果
        
        返回:
            dict: 最后一次调用的结果，包含success和result字段
        
        **功能**:
        - 获取call_history列表中最后一条记录的result字段
        - 用于链式调用中的结果传递
        
        **调用者**:
        - 外部调用获取最新结果
        
        **被调用**:
        - 无
        """
        if self.call_history:
            return self.call_history[-1]['result']
        return None
    
    def get_call_chain(self):
        """
        获取调用链的描述（格式化显示）
        
        返回:
            str: 调用链的描述，格式为"步骤1: tool1 -> 步骤2: tool2 -> ..."
        
        **功能**:
        - 将call_history转换为可读的调用链字符串
        - 用于日志输出和结果展示
        
        **调用者**:
        - get_summary(), 外部日志输出
        
        **被调用**:
        - 无
        """
        chain = []
        for call in self.call_history:
            chain.append(f"步骤{call['step']}: {call['tool_name']}")
        return " -> ".join(chain) if chain else "无"
    
    def should_continue(self):
        """
        检查是否应该继续迭代（防止无限循环）
        
        返回:
            bool: 如果可以继续返回True，否则返回False
        
        **功能**:
        - 检查三个终止条件：达到最大迭代次数、已完成标记、存在错误
        - 任何一个条件满足则返回False，停止迭代
        
        **调用者**:
        - chat_client.py: execute_chained_calls()循环判断
        
        **被调用**:
        - 无
        """
        if self.current_iteration >= self.max_iterations:
            self.error = f"达到最大迭代次数 ({self.max_iterations})"
            return False
        
        if self.is_complete:
            return False
        
        if self.error:
            return False
        
        return True
    
    def increment_iteration(self):
        """
        增加迭代计数（每次工具调用后调用）
        
        **功能**:
        - 递增current_iteration计数器
        - 配合should_continue()实现最大迭代次数控制
        
        **调用者**:
        - chat_client.py: execute_chained_calls()
        
        **被调用**:
        - 无
        """
        self.current_iteration += 1
    
    def set_complete(self, result):
        """
        设置链式调用完成（手动标记完成）
        
        参数:
            result: 最终结果
        
        **功能**:
        - 设置is_complete为True
        - 保存最终结果到final_result
        - 调用should_continue()将返回False
        
        **调用者**:
        - 外部手动标记完成
        
        **被调用**:
        - 无
        """
        self.is_complete = True
        self.final_result = result
    
    def get_summary(self):
        """
        获取链式调用的摘要信息
        
        返回:
            dict: 包含摘要信息的字典，包含total_steps, max_iterations, final_iteration, is_complete, call_chain, variables, error
        
        **功能**:
        - 汇总链式调用的完整信息
        - 包含调用步骤数、迭代次数、调用链描述、变量列表、错误信息
        
        **调用者**:
        - chat_client.py: 结果展示
        
        **被调用**:
        - get_call_chain()
        """
        return {
            "total_steps": len(self.call_history),
            "max_iterations": self.max_iterations,
            "final_iteration": self.current_iteration,
            "is_complete": self.is_complete,
            "call_chain": self.get_call_chain(),
            "variables": list(self.variables.keys()),
            "error": self.error
        }


def parse_skill_md(file_path):
    """
    解析SKILL.md文件的YAML front matter，提取name和description字段
    
    参数:
        file_path (str): SKILL.md文件的绝对路径
    
    返回:
        dict: 包含name和description的字典，如果解析失败返回None
    
    **功能**:
    - 读取SKILL.md文件内容
    - 解析---标记之间的YAML内容
    - 提取name和description字段
    
    **调用者**:
    - get_skills_list(), load_skill_content()
    
    **被调用**:
    - 无
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            return None
        
        end_index = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return None
        
        yaml_content = '\n'.join(lines[1:end_index])
        
        skill_info = {}
        for line in yaml_content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'name':
                    skill_info['name'] = value
                elif key == 'description':
                    skill_info['description'] = value
        
        if 'name' in skill_info and 'description' in skill_info:
            return skill_info
        
        return None
    
    except Exception as e:
        print(f"解析SKILL.md文件失败: {file_path}, 错误: {str(e)}")
        return None


def get_skills_list():
    """
    读取技能列表并返回包含name和description的列表
    
    返回:
        list: 包含技能信息的列表，每个技能是一个包含name和description的字典
    
    **功能**:
    - 扫描.agents/skills目录
    - 遍历所有子目录和.md文件
    - 调用parse_skill_md()解析每个SKILL.md文件
    - 返回技能信息列表
    
    **调用者**:
    - list_available_skills(), build_tools_system_prompt()
    
    **被调用**:
    - parse_skill_md()
    """
    try:
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills')
        
        if not os.path.exists(skills_dir):
            return []
        
        skill_items = []
        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            
            if os.path.isdir(item_path):
                skill_md_path = os.path.join(item_path, 'SKILL.md')
                if os.path.exists(skill_md_path):
                    skill_info = parse_skill_md(skill_md_path)
                    if skill_info:
                        skill_items.append(skill_info)
            elif item.endswith('.md'):
                skill_md_path = item_path
                skill_info = parse_skill_md(skill_md_path)
                if skill_info:
                    skill_items.append(skill_info)
        
        return skill_items
    
    except Exception as e:
        print(f"读取技能列表失败: {str(e)}")
        return []


def list_available_skills():
    """
    读取并列出所有可用的技能（工具函数）
    
    返回:
        dict: {"success": bool, "result": str}
    
    **功能**:
    - 调用get_skills_list()获取技能列表
    - 将技能列表格式化为JSON字符串
    - 返回格式化后的结果
    
    **调用者**:
    - TOOLS["list_available_skills"]: chat_client.py通过工具调用执行
    
    **被调用**:
    - get_skills_list()
    """
    skills_data = get_skills_list()
    
    if not skills_data:
        return {
            "success": True,
            "result": "暂无可用技能"
        }
    
    skills_json = json.dumps({"skills": skills_data}, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "result": f"可用技能列表:\n{skills_json}"
    }


def load_skill_content(skill_name):
    """
    加载指定技能的SKILL.md文件正文内容（YAML front matter之后的部分）
    
    参数:
        skill_name (str): 技能名称（目录名或SKILL.md中的name字段）
    
    返回:
        dict: {"success": bool, "result": str} 或 {"success": bool, "error": str}
    
    **功能**:
    - 在.agents/skills目录中查找指定技能
    - 支持按目录名或name字段匹配
    - 提取YAML front matter之后的正文内容
    - 返回技能详细说明供LLM遵照执行
    
    **调用者**:
    - TOOLS["load_skill_content"]: chat_client.py通过工具调用执行
    - chat_client.py: main()直接调用（通知撰写功能）
    
    **被调用**:
    - parse_skill_md()
    """
    try:
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills')
        
        if not os.path.exists(skills_dir):
            return {
                "success": False,
                "error": f"技能目录不存在: {skills_dir}"
            }
        
        skill_path = None
        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            
            if os.path.isdir(item_path):
                if item.lower() == skill_name.lower():
                    skill_md_path = os.path.join(item_path, 'SKILL.md')
                    if os.path.exists(skill_md_path):
                        skill_path = skill_md_path
                        break
                else:
                    skill_md_path = os.path.join(item_path, 'SKILL.md')
                    if os.path.exists(skill_md_path):
                        skill_info = parse_skill_md(skill_md_path)
                        if skill_info and skill_info.get('name', '').lower() == skill_name.lower():
                            skill_path = skill_md_path
                            break
            elif item.endswith('.md'):
                if item.replace('.md', '').lower() == skill_name.lower():
                    skill_path = item_path
                    break
                else:
                    skill_info = parse_skill_md(item_path)
                    if skill_info and skill_info.get('name', '').lower() == skill_name.lower():
                        skill_path = item_path
                        break
        
        if not skill_path:
            return {
                "success": False,
                "error": f"未找到技能: {skill_name}"
            }
        
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            return {
                "success": True,
                "result": content.strip()
            }
        
        end_index = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return {
                "success": True,
                "result": content.strip()
            }
        
        body_content = '\n'.join(lines[end_index+1:]).strip()
        
        return {
            "success": True,
            "result": body_content
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"加载技能内容失败: {str(e)}"
        }


def read_file(file_path):
    """
    读取指定文件的全部内容（链式调用工具）
    
    参数:
        file_path (str): 文件路径，可以是绝对路径或相对于项目根目录的路径
    
    返回:
        dict: {"success": bool, "result": str, "file_name": str, "file_size": int}
    
    **功能**:
    - 解析文件路径（支持相对路径和绝对路径）
    - 检查文件是否存在
    - 读取文件内容并返回
    
    **调用者**:
    - TOOLS["read_file"]: chat_client.py通过工具调用执行
    - 链式调用中的第一步工具
    
    **被调用**:
    - 无
    """
    try:
        full_path = file_path
        if not os.path.isabs(full_path):
            full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "result": content,
            "file_name": os.path.basename(file_path),
            "file_size": len(content)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }


def extract_info(text, pattern):
    """
    从文本中提取符合指定模式的信息（链式调用工具）
    
    参数:
        text (str): 要提取信息的文本内容（通常来自read_file的结果）
        pattern (str): 提取模式，可以是预定义模式（姓名、部门、职位、日期、数字、邮箱、电话）或自定义正则表达式
    
    返回:
        dict: {"success": bool, "result": list, "count": int}
    
    **功能**:
    - 支持预定义模式和自定义正则表达式
    - 使用re模块进行正则匹配
    - 返回匹配结果列表和匹配数量
    
    **调用者**:
    - TOOLS["extract_info"]: chat_client.py通过工具调用执行
    - 链式调用中的中间步骤工具（通常在read_file之后）
    
    **被调用**:
    - re.findall()
    """
    try:
        import re
        
        patterns_map = {
            "姓名": r"姓名[：:]\s*([^\n]+)",
            "部门": r"部门[：:]\s*([^\n]+)",
            "职位": r"职位[：:]\s*([^\n]+)",
            "日期": r"日期[：:]\s*([^\n]+)",
            "数字": r"\d+[\.。]\d+|\d+",
            "邮箱": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "电话": r"\d{3}[-\s]?\d{4}[-\s]?\d{4}"
        }
        
        regex_pattern = patterns_map.get(pattern, pattern)
        
        matches = re.findall(regex_pattern, text)
        
        return {
            "success": True,
            "result": matches if matches else [],
            "count": len(matches)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"提取信息失败: {str(e)}"
        }


def format_data(data, format_type):
    """
    格式化数据为指定格式（链式调用工具）
    
    参数:
        data: 要格式化的数据（通常来自extract_info的结果）
        format_type (str): 格式化类型：json、text 或 table
    
    返回:
        dict: {"success": bool, "result": str}
    
    **功能**:
    - 根据format_type参数格式化数据
    - JSON格式：使用json.dumps()转换
    - text格式：转换为字符串
    - table格式：生成表格描述
    
    **调用者**:
    - TOOLS["format_data"]: chat_client.py通过工具调用执行
    - 链式调用中的最后步骤工具（通常在extract_info之后）
    
    **被调用**:
    - json.dumps()
    """
    try:
        if format_type == "json":
            if isinstance(data, str):
                formatted = json.dumps({"data": data}, ensure_ascii=False, indent=2)
            else:
                formatted = json.dumps(data, ensure_ascii=False, indent=2)
        elif format_type == "text":
            if isinstance(data, (list, dict)):
                formatted = json.dumps(data, ensure_ascii=False)
            else:
                formatted = str(data)
        elif format_type == "table":
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                headers = list(data[0].keys())
                rows = [[item.get(h, "") for h in headers] for item in data]
                formatted = f"表格格式 ({len(rows)}行{len(headers)}列)"
            else:
                formatted = f"表格数据: {len(data) if isinstance(data, list) else 1}条"
        else:
            formatted = str(data)
        
        return {
            "success": True,
            "result": formatted
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"格式化数据失败: {str(e)}"
        }


TOOLS = {
    "list_available_skills": {
        "function": list_available_skills,
        "description": "读取并列出所有可用的技能",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "load_skill_content": {
        "function": load_skill_content,
        "description": "加载指定技能的SKILL.md文件正文内容（YAML front matter之后的部分），用于让LLM遵照执行",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "技能名称"
                }
            },
            "required": ["skill_name"]
        }
    },
    "read_file": {
        "function": read_file,
        "description": "读取指定路径的文件内容",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径，可以是绝对路径或相对于项目根目录的路径"
                }
            },
            "required": ["file_path"]
        }
    },
    "extract_info": {
        "function": extract_info,
        "description": "从文本中提取符合指定模式的信息，如姓名、部门、数字等",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要提取信息的文本内容"
                },
                "pattern": {
                    "type": "string",
                    "description": "提取模式，可以是预定义的模式（姓名、部门、职位、日期、数字、邮箱、电话）或正则表达式"
                }
            },
            "required": ["text", "pattern"]
        }
    },
    "format_data": {
        "function": format_data,
        "description": "格式化数据为指定格式（json、text、table）",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "要格式化的数据"
                },
                "format_type": {
                    "type": "string",
                    "description": "格式化类型：json、text 或 table"
                }
            },
            "required": ["data", "format_type"]
        }
    }
}