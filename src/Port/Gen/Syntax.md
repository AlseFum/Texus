这个文档讲generator的文法

### 基础结构
使用缩进表示层级结构和随机选择。子项会从同一缩进级别中**随机选择一个**：
```
item
    itemA
    itemB
item2
    item2A
    item2B
```
表明可能会从item或者item2取值，就是是其下的itemA/B,item2A/B
最终可能生成 itemA,itemB,item2A,item2B其中任一
### 行内快速随机
```
Hello #(world|human|my life)!
```
`#(arg1|arg2|argN...)`也是随机列表，写起来更快，但不可用作其他地方
可以嵌套
### 不均等权重
```
item
    itemA
    :2:itemB
```
```
Hello #(:2:world|human|my life)!
```
上面的计法都表明权重被更改了，数字即表示占用原来多少份的概率

**动态权重**：权重值可以使用表达式 `#[]` 动态计算
```
$importance : num
greeting
    Hello #(:#[$importance]:world|human|my life)!
```
这样可以根据变量值动态调整选项的权重。例如：
```
$mood : num
story
    The hero feels #(:#[$mood * 2]:happy|:#[$mood]:sad|neutral)
```
权重表达式会在生成时计算，支持所有数值运算。
### 使用其他item
```
item
    itemA
    itemB
item2
    #item 2
    #"item" 2
```
上面两种写法都表示引用item，在生成item2时会生成item的值插入进去。
其中没有引号的写法，其后第一个空格会被省略，因为其作为隔断使用。
*注意，如果某一行的内容不能在运行时确定，它将不能延申出子项*
*好吧不好说*
### 变量
变量被使用一般需要声明
```
$a : num
$b = "str"
$c : $item
```
变量可以为数字，字符串变量，和生成结果。
变量可以被使用。未设置初值的会被设置初值。
如a默认为0，b默认为"，c默认为None
这里$item只是表示类型，实际上没有赋值。
要赋值得#item
在$~~之前，可以加上const，once，等关键字
```
$d: const jack $o-lantern = #balabala
```
```
YetAnotherItem
    a is $a
    b is $b
    c is $c
```
上面即将变量值作为文本输出。其中c在被访问时如果没有赋初值，会显示为None
### 副作用与赋值
副作用允许在生成过程中修改变量值，使用`#{}`语法包裹。
```
$count : num
item
    Hello #{$count = $count + 1}
    You are visitor number $count
```
多个副作用可以连续执行：
```
$a : num
$b : num
complex
    #{$a = 5}#{$b = 10}Result: $a and $b
```
副作用不会输出任何文本，只改变状态。

**特别地**，可以在行中任意位置进行赋值：
```
$mood = "happy"
story
    The hero #{$mood = "angry"} started fighting.
    He was very $mood during the battle.
```
上面会输出"The hero  started fighting."（注意赋值处为空）和"He was very angry during the battle."。赋值操作可以穿插在文本中，不影响输出，但会改变后续的变量值。

**注意**：前缀和后缀的区别在于，如果副作用中有输出（虽然通常不建议），`$count++` 先输出原值再加1，`++$count` 先加1再输出新值。但因为 `#{}` 不输出内容，两者在大多数情况下效果相同。

### 表达式
变量可以参与数值运算和字符串拼接：
```
$x : num
$y : num
calculation
    #{$x = 10}
    #{$y = 20}
    Sum is #[$x + $y]
    Product is #[$x * $y]
```
`#[expression]`用于计算表达式并输出结果。**注意**：表达式内部是纯计算，不能对外界造成任何影响（不能包含赋值、副作用等）。

支持的运算符：
- 数值：`+`, `-`, `*`, `/`, `%`（取模）
- 比较：`>`, `<`, `>=`, `<=`, `==`, `!=`
- 逻辑：`and`, `or`, `not`
- 字符串：`+`（拼接）

