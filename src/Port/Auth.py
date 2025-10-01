#auth不单是某个某个用户，也可以是分配的使用额度
#比如，某个密钥只能使用一次，或着在某个时间段可用
#这些都需要分发
#更甚者，auth可能有表里多层，一个账号根据密码情况对应两种用户权限
class User:
    hash:str
    keys:list[Tuple[str,datetime.datetime]]
    expired_keys:list[Tuple[str,datetime.datetime]]
def authInPack(pack:Pack):
    #在这里提取使用的auth的信息
    if pack.query["useAuth"] :
        pass
    else:
        pass