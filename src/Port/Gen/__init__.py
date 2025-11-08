from typing import Optional
from Common.base import FinalVis, entry
from Database import Table

from .generator import Generator
from .parser import Parser, ParseError
from .file import GenFile

# 导出公共接口
__all__ = ['Gen', 'Generator', 'Parser', 'ParseError', 'GenFile']


class Gen:
    """生成器 Port - 从 pub 表读取内容并生成随机文本
    
    使用 gen 表缓存解析后的 Generator 对象，根据时间戳判断是否需要重新解析
    """
    
    @staticmethod
    def access(pack) -> FinalVis:
        """主访问方法"""
        main_table = Table.of("main")
        gen_table = Table.of("GEN")
        
        # 1. 从主表获取内容
        data = main_table.get(pack.entry)
        if data is None:
            return FinalVis.of("raw", payload={"text": "(empty)"})
        
        # 统一转换为 entry 格式
        if isinstance(data, entry):
            pub_file = data
        elif isinstance(data, dict):
            pub_file = entry(mime="text", value=data)
        else:
            pub_file = entry(mime="text", value={"text": str(data)})
            # 如果是原始数据，保存为entry对象
            main_table.set(pack.entry, pub_file)
        
        pub_timestamp = pub_file.value.get("lastSavedTime")
        
        # 2. 检查 gen 表缓存
        cached_genfile = gen_table.get(pack.entry)
        genfile = None
        
        # 3. 判断缓存是否有效
        if isinstance(cached_genfile, GenFile):
            cached_timestamp = cached_genfile.value.get("sourceTimestamp")
            if cached_timestamp == pub_timestamp and cached_genfile.root is not None:
                genfile = cached_genfile
        
        # 4. 如果需要，重新解析
        if genfile is None:
            try:
                genfile = Parser(pub_file).parse()
                gen_table.set(pack.entry, genfile)
            except Exception as e:
                return FinalVis.of("raw", payload={"text": f"Error: {e}"})
        
        # 5. 生成内容并输出
        result = genfile.gen()
        is_api = getattr(pack, 'by', '') == 'api'
        result_str = str(result)
        if is_api:
            # API请求：只需要value
            return FinalVis.of("raw", value=result_str, skip=True)
        else:
            # Web请求：只需要payload
            return FinalVis.of("raw", payload={"text": result_str})

# 插件注册函数
def registry():
    return {
        "mime": "gen",
        "port": Gen
    }