### 条件语句
使用`?:`三元运算符或条件块：
```
$score : num
grade
    Your score is $score
    #[$score >= 90 ? "优秀" : "继续努力"]
```
使用条件块（更复杂的情况）：
```
$hp : num
status
    ?if $hp > 80
        角色状态良好
    ?elif $hp > 50
        角色受了轻伤
    ?elif $hp > 20
        角色受了重伤
    ?else
        角色濒临死亡
```

### 递归与引用深度
引用可以递归，但需要注意避免无限循环：
```
sentence
    $sentence and more
    done
```
系统会在递归深度超过100时自动终止并报错。

### 多重引用与组合
可以在一行中多次引用：
```
name
    Alice
    Bob
    Charlie
greeting
    $name meets $name
```
上面可能生成"Alice meets Bob"等组合。每次引用都会重新生成。

### 保持引用一致性
如果想在同一次生成中保持引用结果一致，使用变量：
```
$person = #name
greeting
    $person meets $person
```
这样会生成"Alice meets Alice"而不是两个不同的名字。

### 注释
使用`//`开始单行注释：
```
item
    // 这是注释
    itemA  // 行尾注释
    itemB
```
多行注释使用`/* */`：
```
/*
这是多行注释
可以跨越多行
*/
item
    value
```

### 空值与可选内容
使用空字符串表示"可能什么都不生成"：
```
optional
    something
    
    another thing
```
上面第二行为空，表示有概率不输出任何内容。

### 转义字符
特殊字符需要转义：
- `\$` - 字面美元符号
- `\#` - 字面井号
- `\[` `\]` - 字面方括号
- `\\` - 字面反斜杠

```
price
    The price is \$#[$amount]
```

### 内置函数
表达式中可以使用内置函数：

**数学函数**：
- `round(n)` - 四舍五入
- `floor(n)` - 向下取整
- `ceil(n)` - 向上取整
- `abs(n)` - 绝对值
- `min(a, b)` - 最小值
- `max(a, b)` - 最大值
- `pow(a, b)` - a的b次方

**随机函数**：
- `rand(min, max)` - 生成[min, max]之间的随机浮点数
- `randint(min, max)` - 生成[min, max]之间的随机整数
- `dice(n)` - 生成1到n之间的随机整数（骰子）

**字符串函数**：
- `upper(str)` - 转大写
- `lower(str)` - 转小写
- `len(str)` - 字符串长度
- `substr(str, start, length)` - 截取子字符串

示例：
```
$damage = #[rand(10.5, 20.8)]
$diceRoll = #[dice(6)]
battle
    造成了#[round($damage)]点伤害
    骰子点数：$diceRoll
    伤害范围：#[min(5, $damage)] ~ #[max(5, $damage)]
```

### 重复生成
使用 `@n` 或 `@n{...}` 重复生成内容：

**基础重复**：
```
items
    @3:#item
```
重复生成3次item（每次独立随机）。

**带分隔符的重复**：
```
list
    @3{#item, }
```
生成3个item，用逗号和空格分隔。输出如：`itemA, itemB, itemC`

**使用变量控制次数**：
```
$count : num
list
    #{$count = 5}
    @$count{- #item\n}
```
生成5行，每行格式为"- item名称"。

**带索引的重复**：
```
numbered
    @3{第#i项：#item\n}
```
特殊变量 `#i` 在重复中表示当前索引（从1开始）。

### 序列生成
使用特殊标记 `<>` 表示按顺序拼接所有子项（而不是随机选择）：

```
fullStory
    <>开头
        从前有座山
    <>中间
        山里有座庙
    <>结尾
        庙里有个和尚
```
生成时会按顺序拼接：`从前有座山山里有座庙庙里有个和尚`

也可以在子项前加 `>` 标记：
```
story
    >第一部分
    >第二部分
    >第三部分
```
会按顺序生成所有标记了 `>` 的项。

### 变量作用域
**全局变量**：在顶层声明的变量，整个生成过程中都可访问。
```
$globalVar = 1
```

