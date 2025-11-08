from Common.base import entry

class GenFile(entry):
    def __init__(self, value, root=None):
        self.root = root
        super().__init__(mime="gen", value=value)
    
    def to_dict(self):
        """重写 to_dict 方法，处理 GenFile 的特殊逻辑"""
        base_dict = super().to_dict()
        
        if self.root is not None:
            # 调用 generator 生成文本
            generated_text = self.root.gen()
            base_dict["value"] = {
                "text": generated_text,
                "lastSavedTime": self._value.get("lastSavedTime"),
                "sourceTimestamp": self._value.get("sourceTimestamp")
            }
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建 GenFile 对象"""
        if not isinstance(data, dict):
            raise ValueError("数据必须是字典格式")
        
        # 创建基础 entry 对象
        base_entry = super(GenFile, cls).from_dict(data)
        
        # 创建 GenFile 实例
        instance = cls(
            value=base_entry._value,
            root=None  # root 需要单独处理，因为它是 Generator 对象
        )
        
        # 复制其他属性
        instance.lastModifiedTime = base_entry.lastModifiedTime
        
        return instance
    
    def gen(self, seed=None):
        """生成内容"""
        if self.root is not None:
            return self.root.gen(seed)
        return None

