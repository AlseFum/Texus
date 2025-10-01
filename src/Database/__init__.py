from .database import pubdb,hiddb,MIMEs
def get(path):
    return {"value":"nihao","pagetype":"text","useWeb":True}
def pub_get(entry):
    if entry in pubdb:
        return pubdb[entry]
    else:
        # 如果条目不存在，返回默认值或抛出友好错误
        return None
def pub_set(entry,value):
    pubdb[entry]=value
    return True
def hid_set(entry,value):
    hiddb[entry]=value
    return True
def hid_get(entry):
    if entry in hiddb:
        return hiddb[entry]
    else:
        return None
def claim(path,mime):
    if MIMEs.get(path,None) is None:
        MIMEs[path]=mime
        return True
    else:
         return False
def getmime(path):
    return MIMEs.get(path,None)