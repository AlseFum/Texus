from protocol.types import File

class GenFile(File):
    def __init__(self, value, root=None):
        self.root = root
        super().__init__(mime="gen", value=value)
    
    def to_dict(self):
        if self.root is not None:
            # 调用 generator 生成文本
            generated_text = self.root.gen()
            return {
                "text": generated_text,
                "lastSavedTime": self._value.get("lastSavedTime")
            }
        return self._value
    
    def gen(self, seed=None):
        return self.root.gen(seed)

