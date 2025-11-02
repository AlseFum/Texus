# 入门指南

## 项目结构

```
texus/
├── src/
│   ├── Common/          # 通用模块（类型定义、脚本执行）
│   ├── Database/        # 数据库模块（存储、备份）
│   ├── Express/         # 表达层（Web 界面、模板）
│   ├── Port/            # 端口层（Text, Exec, Gen, Meta, Timer）
│   ├── server/          # 服务器（FastAPI 应用）
│   └── util.py          # 工具函数
├── backup/              # 备份目录
├── pyproject.toml       # 项目配置
├── start.sh            # 启动脚本
└── README.md            # 本文档
```

## 基本概念

### Port 系统

Port 是处理特定类型请求的处理器，系统根据 MIME 类型自动分发到相应的 Port：

- **Text Port**: 处理文本数据（默认）
- **Exec Port (py)**: 执行 Python 脚本
- **Gen Port**: 生成随机内容
- **Meta Port**: 执行 Meta 脚本
- **Timer Port**: 管理定时任务

### Entry 和 MIME 类型

- **Entry**: 数据库中的数据条目，通过路径访问
- **MIME 类型**: 通过文件扩展名或显式声明确定，例如：
  - `.text` 或 `text` → Text Port
  - `.py` 或 `py` → Exec Port
  - `.gen` 或 `gen` → Gen Port
  - `.meta` 或 `meta` → Meta Port
  - `.timer` 或 `timer` → Timer Port

## 第一个文本文件

1. **创建文本**（使用 Web 界面）:
   - 访问 `http://localhost:7123/myfile`
   - 在编辑器中输入内容
   - 点击保存

2. **通过 API 创建**:
   ```bash
   curl -X POST "http://localhost:7123/myfile?op=set&content=Hello%20World"
   ```

3. **读取文本**:
   ```bash
   curl http://localhost:7123/myfile
   ```

## 第一个脚本

1. **创建脚本文件** `test.py`:
   ```python
   db.set("message", "Hello from script!")
   print(db.get("message"))
   ```

2. **通过 Web 创建**:
   - 访问 `http://localhost:7123/test.py`
   - 输入上面的脚本代码
   - 保存并访问以执行

3. **执行脚本**:
   ```bash
   curl http://localhost:7123/test.py
   ```

## 下一步

- 查看 [教程](tutorial.md) 学习更多功能
- 参考 [API 文档](api.md) 了解完整的 API 接口

