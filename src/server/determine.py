from fastapi import Request
from protocol.types import Access

def determine_access_type(request: Request):
    """通过 query 参数、User-Agent 和其他请求头判断访问类型"""
    
    # 优先检查 query 参数
    from_param = request.query_params.get("from", "").lower()
    
    
    # 如果 query 中明确指定了 from 参数，优先使用
    if from_param == "api":
        return Access.API
    elif from_param == "web":
        return Access.Web
    
    # 如果没有明确指定，则根据 User-Agent 等判断
    user_agent = request.headers.get("user-agent", "").lower()
    content_type = request.headers.get("content-type", "").lower()
    accept = request.headers.get("accept", "").lower()
    
    # 调试信息
    
    # API 请求的特征
    api_indicators = [
        # 明确的 API 请求头
        "application/json" in content_type,
        "application/json" in accept,
        
        # 常见的 API 客户端 User-Agent
        "curl/" in user_agent,
        "wget/" in user_agent,
        "httpie/" in user_agent,
        "postman" in user_agent,
        "insomnia" in user_agent,
        "axios/" in user_agent,
        "fetch/" in user_agent,
        "python-requests/" in user_agent,
        "python-urllib/" in user_agent,
        
        # Shell 和命令行工具
        "powershell/" in user_agent,
        "windowspowershell/" in user_agent,
        "pwsh/" in user_agent,
        "bash/" in user_agent,
        "zsh/" in user_agent,
        
        # 移动端 API 请求
        "okhttp/" in user_agent,
        "alamofire/" in user_agent,
        
        # 编程语言相关的 HTTP 客户端
        "go-http-client/" in user_agent,
        "java/" in user_agent and "http" in user_agent,
        "ruby" in user_agent and "http" in user_agent,
        
        # 无 User-Agent（通常是脚本请求）
        user_agent == "",
        
        # 明确指定 API 的自定义头
        "api" in user_agent,
        "bot" in user_agent and "browser" not in user_agent,
    ]
    
    # Web 浏览器的特征 - 更精确的判断
    web_indicators = [
        # 真正的浏览器通常同时包含多个标识
        "mozilla/" in user_agent and ("chrome/" in user_agent or "firefox/" in user_agent or "safari/" in user_agent or "edge/" in user_agent),
        "chrome/" in user_agent and "safari/" in user_agent,  # Chrome 包含 Safari 标识
        "firefox/" in user_agent and "gecko/" in user_agent,  # Firefox 包含 Gecko
        "safari/" in user_agent and "version/" in user_agent and "webkit/" in user_agent,  # Safari 特征
        "edge/" in user_agent and ("chrome/" in user_agent or "webkit/" in user_agent),  # Edge 特征
        "opera/" in user_agent,
        
        # Accept 头明确要求 HTML
        "text/html" in accept and "application/xhtml+xml" in accept,
        "text/html,application/xhtml+xml" in accept,
    ]
    
    # 判断逻辑
    if any(api_indicators):
        return Access.API
    elif any(web_indicators):
        return Access.Web
    else:
        # 默认情况，可能是未知的客户端
        if "json" in accept or "json" in content_type:
            print(f"DEBUG - Unknown client, but has JSON - API")
            return Access.API
        else:
            print(f"DEBUG - Unknown client, default - API")
            return Access.API
