from .database import pubdb,hiddb,MIMEs
def get(path):
    return {"value":"nihao","pagetype":"text","useWeb":True}
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

tables={

}
class Table:
    inner={}
    def __init__(self,string):
        if string in tables:
            return tables[string]
        tables[string]=self
    def of(string):
        if string in tables:
            return tables[string]
        else:
            tables[string]=Table(string)
            return tables[string]
    def get(self,string,otherwise=None):
        return self.inner.get(string,otherwise)
    def set(self,string,value):
        self.inner[string]=value
    def __getitem__(self,string):
        return self.get(string,None)
    def __setitem__(self,string,value):
        self.set(string,value)