import os
import json
import subprocess

def anythingllm_query(message):
    """
    使用curl命令访问AnythingLLM的聊天API接口
    
    参数:
        message (str): 查询消息
    
    返回:
        dict: 包含查询结果的结果
    """
    try:
        # 读取.env文件中的配置
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        anythingllm_api_key = ""
        anythingllm_workspace_slug = ""
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        if key == 'ANYTHINGLLM_API_KEY':
                            anythingllm_api_key = value
                        elif key == 'ANYTHINGLLM_WORKSPACE_SLUG':
                            anythingllm_workspace_slug = value
        
        if not anythingllm_api_key:
            return {
                "success": False,
                "error": "未找到ANYTHINGLLM_API_KEY配置"
            }
        
        if not anythingllm_workspace_slug:
            return {
                "success": False,
                "error": "未找到ANYTHINGLLM_WORKSPACE_SLUG配置"
            }
        
        # 构建API URL
        api_url = f"http://localhost:3001/api/v1/workspace/{anythingllm_workspace_slug}/chat"
        
        # 构建请求数据
        payload = json.dumps({
            "message": message,
            "thinking": "",
            "includeHistory": True
        }, ensure_ascii=False)
        
        # 构建curl命令
        curl_command = [
            "curl",
            "-X", "POST",
            api_url,
            "-H", f"Authorization: Bearer {anythingllm_api_key}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ]
        
        # 执行curl命令
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 检查执行结果
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"curl命令执行失败: {result.stderr}"
            }
        
        # 解析响应
        try:
            response = json.loads(result.stdout)
            
            # 只返回简洁的结果
            if response.get('textResponse'):
                return {
                    "success": True,
                    "result": response['textResponse'].strip()
                }
            elif response.get('error'):
                return {
                    "success": False,
                    "error": response['error']
                }
            else:
                return {
                    "success": True,
                    "result": "查询完成，但没有返回结果。"
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"响应解析失败: {result.stdout}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"查询失败: {str(e)}"
        }

def list_available_skills():
    """
    读取本项目目录下的.agents目录下的skills目录下的所有一级子目录，
    读取每个子目录内的SKILL.md文件的YAML front matter，提取name和description字段
    
    返回:
        dict: 包含技能列表的结果
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

def get_skills_list():
    """
    读取技能列表并返回包含name和description的列表
    
    返回:
        list: 包含技能信息的列表，每个技能是一个包含name和description的字典
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

def parse_skill_md(file_path):
    """
    解析SKILL.md文件的YAML front matter，提取name和description字段
    
    参数:
        file_path (str): SKILL.md文件的路径
    
    返回:
        dict: 包含name和description的字典，如果解析失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找YAML front matter（---标记之间的内容）
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            return None
        
        # 找到结束的---标记
        end_index = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return None
        
        # 提取YAML内容
        yaml_content = '\n'.join(lines[1:end_index])
        
        # 解析YAML内容，提取name和description
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
        
        # 确保name和description都存在
        if 'name' in skill_info and 'description' in skill_info:
            return skill_info
        
        return None
    
    except Exception as e:
        print(f"解析SKILL.md文件失败: {file_path}, 错误: {str(e)}")
        return None

def load_skill_content(skill_name):
    """
    加载指定技能的SKILL.md文件正文内容（YAML front matter之后的部分）
    
    参数:
        skill_name (str): 技能名称
    
    返回:
        dict: 包含技能内容的结果
    """
    try:
        skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.agents', 'skills')
        
        if not os.path.exists(skills_dir):
            return {
                "success": False,
                "error": f"技能目录不存在: {skills_dir}"
            }
        
        # 查找技能对应的目录或文件
        skill_path = None
        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            
            if os.path.isdir(item_path):
                # 检查目录名是否匹配技能名（不区分大小写）
                if item.lower() == skill_name.lower():
                    skill_md_path = os.path.join(item_path, 'SKILL.md')
                    if os.path.exists(skill_md_path):
                        skill_path = skill_md_path
                        break
                else:
                    # 检查目录内的SKILL.md文件中的name字段
                    skill_md_path = os.path.join(item_path, 'SKILL.md')
                    if os.path.exists(skill_md_path):
                        skill_info = parse_skill_md(skill_md_path)
                        if skill_info and skill_info.get('name', '').lower() == skill_name.lower():
                            skill_path = skill_md_path
                            break
            elif item.endswith('.md'):
                # 检查文件名是否匹配
                if item.replace('.md', '').lower() == skill_name.lower():
                    skill_path = item_path
                    break
                else:
                    # 检查文件中的name字段
                    skill_info = parse_skill_md(item_path)
                    if skill_info and skill_info.get('name', '').lower() == skill_name.lower():
                        skill_path = item_path
                        break
        
        if not skill_path:
            return {
                "success": False,
                "error": f"未找到技能: {skill_name}"
            }
        
        # 读取并提取YAML front matter之后的正文内容
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            # 没有YAML front matter，直接返回全部内容
            return {
                "success": True,
                "result": content.strip()
            }
        
        # 找到结束的---标记
        end_index = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            # 没有找到结束标记，直接返回全部内容
            return {
                "success": True,
                "result": content.strip()
            }
        
        # 提取YAML front matter之后的正文内容
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

# 工具函数映射
TOOLS = {
    "anythingllm_query": {
        "function": anythingllm_query,
        "description": "访问AnythingLLM的聊天API接口，查询文档仓库中的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "查询消息"
                }
            },
            "required": ["message"]
        }
    },
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
    }
}