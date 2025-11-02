from typing import Optional
from Common.types import FinalVis, entry
from Database import Table, pub_get, pub_set

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
        # 1. 从 pub 表获取内容
        pub_data = pub_get(pack.entry)
        if pub_data is None:
            return FinalVis.of("raw", "(empty)")
        
        # 统一转换为 entry 格式
        if isinstance(pub_data, entry):
            pub_file = pub_data
        elif isinstance(pub_data, dict):
            pub_file = entry(mime="text", value=pub_data)
        else:
            pub_file = entry(mime="text", value={"text": str(pub_data)})
            # 如果是原始数据，保存为entry对象
            pub_set(pack.entry, pub_file)
        
        pub_timestamp = pub_file.value.get("lastSavedTime")
        
        # 2. 检查 gen 表缓存
        gen_table = Table.of("GEN")
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
                return FinalVis.of("raw", f"Error: {e}")
        
        # 5. 生成内容并输出
        result = genfile.gen()
        is_api = getattr(pack, 'by', '') == 'api'
        return FinalVis.of("raw", str(result), skip=is_api)

