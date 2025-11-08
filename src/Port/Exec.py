from typing import Dict, Any, Tuple, Optional
from Common.util import first_valid
from Database import Table
from Common.base import FinalVis, entry
from Common import execute_script
from datetime import datetime


class Exec:
    """执行用户脚本的Port - 只能操作数据库entry"""
    
    @staticmethod
    def access(pack) -> FinalVis:
        """主访问方法"""
        return Exec.run_script(pack)
    
    @staticmethod
    def run_script(pack) -> FinalVis:
        """执行用户脚本"""
        # 判断是否是 API 请求
        is_api = getattr(pack, 'by', '') == 'api'
        
        # 获取脚本内容
        script_content = first_valid(pack.query.get('script', None), "")
        if not script_content:
            # 从entry中获取脚本
            main_table = Table.of("main")
            script_entry = main_table.get(pack.entry)
            if isinstance(script_entry, entry):
                script_content = script_entry.value.get("text", "")
            else:
                script_content = str(script_entry or "")
        
        if not script_content.strip():
            if is_api:
                return FinalVis.of("text", {
                    "success": False,
                    "error": "No script content provided",
                    "output": "",
                    "operations": []
                }, skip=True)
            else:
                return FinalVis.of("raw", "No script content provided")
        
        # 使用通用执行函数
        success, output, operations = execute_script(script_content)
        
        if success:
            if is_api:
                return FinalVis.of("text", {
                    "success": True,
                    "output": output,
                    "operations": operations,
                    "operations_count": len(operations)
                }, skip=True)
            else:
                # Web 请求：直接用 raw 表达 output
                return FinalVis.of("raw", output if output else "Script executed successfully")
        else:
            if is_api:
                return FinalVis.of("text", {
                    "success": False,
                    "error": output,
                    "output": "",
                    "operations": operations
                }, skip=True)
            else:
                # Web 请求：直接用 raw 表达错误信息
                return FinalVis.of("raw", f"Script execution error: {output}")

# 插件注册函数
def registry():
    return {
        "mime": ["py", "exec"],
        "port": Exec
    }
