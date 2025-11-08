# 贡献指南

感谢您对 Texus 项目的关注！我们欢迎任何形式的贡献。

## 开发环境设置

1. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd texus
   ```

2. **创建虚拟环境**:
   ```bash
   uv venv
   ```

3. **安装依赖**:
   ```bash
   uv sync
   ```

4. **运行开发服务器**:
   ```bash
   uv run uvicorn --app-dir src app:app --reload --host 0.0.0.0 --port 7123
   ```

## 代码规范

- **Python 风格**: 遵循 PEP 8
- **类型提示**: 使用类型注解
- **文档字符串**: 为所有公共函数和类添加文档字符串
- **注释**: 解释复杂的逻辑

## 提交规范

提交信息应遵循以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```
feat(Port): 添加新的 Gen Port 功能

实现了基于模板的内容生成器，支持随机选择和嵌套结构。

Closes #123
```

## 添加新的 Port

1. **创建 Port 类**:
   ```python
   from Common.base import FinalVis
   from .Text import Text
   
   class MyPort(Text):
       @staticmethod
       def access(pack) -> FinalVis:
           # 处理逻辑
           return FinalVis.of("text", result)
   ```

2. **注册到分发系统**:
   在 `src/Port/__init__.py` 中的 `dispatch()` 函数添加：
   ```python
   elif which == "myport":
       return MyPort
   ```

3. **编写文档**:
   - 在 `src/Port/README.md` 中添加说明
   - 在 `src/Port/Meta.py` 中添加帮助文档

## 测试

运行测试（如果有）:

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_port.py
```

## Pull Request 流程

1. **创建分支**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **提交更改**:
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

3. **推送分支**:
   ```bash
   git push origin feature/my-feature
   ```

4. **创建 Pull Request**:
   - 在 GitHub 上创建 PR
   - 描述更改内容和原因
   - 等待代码审查

## 问题报告

报告问题时请包含：

- **问题描述**: 清晰描述问题
- **复现步骤**: 如何重现问题
- **预期行为**: 应该发生什么
- **实际行为**: 实际发生了什么
- **环境信息**: Python 版本、操作系统等

## 许可

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

## 贡献者

感谢所有为项目做出贡献的人！

