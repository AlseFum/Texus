"""Gen 模块测试用例

这个文件包含了各种 Gen 语法的测试用例。
可以通过调用 load_test_cases() 来加载所有测试用例到数据库。
"""

from protocol.types import entry
from datetime import datetime


def load_test_cases(pub_table):
    """加载所有测试用例到 PUB 表"""
    
    # 旧语法测试（向后兼容）
    pub_table.set("test_gen", entry(mime="gen", value={
        "text": "你好[世界|朋友|同志]！今天天气[真|很|超级]{好|不错|棒}呢。",
        "lastSavedTime": datetime.now()
    }))
    
    pub_table.set("greeting", entry(mime="gen", value={
        "text": "{早上|中午|晚上}好啊，[很|非常|特别][开心|高兴|愉快]见到你！",
        "lastSavedTime": datetime.now()
    }))
    
    # 新语法测试用例
    
    # 测试1: 基础缩进结构 + 权重
    pub_table.set("test_weight", entry(mime="gen", value={
        "text": """greeting
    你好
    :2:早安
    :3:晚上好
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试2: 变量声明和使用
    pub_table.set("test_variable", entry(mime="gen", value={
        "text": """$name = "艾莉丝"
$age : num
main
    我的名字是$name，年龄是$age岁。
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试3: 表达式计算 #[]
    pub_table.set("test_expression", entry(mime="gen", value={
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
    pub_table.set("test_side_effect", entry(mime="gen", value={
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
    pub_table.set("test_inline", entry(mime="gen", value={
        "text": """story
    英雄#(勇敢地|小心翼翼地|快速地)走进了森林。
    #(他|她)看到了一只#(老虎|狮子|熊)。
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试6: Item 引用
    pub_table.set("test_item_ref", entry(mime="gen", value={
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
    pub_table.set("test_dynamic_weight", entry(mime="gen", value={
        "text": """$mood : num
greeting
    #{$mood = 5}
    心情指数: $mood
    状态: #(#[$mood]:开心|#[$mood * 2]:难过|普通)
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试8: 条件语句（三元运算符）
    pub_table.set("test_conditional", entry(mime="gen", value={
        "text": """$score : num
result
    #{$score = 85}
    你的分数是: $score
    评价: #[$score >= 90 ? "优秀" : "继续努力"]
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试9: 复杂示例 - 角色生成器
    pub_table.set("test_character", entry(mime="gen", value={
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
    pub_table.set("test_consistency", entry(mime="gen", value={
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
    pub_table.set("test_recursive", entry(mime="gen", value={
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
    pub_table.set("test_optional", entry(mime="gen", value={
        "text": """optional
    有内容
    
    :2:另一个内容

main
    结果: #optional结束
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试13: 格式控制转义序列
    pub_table.set("test_escape", entry(mime="gen", value={
        "text": r"""poem
    第一行\n第二行\n\t缩进的第三行
    
price
    价格是 \$100
    
spacing
    \s\s前导空格
    尾随空格\s\s
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试14: 重复生成功能
    pub_table.set("test_repeat", entry(mime="gen", value={
        "text": """name
    Alice
    Bob
    Charlie

// 简单重复3次
simple
    #*3name, 

$count : num
// 表达式控制次数
dynamic
    #{$count = 5}
    重复$count次: #*[$count]name-

// 带索引的重复
numbered
    #*3`第$i项：#name\n`
""",
        "lastSavedTime": datetime.now()
    }))
    
    # 测试15: 综合测试 - 使用到条件语句前的所有功能
    pub_table.set("test_ultimate", entry(mime="gen", value={
        "text": r"""// 综合测试 - 使用所有已实现功能
// ========================================

/* 变量声明 */
$name = #names
$count : num
$hp : num

// 名字列表（权重）
names
    艾莉丝
    :2:鲍勃
    :3:查理

// 武器列表
weapon
    剑
    :2:法杖
    弓

// 简单列表
item
    物品A
    物品B
    物品C

// ========================================
// 测试：格式控制转义
// ========================================
format_test
    第一行\n第二行\n\t缩进内容
    价格：\$100\n空格：\s\s前导

// ========================================
// 测试：重复生成
// ========================================
repeat_test
    简单重复：#*3item\n
    #{$count = 4}\
    变量重复：#*[$count]weapon\n
    带索引：#*3`第$i项：#names\n`

// ========================================
// 测试：副作用和表达式
// ========================================
calc_test
    #{$hp = 100}\
    初始HP：$hp\n\
    #{$hp += 50}\
    增加后：$hp\n\
    #{$hp++}\
    自增后：$hp

// ========================================
// 测试：行内随机和动态权重
// ========================================
random_test
    英雄#(勇敢地|小心地|快速地)前进\n
    #{$count = 3}\
    权重测试：#(:#[$count]:高|:2:中|低)

// ========================================
// 主入口
// ========================================
main
    ══════════════════════════════\n\
    📝 Gen 综合功能测试\n\
    ══════════════════════════════\n\n\
    角色：$name\n\
    武器：#weapon\n\n\
    #format_test\n\n\
    #repeat_test\n\n\
    #calc_test\n\n\
    #random_test\n\n\
    /* 已测试功能：
       ✅ 缩进结构
       ✅ 权重（静态和动态）
       ✅ 变量声明和使用
       ✅ 表达式 #[]
       ✅ 副作用 #{}
       ✅ 行内随机 #()
       ✅ Item引用
       ✅ 格式转义 \n \t \s
       ✅ 字符转义 \$ \#
       ✅ 重复生成 #*n #*[expr]
       ✅ 索引变量 $i
       ✅ 注释 // 和 /* */
    */
""",
        "lastSavedTime": datetime.now()
    }))
    
    print(f"✓ 已加载 {15} 个 Gen 测试用例")

