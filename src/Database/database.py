class Entry:
    value='aef'
    def toString(self):
        return self.value
    def to_dict(self ):
        return {"p":23}
    __dict__={"p":24}

pubdb={
    "":{"public":True,"pagetype":"text","value":"欢迎访问首页"},  # 根路径的默认条目
    "a":"234|b\np",
    "danshi":"oh wo ai ni",
    "escape":Entry()
}
hiddb={
    
}
MIMEs={

}