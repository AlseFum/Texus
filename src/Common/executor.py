from typing import Dict, Tuple
import re
import io
import sys


def execute_script(script_content: str, extra_globals: Dict = None) -> Tuple[bool, str, list]:
    """执行脚本的通用函数
    
    Args:
        script_content: 脚本内容
        extra_globals: 额外的全局变量
        
    Returns:
        (成功标志, 输出内容, 操作历史)
    """
    if not script_content.strip():
        return False, "", []
    
    # 延迟导入以避免循环导入
    from Database import vmAPI
    
    # 创建安全的执行环境
    db_api = vmAPI()
    safe_globals = {
        '__builtins__': {
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'print': print,
            'max': max,
            'min': min,
            'sum': sum,
            'sorted': sorted,
            'reversed': reversed,
            'any': any,
            'all': all,
        },
        'db': db_api,  # 提供数据库API
        're': re,      # 正则表达式
    }
    
    # 添加额外的全局变量
    if extra_globals:
        safe_globals.update(extra_globals)
    
    # 捕获输出
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    try:
        # 执行用户脚本
        exec(script_content, safe_globals, {})
        output = captured_output.getvalue()
        return True, output, db_api.operations
        
    except Exception as e:
        output = captured_output.getvalue()
        return False, str(e), db_api.operations
        
    finally:
        sys.stdout = old_stdout

