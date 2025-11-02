# API 文档

## 基础端点

### 静态资源

```http
GET /assets/{path}
```

提供前端静态资源文件。

## 文本 API

### 读取文本

```http
GET /api/{entry}
```

**参数**:
- `entry`: 数据条目路径

**响应**:
```json
{
  "text": "文本内容",
  "lastSavedTime": "2024-01-01T12:00:00"
}
```

### 写入文本

```http
POST /api/{entry}?op=set&content={content}
```

**参数**:
- `entry`: 数据条目路径
- `content`: 文本内容（URL 编码）

**响应**:
```json
{
  "success": true,
  "message": "保存成功",
  "data": {
    "text": "文本内容",
    "lastSavedTime": "2024-01-01T12:00:00"
  }
}
```

## 脚本执行 API

### 执行脚本

```http
GET /api/{entry}.py
POST /api/{entry}.py?script={script}
```

**参数**:
- `entry`: 脚本文件路径
- `script`: 可选的脚本内容（用于 POST 请求）

**响应**:
```json
{
  "success": true,
  "output": "脚本输出",
  "operations": [...],
  "operations_count": 5
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误信息",
  "output": "",
  "operations": []
}
```

## Meta 脚本 API

### 执行 Meta 脚本

```http
GET /api/{source}.{meta}
```

**参数**:
- `source`: 源数据 entry 名称
- `meta`: Meta 脚本 entry 名称

**响应**: 脚本的 print 输出（纯文本）

## 生成器 API

### 生成内容

```http
GET /api/{entry}.gen
```

**参数**:
- `entry`: 生成器模板 entry 名称

**响应**: 生成的随机内容（纯文本）

## 定时任务 API

### 查看定时任务

```http
GET /api/{entry}.timer
```

**参数**:
- `entry`: Timer entry 名称

**响应**: Timer 文件内容

## 请求类型

系统自动识别请求类型：

- **API 请求**: `/api/*` 路径或包含 `from=api` 参数
- **Web 请求**: 其他情况

## 错误处理

所有 API 错误遵循以下格式：

```json
{
  "detail": "错误描述"
}
```

**常见错误码**:
- `404`: 资源不存在
- `500`: 服务器内部错误

