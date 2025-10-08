"""Gen 模块测试用例

这个文件包含了各种 Gen 语法的测试用例。
可以通过调用 load_test_cases() 来加载所有测试用例到数据库。
"""

from protocol.types import File
from datetime import datetime


def load_test_cases(pub_table):
    """加载所有测试用例到 PUB 表"""
    
    # 旧语法测试（向后兼容）
    pub_table.set("test_gen", File(mime="gen", value={
        "text": "你好[世界|朋友|同志]！今天天气[真|很|超级]{好|不错|棒}呢。",
        "lastSavedTime": datetime.now()
    }))
    
    pub_table.set("greeting", File(mime="gen", value={
        "text": "{早上|中午|晚上}好啊，[很|非常|特别][开心|高兴|愉快]见到你！",
        "lastSavedTime": datetime.now()
    }))
    
    # 新语法测试用例
    
    # 测试1: 基础缩进结构 + 权重
    pub_table.set("test_weight", File(mime="gen", value={
        "text": """greeting
    你好
    :2:早安
    :3:晚上好
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试2: 变量声明和使用
    pub_table.set("test_variable", File(mime="gen", value={
        "text": """$name = "艾莉丝"
$age : num
main
    我的名字是$name，年龄是$age岁。
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试3: 表达式计算 #[]
    pub_table.set("test_expression", File(mime="gen", value={
        "text": """$x : num
$y : num
calc
    #{$x = 10}#{$y = 20}
    $x + $y = #[$x + $y]
    $x * $y = #[$x * $y]
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试4: 副作用 #{} 和简写运算符
    pub_table.set("test_side_effect", File(mime="gen", value={
        "text": """$count : num
counter
    开始计数: $count
    #{$count++}第一次: $count
    #{$count++}第二次: $count
    #{$count += 10}加10后: $count
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试5: 行内快速随机 #()
    pub_table.set("test_inline", File(mime="gen", value={
        "text": """story
    英雄#(勇敢地|小心翼翼地|快速地)走进了森林。
    #(他|她)看到了一只#(老虎|狮子|熊)。
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试6: Item 引用
    pub_table.set("test_item_ref", File(mime="gen", value={
        "text": """name
    艾莉丝
    鲍勃
    查理

weapon
    长剑
    法杖
    弓箭

character
    角色: #name
    武器: #weapon
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试7: 动态权重
    pub_table.set("test_dynamic_weight", File(mime="gen", value={
        "text": """$mood : num
greeting
    #{$mood = 5}
    心情指数: $mood
    状态: #(#[$mood]:开心|#[$mood * 2]:难过|普通)
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试8: 条件语句（三元运算符）
    pub_table.set("test_conditional", File(mime="gen", value={
        "text": """$score : num
result
    #{$score = 85}
    你的分数是: $score
    评价: #[$score >= 90 ? "优秀" : "继续努力"]
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试9: 复杂示例 - 角色生成器
    pub_table.set("test_character", File(mime="gen", value={
        "text": """// 角色生成器
$hp : num
$name = #names
$weapon = #weapons

dice
    1
    2
    3
    :2:4
    :2:5
    6

names
    艾莉丝
    鲍勃
    :3:查理

weapons
    长剑
    法杖
    弓箭

character
    #{$hp = #[50 + #dice * 10]}
    ===角色卡===
    名字: $name
    生命值: $hp
    武器: $weapon
    状态: #[$hp > 70 ? "优秀" : "一般"]

story
    #character
    
    $name踏上了冒险之旅。
    #(他|她|它)手持$weapon，准备迎接挑战。
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试10: 多重引用与一致性
    pub_table.set("test_consistency", File(mime="gen", value={
        "text": """name
    Alice
    Bob
    Charlie

// 每次引用都会重新生成
different
    #name meets #name

// 使用变量保持一致
$person = #name
same
    $person meets $person
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试11: 递归和副作用组合
    pub_table.set("test_recursive", File(mime="gen", value={
        "text": """$step : num

action
    跑步
    跳跃
    攻击

sequence
    #{$step++}步骤$step: #action
    #{$step++}步骤$step: #action
    #{$step++}步骤$step: #action
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试12: 空值和可选内容
    pub_table.set("test_optional", File(mime="gen", value={
        "text": """optional
    有内容
    
    :2:另一个内容

main
    结果: #optional结束
""",
        "lastSavedTime": datetime.now()
    }))
    
    print(f"✓ 已加载 {13} 个 Gen 测试用例")

