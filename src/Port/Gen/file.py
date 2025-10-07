from protocol.types import File

class GenFile(File):
    """生成器文件类型
    
    继承自 File，专门用于存储生成器内容
    如果 value 中包含 root (generator)，会调用它来生成文本
    """
    def __init__(self, value, root=None):
        """
        Args:
            value: 文件内容（字典格式）
            root: Generator 对象，如果提供则用于生成文本
        """
        self.root = root
        super().__init__(mime="gen", value=value)
    
    def to_dict(self):
        """转换为字典格式
        
        如果有 root (generator)，调用它生成文本并返回
        """
        if self.root is not None:
            # 调用 generator 生成文本
            generated_text = self.root.gen()
            return {
                "text": generated_text,
                "template": self._value.get("template", ""),
                "lastSavedTime": self._value.get("lastSavedTime")
            }
        return self._value
    
    def gen(self, seed=None):
        """生成文本
        
        Args:
            seed: 随机种子
            
        Returns:
            生成的文本字符串
        """
        if self.root is not None:
            return self.root.gen(seed)
        # 如果没有 root，返回原始文本
        return self._value.get("text", "")

