from protocol.types import File
tables={}

class Table:
    def __init__(self, string):
        self.inner = {}
        self.name = string
        tables[string] = self
    
    @staticmethod
    def of(string):
        if string in tables:
            return tables[string]
        else:
            return Table(string)
    def get(self, key, otherwise=None):
        return self.inner.get(key, otherwise)
    
    def set(self, key, value):
        self.inner[key] = value
    
    def __getitem__(self, key):
        return self.get(key, None)
    
    def __setitem__(self, key, value):
        self.set(key, value)
def pub_get(entry):
    """获取公共条目"""
    pub_table = Table.of("PUB")
    return pub_table.get(entry, None)

def pub_set(entry, value):
    """设置公共条目"""
    pub_table = Table.of("PUB")
    return pub_table.set(entry, value)

def hid_set(entry, value):
    """设置私有条目"""
    hid_table = Table.of("HID")
    return hid_table.set(entry, value)

def hid_get(entry):
    """获取私有条目"""
    hid_table = Table.of("HID")
    return hid_table.get(entry, None)
def claim(path,mime):
    """声明MIME类型"""
    mime_table = Table.of("MIME")
    if mime_table.get(path) is None:
        mime_table.set(path, mime)
        return True
    else:
        return False

def getmime(path):
    """获取MIME类型"""
    mime_table = Table.of("MIME")
    return mime_table.get(path, None)

from datetime import datetime
Table.of("PUB").set("a",File(mime="text", value={"text": "234|b\np", "lastSavedTime": datetime.now()}))

# Gen 测试模板
Table.of("PUB").set("test_gen", File(mime="gen", value={
    "text": "你好[世界|朋友|同志]！今天天气[真|很|超级]{好|不错|棒}呢。",
    "lastSavedTime": datetime.now()
}))

Table.of("PUB").set("greeting", File(mime="gen", value={
    "text": "{早上|中午|晚上}好啊，[很|非常|特别][开心|高兴|愉快]见到你！",
    "lastSavedTime": datetime.now()
}))