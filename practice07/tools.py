import os
import json
import re
import urllib.request
import urllib.error

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
    读取并列出所有可用的技能
    
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

def search_files_with_keyword(directory, keyword):
    """
    在指定目录下搜索包含指定关键词的文件
    
    参数:
        directory (str): 要搜索的目录路径
        keyword (str): 要搜索的关键词
    
    返回:
        dict: 包含搜索结果的字典
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(project_root, directory)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"目录不存在: {full_path}"
            }
        
        matching_files = []
        for root, dirs, files in os.walk(full_path):
            for file in files:
                if file.endswith('.py') or file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if keyword in content:
                                # 计算相对路径
                                rel_path = os.path.relpath(file_path, project_root)
                                matching_files.append({
                                    "file": rel_path,
                                    "line_count": len(content.split('\n'))
                                })
                    except Exception as e:
                        continue
        
        if not matching_files:
            return {
                "success": True,
                "result": f"在目录 '{directory}' 中未找到包含关键词 '{keyword}' 的文件"
            }
        
        result = f"在目录 '{directory}' 中找到 {len(matching_files)} 个包含关键词 '{keyword}' 的文件:\n"
        for item in matching_files:
            result += f"- {item['file']} (约 {item['line_count']} 行)\n"
        
        return {
            "success": True,
            "result": result.strip(),
            "files": matching_files
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"搜索文件失败: {str(e)}"
        }

def read_file_content(file_path):
    """
    读取指定文件的内容
    
    参数:
        file_path (str): 要读取的文件路径（相对于项目根目录）
    
    返回:
        dict: 包含文件内容的字典
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(project_root, file_path)
        
        if not os.path.exists(full_path):
            return {
                "success": False,
                "error": f"文件不存在: {full_path}"
            }
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "result": content,
            "file_path": file_path
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }

def fetch_webpage(url):
    """
    获取指定网页的内容
    
    参数:
        url (str): 网页URL
    
    返回:
        dict: 包含网页内容的字典
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        return {
            "success": True,
            "result": content,
            "url": url
        }
    
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP错误: {e.code} - {e.reason}"
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL错误: {str(e.reason)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"获取网页失败: {str(e)}"
        }

def write_file_content(file_path, content):
    """
    将内容写入指定文件
    
    参数:
        file_path (str): 要写入的文件路径（相对于项目根目录）
        content (str): 要写入的内容
    
    返回:
        dict: 包含写入结果的字典
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        full_path = os.path.join(project_root, file_path)
        
        # 确保父目录存在
        parent_dir = os.path.dirname(full_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "result": f"内容已成功写入文件: {file_path}",
            "file_path": file_path
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"写入文件失败: {str(e)}"
        }

# 工具函数映射
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
    "search_files_with_keyword": {
        "function": search_files_with_keyword,
        "description": "在指定目录下搜索包含指定关键词的文件，返回匹配的文件列表",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "要搜索的目录路径（相对于项目根目录）"
                },
                "keyword": {
                    "type": "string",
                    "description": "要搜索的关键词"
                }
            },
            "required": ["directory", "keyword"]
        }
    },
    "read_file_content": {
        "function": read_file_content,
        "description": "读取指定文件的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件路径（相对于项目根目录）"
                }
            },
            "required": ["file_path"]
        }
    },
    "fetch_webpage": {
        "function": fetch_webpage,
        "description": "获取指定网页的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "网页URL"
                }
            },
            "required": ["url"]
        }
    },
    "write_file_content": {
        "function": write_file_content,
        "description": "将内容写入指定文件",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要写入的文件路径（相对于项目根目录）"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的内容"
                }
            },
            "required": ["file_path", "content"]
        }
    }
}