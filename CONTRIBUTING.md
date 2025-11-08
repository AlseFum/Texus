# 贡献指南 Contributing Guide

感谢你对 Texus 感兴趣！我们欢迎任何形式的贡献。

Thank you for your interest in Texus! We welcome contributions of all kinds.

[English](#english) | [中文](#中文)

---

## English

### How to Contribute

There are many ways to contribute to Texus:

1. **Report Bugs** - Found a bug? [Create an issue](https://github.com/your-org/texus/issues/new?template=bug_report.yml)
2. **Suggest Features** - Have an idea? [Request a feature](https://github.com/your-org/texus/issues/new?template=feature_request.yml)
3. **Improve Documentation** - Help make our docs better
4. **Write Code** - Submit pull requests for bug fixes or new features
5. **Share** - Star the repo, share with friends, write blog posts

### Getting Started

1. **Fork the Repository**
   ```bash
   # Click the "Fork" button on GitHub
   git clone https://github.com/your-username/texus.git
   cd texus
   ```

2. **Set Up Development Environment**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync
   
   # Run development server
   uv run dev
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/my-amazing-feature
   ```

4. **Make Your Changes**
   - Write clean, well-documented code
   - Follow the existing code style
   - Add tests if applicable

5. **Test Your Changes**
   ```bash
   # Run tests
   uv run pytest
   
   # Check linting
   uv run ruff check src
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "✨ Add amazing feature"
   ```
   
   Use [conventional commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test updates
   - `chore:` - Build/config updates

7. **Push and Create PR**
   ```bash
   git push origin feature/my-amazing-feature
   ```
   Then create a pull request on GitHub.

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Write tests for new features

### Project Structure

```
texus/
├── src/
│   ├── Port/           # Port modules (Text, Exec, Gen, Meta, Timer)
│   ├── Express/        # Rendering system
│   ├── Database/       # Database implementation
│   ├── Common/         # Shared utilities
│   └── app.py          # Main application
├── docs/               # Documentation
└── tests/              # Tests
```

### Need Help?

- Read the [documentation](docs/)
- Join discussions in [Issues](https://github.com/your-org/texus/issues)
- Ask questions in pull requests

---

## 中文

### 如何贡献

你可以通过多种方式为 Texus 做出贡献：

1. **报告错误** - 发现了 Bug？[创建 Issue](https://github.com/your-org/texus/issues/new?template=bug_report.yml)
2. **提出建议** - 有好想法？[提交功能建议](https://github.com/your-org/texus/issues/new?template=feature_request.yml)
3. **改进文档** - 帮助我们完善文档
4. **贡献代码** - 提交 PR 修复 Bug 或实现新功能
5. **传播分享** - Star 项目、分享给朋友、写博客

### 开始贡献

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上点击 "Fork" 按钮
   git clone https://github.com/your-username/texus.git
   cd texus
   ```

2. **搭建开发环境**
   ```bash
   # 安装 uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 安装依赖
   uv sync
   
   # 运行开发服务器
   uv run dev
   ```

3. **创建特性分支**
   ```bash
   git checkout -b feature/我的新功能
   ```

4. **进行修改**
   - 编写清晰、有文档的代码
   - 遵循现有代码风格
   - 如适用，添加测试

5. **测试你的修改**
   ```bash
   # 运行测试
   uv run pytest
   
   # 检查代码规范
   uv run ruff check src
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "✨ 添加新功能"
   ```
   
   使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/):
   - `feat:` - 新功能
   - `fix:` - Bug 修复
   - `docs:` - 文档修改
   - `style:` - 代码格式
   - `refactor:` - 重构
   - `test:` - 测试更新
   - `chore:` - 构建/配置更新

7. **推送并创建 PR**
   ```bash
   git push origin feature/我的新功能
   ```
   然后在 GitHub 上创建 Pull Request。

### 代码规范

- Python 代码遵循 PEP 8
- 使用有意义的变量名
- 为函数和类添加文档字符串
- 保持函数专注和简洁
- 为新功能编写测试

### 项目结构

```
texus/
├── src/
│   ├── Port/           # Port 模块（Text、Exec、Gen、Meta、Timer）
│   ├── Express/        # 渲染系统
│   ├── Database/       # 数据库实现
│   ├── Common/         # 共享工具
│   └── app.py          # 主应用
├── docs/               # 文档
└── tests/              # 测试
```

### 需要帮助？

- 阅读[文档](docs/)
- 在 [Issues](https://github.com/your-org/texus/issues) 中参与讨论
- 在 Pull Request 中提问

---

## Code of Conduct / 行为准则

We are committed to providing a welcoming and inclusive environment. Please be respectful and considerate in all interactions.

我们致力于提供友好和包容的环境。请在所有互动中保持尊重和体谅。

## License / 许可证

By contributing to Texus, you agree that your contributions will be licensed under the MIT License.

通过为 Texus 贡献，你同意你的贡献将在 MIT 许可证下授权。

---

Thank you for contributing to Texus! 🎉

感谢你为 Texus 做出贡献！🎉

