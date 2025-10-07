import random

class Generator:
    """生成器核心类
    
    支持两种生成器类型：
    - PlainList: 顺序拼接所有元素
    - Roulette: 随机选择其中一个元素
    """
    PlainList = "PlainList"
    Roulette = "Roulette"
    
    def __init__(self, type, thing):
        self.type = type
        self.thing = thing
    
    def gen(self, seed=None):
        """生成内容
        
        Args:
            seed: 随机种子（用于 Roulette 类型）
            
        Returns:
            生成的字符串内容
        """
        if self.type == self.PlainList:
            result = []
            for item in self.thing:
                if isinstance(item, Generator):
                    result.append(str(item.gen(seed)))
                else:
                    result.append(str(item))
            return ''.join(result)
        elif self.type == self.Roulette:
            seed = random.randint(0, len(self.thing) - 1)
            item = self.thing[seed]
            # 如果选中的是生成器，递归生成
            if isinstance(item, Generator):
                return item.gen()
            return str(item)
        return self.thing

