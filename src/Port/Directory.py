from termios import VINTR
from protocol.types import VisualContent, Medium, PathAnalysis

class Directory:
    def access(pack):
        """this is to pass as a part of pipe"""
        v = VisualContent()
        v.skip = True
        v.value = {
            "success": False,
            "message": "文件夹功能暂时不可用"
        }
    
    def pipeline(pack):
        """处理路径继续访问，只用于需要后续处理的状态"""
        # 使用 pack 中的 path_analysis
        path_analysis = pack.path_analysis
        
        # 如果路径为空或只有一个 entry，返回 None 表示不需要后续处理
        if path_analysis.is_empty or len(path_analysis.entries) <= 1:
            return None
        
        # 如果有子路径，返回 Medium 以便继续访问
        remaining_path = path_analysis.remaining_path
        
        # 尝试确定子路径的 MIME 类型
        sub_entry = path_analysis.get_entry_at(1) if path_analysis.has_subpath() else ""
        sub_mime = Directory.detect_mime_type(sub_entry)
        
        return Medium.of(
            data={
                "type": "directory", 
                "path": pack.path,
                "path_analysis": path_analysis.to_dict()
            },
            mime=sub_mime,
            path=remaining_path,
            pack=pack
        )
    
    def detect_mime_type(filename):
        """检测文件类型"""
        if "." in filename:
            ext = filename.split(".")[-1].lower()
            if ext in ["txt", "md", "text"]:
                return "text"
            elif ext in ["json", "xml", "yaml", "yml"]:
                return "raw"
            else:
                return "note"
        else:
            # 没有扩展名，可能是目录或笔记
            return "dir"  # 假设是目录，让系统继续尝试
    
    def info(pack):
        """this is to show the info of the directory"""
        return VisualContent.of("raw","This is a directory")