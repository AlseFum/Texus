from util import Request
from Common.types import Access, ByType
from Database import getmime


def detect_by(request: Request):
    """通过 query 参数、User-Agent 和其他请求头判断访问类型"""
    
    # 优先检查 query 参数
    from_param = request.query_params.get("from", "").lower()
    
    
    # 如果 query 中明确指定了 from 参数，优先使用
    if from_param == "api":
        return ByType.API
    elif from_param == "web":
        return ByType.WEB
    
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
        return ByType.API
    elif any(web_indicators):
        return ByType.WEB
    else:
        # 默认情况，可能是未知的客户端
        if "json" in accept or "json" in content_type:
            return ByType.API
        else:
            return ByType.API


def detect_who(request: Request):
    """通过 query 参数、User-Agent 和其他请求头判断访问者类型"""
    
    # 优先检查 query 参数中的 role
    role_param = request.query_params.get("role", "").lower()
    
    # 如果 query 中明确指定了 role 参数，优先使用
    if role_param in ["user", "script", "agent"]:
        return role_param
    
    # 如果没有明确指定，则根据 User-Agent 等判断
    user_agent = request.headers.get("user-agent", "").lower()
    content_type = request.headers.get("content-type", "").lower()
    accept = request.headers.get("accept", "").lower()
    
    # Script 请求的特征
    script_indicators = [
        # 命令行工具和脚本
        "curl/" in user_agent,
        "wget/" in user_agent,
        "httpie/" in user_agent,
        "python-requests/" in user_agent,
        "python-urllib/" in user_agent,
        
        # Shell 和命令行工具
        "powershell/" in user_agent,
        "windowspowershell/" in user_agent,
        "pwsh/" in user_agent,
        "bash/" in user_agent,
        "zsh/" in user_agent,
        
        # 编程语言相关的 HTTP 客户端
        "go-http-client/" in user_agent,
        "java/" in user_agent and "http" in user_agent,
        "ruby" in user_agent and "http" in user_agent,
        
        # 无 User-Agent（通常是脚本请求）
        user_agent == "",
        
        # 明确的脚本标识
        "script" in user_agent,
        "automation" in user_agent,
    ]
    
    # Agent 请求的特征
    agent_indicators = [
        # 开发工具和 API 测试工具
        "postman" in user_agent,
        "insomnia" in user_agent,
        "axios/" in user_agent,
        "fetch/" in user_agent,
        
        # 移动端 API 请求
        "okhttp/" in user_agent,
        "alamofire/" in user_agent,
        
        # 明确的 agent 标识
        "agent" in user_agent,
        "bot" in user_agent and "browser" not in user_agent,
        "api" in user_agent,
        
        # 特定的内容类型表明是程序化访问
        "application/json" in content_type,
        "application/json" in accept and "text/html" not in accept,
    ]
    
    # User 请求的特征（真实用户浏览器）
    user_indicators = [
        # 真正的浏览器通常同时包含多个标识
        "mozilla/" in user_agent and ("chrome/" in user_agent or "firefox/" in user_agent or "safari/" in user_agent or "edge/" in user_agent),
        "chrome/" in user_agent and "safari/" in user_agent,  # Chrome 包含 Safari 标识
        "firefox/" in user_agent and "gecko/" in user_agent,  # Firefox 包含 Gecko
        "safari/" in user_agent and "version/" in user_agent and "webkit/" in user_agent,  # Safari 特征
        "edge/" in user_agent and ("chrome/" in user_agent or "webkit/" in user_agent),  # Edge 特征
        "opera/" in user_agent,
        
        # Accept 头明确要求 HTML（用户浏览器的典型行为）
        "text/html" in accept and "application/xhtml+xml" in accept,
        "text/html,application/xhtml+xml" in accept,
    ]
    
    # 判断逻辑：按优先级判断
    if any(user_indicators):
        return "user"
    elif any(agent_indicators):
        return "agent"
    elif any(script_indicators):
        return "script"
    else:
        # 默认情况，根据内容类型判断
        if "json" in accept or "json" in content_type:
            return "agent"
        else:
            return "user"


def request2access(
    request: Request,
    path: str | None = None,
    mime: str | None = None,
    entry: str | None = None,
    who: str | None = None,
    by: str | None = None,
) -> Access:
    """将HTTP请求转换为访问对象

    Args:
        request: HTTP请求对象
        path: 可选，指定路径字符串（默认从request.url.path获取）
        mime: 可选，强制指定MIME类型（否则自动检测）
        entry: 可选，指定入口点（否则从路径解析）
        who: 可选，指定访问者类型（user/script/agent，否则从请求参数或默认为user）
        by: 可选，指定访问方式（否则自动检测）
        
    Returns:
        Access: 构造的访问对象
    """
    # 1. 解析路径信息
    if path is None:
        path = request.url.path
    
    # 过滤掉空的路径部分
    path_parts = [part for part in path.split("/") if part]
    
    # 解析路径：第一个部分作为 primary，剩余部分作为 tags
    if path_parts:
        primary = path_parts[0]
        path_tags = path_parts[1:]  # 剩余的路径片段
    else:
        primary = ""
        path_tags = []
    
    # 确定 entry 和 mime
    if entry is None:
        # 从 primary 中分离 entry 和 mime（如果有扩展名）
        if "." in primary:
            entry, primary_mime = primary.rsplit(".", 1)
        else:
            entry = primary
            primary_mime = ""
    else:
        primary_mime = ""
    
    # 确定 mime 类型
    if mime is None:
        mime = primary_mime or getmime(entry) or "text"
    
    # 合并 query 参数
    # 1. 先获取 URL 查询参数
    query_dict = dict(request.query_params)
    
    # 2. 将路径片段作为标记添加到 query（值为 True）
    for tag in path_tags:
        # 如果 tag 包含扩展名，去掉扩展名
        tag_key = tag.rsplit(".", 1)[0] if "." in tag else tag
        query_dict[tag_key] = True
    
    # 确定访问者类型
    if who is None:
        who = detect_who(request)
    
    # 确定访问方式
    if by is None:
        by = detect_by(request)
    
    return Access(
        path=path,
        mime=mime,
        entry=entry or "index",  # 如果没有 entry，默认为 "index"
        who=who,
        by=by if hasattr(by, 'value') else str(by),
        query=query_dict,
        cookies=dict(request.cookies)
    )


async def replaceByBody(pack, body_or_request):
    """
    只对查询参数进行特殊值插值处理
    
    Args:
        pack: Access 对象
        body_or_request: 可以是 dict 类型的 body 数据，或者 Request 对象
    
    Returns:
        处理后的 pack 对象
    """
    # 判断传入的是 body 字典还是 Request 对象
    if isinstance(body_or_request, dict):
        # 直接传入 body 的情况
        body = body_or_request
    else:
        # 传入 Request 对象的情况
        try:
            body = await body_or_request.json()
        except Exception:
            body = {}
    
    if not body:
        return pack
    
    # 处理查询参数中的插值
    for q_key, q_value in list(pack.query.items()):
        if isinstance(q_value, str) and q_value.startswith("$"):
            body_key = q_value[1:]
            if body_key in body:
                pack.query[q_key] = str(body[body_key])
    
    # 处理cookie中的插值
    for q_key, q_value in list(pack.cookies.items()):
        if isinstance(q_value, str) and q_value.startswith("$"):
            body_key = q_value[1:]
            if body_key in body:
                pack.cookies[q_key] = str(body[body_key])
    # pack 没有body，不要设置
    
    return pack