**局部变量**：在item内部声明的变量，只在该item及其子项中有效。
```
item1
    $localVar = 2  // 只在item1内有效
    Value: $localVar
```

**作用域规则**：
- 子项可以访问父级的所有变量
- 同名变量会覆盖外层变量（仅在当前作用域）
- 副作用修改的是最近作用域的变量

### 列表和数组
声明和使用列表：

**列表声明**：
```
$names = ["Alice", "Bob", "Charlie"]
$scores = [85, 90, 75]
$empty = []
```

**访问元素**：
```
test
    第一个名字：$names[0]
    第二个分数：$scores[1]
    随机名字：$names[#[randint(0, 2)]]
```

**列表操作**：
- `#[len($names)]` - 获取长度
- `$names[#[len($names) - 1]]` - 获取最后一个元素
- `#{$names.append("David")}` - 添加元素（副作用）
- `#{$names.pop()}` - 移除最后一个元素

**遍历列表**：
```
allNames
    @len($names){$names[#i - 1]\n}
```

### 格式控制
特殊转义序列用于控制输出格式：

- `\n` - 换行符
- `\t` - 制表符
- `\s` - 空格（用于需要明确空格时）
- `\\` - 反斜杠本身

```
poem
    第一行\n第二行\n\t缩进的第三行
```

**首尾空格保留**：
```
item
    \s\s有前导空格
    有尾随空格\s\s
```

### 条件选项简写
在 `#()` 行内随机中，可以使用条件表达式：

**条件选项**：
```
$hp : num
status
    #($hp > 80 : 健康 | $hp > 50 : 受伤 | $hp > 20 : 虚弱 | ?? : 濒死)
```
语法：`条件 : 内容`，每个条件按顺序检查，第一个为真的会被选中。`??` 表示默认选项（所有条件都不满足时）。

**与权重结合**：
```
$mood : num
feeling
    #($mood > 5 : :2:很开心 | $mood > 0 : 还行 | ?? : 不太好)
```

### 宏定义
定义可复用的文本片段：

```
@macro greet(name)
    你好，$name！欢迎光临。

welcome
    @greet("张三")
    @greet($userName)
```

宏支持参数，可以像函数一样调用。

### 引用时的后处理
引用item或变量时可以应用后处理：

```
name
    alice
    bob

story
    $name|upper 说："你好！"
    #name|upper 回答道："嗨！"
```
生成：`ALICE 说："你好！"` 或 `BOB 回答道："嗨！"`

**支持的后处理**：
- `|upper` - 转大写
- `|lower` - 转小写
- `|title` - 首字母大写
- `|reverse` - 反转字符串
- `|trim` - 去除首尾空格

### 完整示例
```
// 角色生成器
$hp = #[50 + #dice * 10]
$name = #names
$weapon = #weapons

// 基础数据
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
    角色名称: $name
    生命值: $hp
    武器: $weapon
    状态: #[$hp > 70 ? "优秀" : "一般"]
    
story
    $character踏上了冒险之旅。
    #(他|她|它)手持$weapon，准备迎接挑战。
```

### 最佳实践
1. **变量命名**：使用有意义的变量名，如`$playerName`而不是`$x`
2. **适度使用权重**：过度使用权重会使生成结果失去随机性
3. **避免深层嵌套**：超过3-4层的引用会降低可读性
4. **善用注释**：为复杂的生成逻辑添加说明
5. **测试边界情况**：确保变量初始化和条件覆盖所有情况

#### 声明模式匹配
使用 `#match` 为开头的行，之后算做一个模式匹配器
分支就是条件1，条件2 =》返回值，这样的
十分类似Rust
因为比较好写吧

#### 自定义#宏
这个就得自行编辑python代码了


#### 数域枚举
以一个数字范围为基础，设置其中的一些项为特殊对应
比如Color 1=red 2=green 3=blue, 最小的4-255都没用上，就可以4-255=unknown
然后除了数字固有的add，sub，还可以设置一些变换，来在域里变换。
特别地，与字符串比较时，会匹配枚举值。