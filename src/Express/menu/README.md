# Menu 前端（Vue + Vite）

- 开发：

```bash
cd src/Express/menu
npm install
npm run dev
```

- 构建：

```bash
npm run build
```

构建后产物位于 `dist/`，后端会读取 `dist/index.html` 并在其中的 `/*!insert*/` 位置注入：

```js
var __ENTRY__ = "<entry-name>"
```

页面运行时会：
- GET `/api/<entry>.menu` 获取表单 schema
- POST `/api/<entry>.menu?op=apply&...` 提交变更

后端已提供 `/assets/{path}` 静态路由，Vite 构建默认引用 `/assets/*`，可直接工作。

