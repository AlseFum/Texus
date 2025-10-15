from typing import Dict, Any
from util import first_valid
from Database import pub_get, pub_set, Table
from protocol.types import FinalVis, entry
from datetime import datetime
import re


class DatabaseAPI:
    """为用户脚本提供的数据库操作API"""
    
    def __init__(self):
        self.operations = []  # 记录操作历史
    
    def get(self, key: str) -> entry:
        """获取entry对象"""
        result = pub_get(key)
        self.operations.append(f"GET {key}")
        if isinstance(result, entry):
            return result
        elif isinstance(result, dict):
            return entry(mime="text", value=result)
        else:
            return entry(mime="text", value={"text": str(result or ""), "lastSavedTime": None})
    
    def set(self, key: str, content: str, mime: str = "text") -> bool:
        """设置entry内容"""
        try:
            file_data = {
                "text": str(content),
                "lastSavedTime": datetime.now()
            }
            new_entry = entry(mime=mime, value=file_data)
            pub_set(key, new_entry)
            self.operations.append(f"SET {key}")
            return True
        except Exception as e:
            self.operations.append(f"SET {key} FAILED: {e}")
            return False
    
    def list_keys(self, pattern: str = None) -> list:
        """列出所有键，可选择模式匹配"""
        pub_table = Table.of("PUB")
        all_keys = list(pub_table.inner.keys()) if hasattr(pub_table, 'inner') else []
        
        if pattern:
            # 简单的通配符匹配
            pattern = pattern.replace('*', '.*').replace('?', '.')
            regex = re.compile(pattern)
            filtered_keys = [key for key in all_keys if regex.match(key)]
            self.operations.append(f"LIST {pattern} -> {len(filtered_keys)} keys")
            return filtered_keys
        else:
            self.operations.append(f"LIST ALL -> {len(all_keys)} keys")
            return all_keys
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        result = pub_get(key) is not None
        self.operations.append(f"EXISTS {key} -> {result}")
        return result
    
    def delete(self, key: str) -> bool:
        """删除entry"""
        try:
            pub_table = Table.of("PUB")
            if hasattr(pub_table, 'inner') and key in pub_table.inner:
                del pub_table.inner[key]
                self.operations.append(f"DELETE {key}")
                return True
            else:
                self.operations.append(f"DELETE {key} NOT_FOUND")
                return False
        except Exception as e:
            self.operations.append(f"DELETE {key} FAILED: {e}")
            return False
    
    def copy(self, from_key: str, to_key: str) -> bool:
        """复制entry"""
        try:
            source = self.get(from_key)
            if source and source.value.get("text"):
                result = self.set(to_key, source.value.get("text", ""), source.mime)
                if result:
                    self.operations.append(f"COPY {from_key} -> {to_key}")
                return result
            else:
                self.operations.append(f"COPY {from_key} -> {to_key} FAILED: source not found")
                return False
        except Exception as e:
            self.operations.append(f"COPY {from_key} -> {to_key} FAILED: {e}")
            return False


class Exec:
    """执行用户脚本的Port - 只能操作数据库entry"""
    
    @staticmethod
    def access(pack) -> FinalVis:
        """主访问方法"""
        op = first_valid(pack.query.get("op", None), "run")
        
        if op == "run":
            return Exec.run_script(pack)
        else:
            return Exec.get_script(pack)
    
    @staticmethod
    def get_script(pack) -> FinalVis:
        """获取脚本内容（API模式）"""
        script_entry = pub_get(pack.entry)
        if isinstance(script_entry, entry):
            script_content = script_entry.value.get("text", "")
        elif isinstance(script_entry, dict):
            script_content = script_entry.get("text", "")
        else:
            script_content = str(script_entry or "")
        
        return FinalVis.of("text", {
            "script": script_content,
            "type": "python",
            "description": "Database manipulation script"
        }, skip=True)
    
    @staticmethod
    def run_script(pack) -> FinalVis:
        """执行用户脚本"""
        try:
            # 获取脚本内容
            script_content = first_valid(pack.query.get('script', None), "")
            if not script_content:
                # 从entry中获取脚本
                script_entry = pub_get(pack.entry)
                if isinstance(script_entry, entry):
                    script_content = script_entry.value.get("text", "")
                elif isinstance(script_entry, dict):
                    script_content = script_entry.get("text", "")
                else:
                    script_content = str(script_entry or "")
            
            if not script_content.strip():
                return FinalVis.of("text", {
                    "success": False,
                    "error": "No script content provided",
                    "output": "",
                    "operations": []
                }, skip=True)
            
            # 创建安全的执行环境
            db_api = DatabaseAPI()
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
            
            # 捕获输出
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                # 执行用户脚本
                exec(script_content, safe_globals, {})
                output = captured_output.getvalue()
                
                return FinalVis.of("text", {
                    "success": True,
                    "output": output,
                    "operations": db_api.operations,
                    "operations_count": len(db_api.operations)
                }, skip=True)
                
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return FinalVis.of("text", {
                "success": False,
                "error": str(e),
                "output": captured_output.getvalue() if 'captured_output' in locals() else "",
                "operations": db_api.operations if 'db_api' in locals() else []
            }, skip=True)
