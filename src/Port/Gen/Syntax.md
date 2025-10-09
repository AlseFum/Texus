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
*这样的列表的类型是内建的Generator*
示例中无缩进的首行是`名字`，用于引用。
名字以特殊字符开头时，须使用引号包裹。当然不以特殊字符开头也可以用引号包裹。
``` 不需引号的实例
item with white space
    item3A
    item3B
1more
    perusona！
```
``` 必须引号
"#devil may cry"
```
### 多行合一
使用`\`表示转行而非新项
```
MultilineExample
    line1\
    line2#(1|2|3)
    line3
```
就会输出line1line22或者line3 
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

### 行内快速随机
```
Hello #(world|human|my life)!
```
`#(arg1|arg2|argN...)`也是随机列表，写起来更快，但不可用作其他地方
其定义会被定义在上一级中，作为匿名列表
可以嵌套
如果里面的值含有`|`，需要使用引号。这里面的引号会自动拆包
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
*计法可能更改*
*当前的`:`不会与变量部分的`:`混淆，因为不在一个地方*
### 使用其他item
```
item
    itemA
    itemB
item2
    #item 2
    #"item with white space" 2
```
上面两种写法都表示引用，在生成item2时会生成item的值插入进去。
其中没有引号的写法，其后第一个空格会被省略，因为其作为隔断使用。
有引号的写法表示引用那些用了空格或者特殊字符的。
*注意，如果某一行的内容不能在运行时确定，它将不能延申出子项*
*好吧不好说*

### 递归与引用深度
引用可以递归，但需要注意避免无限循环：
```
sentence
    $sentence and more
    done
```
系统会在递归深度超过一定上限时自动终止并报错。

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
如果需要保持一个结果，请使用变量
### 变量
变量被使用一般需要声明
```
$a : num = 114514
$b = "str"
$c : itemFoo
```
变量可以为数字，字符串变量，和生成结果。
变量可以被使用。未设置初值的会被设置初值。
如a默认为0，b默认为"，c默认为None
这里#item只是表示类型，实际上没有赋值。
要赋值得加上等于号之后的内容
可以加上const，once，等关键字
变量只在声明层级以及更深处有效
```
$d: const jack #o-lantern = ...
```
```
YetAnotherItem
    a is $a
    b is $b
    c is $c
```
上面即将变量值作为文本输出。其中c在被访问时如果没有赋初值，会显示为None
特别地，如果$var=item而不是$var:item,将会在每次$var时返回动态评估item的结果

### 保持引用一致性
如果想在同一次生成中保持引用结果一致，使用变量：
```
$person = #name
greeting
    $person meets $person
```
这样会生成"Alice meets Alice"而不是两个不同的名字。
```
greeting
    $person=#person meets $person
```
也可以这样，不过范围仅限于行内了

### 重复生成
使用 `#*n` 来重复生成内容：

```
list
    #*3item
```
简单重复3次item，整数后直接跟item名称即可。

### 控制次数
```
$count=3
greet
    #*[count]item
```

**带索引的重复**：
```
numbered
    #*3`第#i项：#item\n`
```
特殊变量 `#i` 在重复中表示当前索引（从1开始）。
### 表达式
变量可以参与数值运算和字符串拼接：
```
$x : num
$y : num
calculation
    #{x = 10}\
    #{y = 20}\
    Sum is #[x + y]\
    Product is #[x * y]
```
`#[expression]`用于计算表达式并输出结果。
**注意**：表达式内部是纯计算，不能对外界造成任何影响（不能包含赋值、副作用等）。

支持的运算符：
- 数值：`+`, `-`, `*`, `/`, `%`（取模）
- 比较：`>`, `<`, `>=`, `<=`, `==`, `!=`
- 逻辑：`and`, `or`, `not`
- 字符串：`+`（拼接）
### 动态权重：权重值可以使用表达式 `#[]` 动态计算
```
$importance : num
greeting
    Hello #(:#[$importance]:world|human|my life)!
$mood : num
story
    The hero feels #(:#[$mood * 2]:happy|:#[$mood]:sad|neutral)
```
这样可以根据变量值动态调整选项的权重。权重表达式会在生成时计算，支持所有数值运算。
### 条件语句
使用`?:`三元运算符或条件块：
```
$score : num
grade
    Your score is $score
    #[$score >= 90 ? "优秀" : "继续努力"]
```
### 内建变量
这些变量是内部设置（用户，系统）而非生成的
1. URL里query设置了的
2. 一些系统常量，用户localstorage或者cookie里的
（现在先留空）
## 之后的都不一定被实现
### 副作用与赋值
副作用允许在生成过程中修改变量值，使用`#{}`语法包裹。
```
$count : num
item
    Hello #{$count = $count + 1}\
    You are visitor number $count
```
多个副作用可以连续执行：
```
$a : num
$b : num
complex
    #{$a = 5}#{$b = 10} Result: $a and $b
```
副作用不会输出任何文本，只改变状态。

**特别地**，可以在行中任意位置进行赋值：
```
$mood = "happy"
story
    The hero #{$mood = "angry"} started fighting.\
    He was very $mood during the battle.
```
赋值操作可以穿插在文本中，不影响输出，但会改变后续的变量值。

### 列表和数组 不一定支持
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
    #*len($names){$names[#i - 1]\n}
```

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

乃至于其他操作（类型自建转化？）

> 可以看到#合$在这时起到一个generate的语义（？


#### 声明模式匹配
使用 `#match` 为开头的行，之后算做一个模式匹配器
分支就是条件1，条件2 =》返回值，这样的
十分类似Rust
因为比较好写吧
这个可以做到后处理那

#### 自定义#宏
这个就得自行编辑python代码了


#### 数域枚举
以一个数字范围为基础，设置其中的一些项为特殊对应
比如Color 1=red 2=green 3=blue, 最小的4-255都没用上，就可以4-255=unknown
然后除了数字固有的add，sub，还可以设置一些变换，来在域里变换。
特别地，与字符串比较时，会匹配枚举值。
#### 首行作用
```
MyItem
    #before
        $a=4
        $c=$a+$b
    #[$a+$c]
    None
```
#开头的都有特殊作用
这个会在进入MyItem时立刻进行，之后再计算概率，进入分支

#### 函数
类shell吧，可以声明一些特殊的函数
