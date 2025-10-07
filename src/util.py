def first_valid(*args):
    """
    返回参数列表中第一个有效（非 None）的值
    
    Args:
        *args: 不定长参数
    
    Returns:
        第一个非 None 的值，如果所有值都是 None 则返回 None
    
    Example:
        >>> first_valid(None, "", "hello")
        ""
        >>> first_valid(None, None, "world")
        "world"
        >>> first_valid(None, None, None)
        None
    """
    for arg in args:
        if arg is not None:
            return arg
    return None
def first_avail(*args):
    for arg in args:
        if arg is not None and arg is not "":
            return arg
    return None