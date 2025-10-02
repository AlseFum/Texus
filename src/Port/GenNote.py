import json
import sys
import os
from util import first_valid
from Database import pub_get, pub_set
from protocol.types import VisualContent
from datetime import datetime

class GenNote:
    def access(pack):
        string=pub_get(pack.entry)
        if string is None:
            string="(empty)"
        else:
            # 随机抽取一行显示
            lines = string.split('\n')
            if lines:
                import random
                string = random.choice(lines).strip()
                if not string:  # 如果选中的是空行，返回第一个非空行
                    for line in lines:
                        if line.strip():
                            string = line.strip()
                            break
                    else:
                        string = "(empty lines only)"
        return VisualContent.of("raw",string)