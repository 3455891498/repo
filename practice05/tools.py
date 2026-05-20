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
    }
}