from Database import Table
from Common.base import FinalVis, entry
from datetime import datetime
from .Text import Text, ShadowPort


def _infer_type(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    return "text"


def _extract_primitive(value):
    if isinstance(value, entry):
        # 常规 text entry
        if isinstance(value.value, dict) and "text" in value.value:
            return value.value.get("text", "")
        return value.value
    return value


class Menu(ShadowPort):
    """基于 PUB 前缀自动生成表单的 ShadowPort (.menu)

    - 访问 web: 返回 menu 页面，由 Express/vue 渲染
    - 访问 api get: 返回表单 schema（fields）
    - 访问 api post (op=apply): 根据提交值写回 PUB（以 <base>.<field> 为键）
    """

    @staticmethod
    def _base_key(entry_key: str) -> str:
        # 对于 entry=foo （来自 foo.menu），base 就是 foo
        return entry_key or ""

    @staticmethod
    def _schema_for(base_key: str) -> dict:
        fields = []
        main_table = Table.of("main")

        # 遍历主表中以 base_key. 开头的键，自动生成字段
        for k, v in main_table.inner.items():
            if not isinstance(k, str):
                continue
            prefix = f"{base_key}."
            if not k.startswith(prefix):
                continue
            name = k[len(prefix) :]
            current = _extract_primitive(v)
            ftype = _infer_type(current)
            # 简单的 normalizer
            if ftype == "number":
                try:
                    current = float(current)
                except Exception:
                    current = 0
            elif ftype == "boolean":
                current = bool(current)
            else:
                current = "" if current is None else str(current)

            fields.append(
                {
                    "name": name,
                    "type": ftype,
                    "value": current,
                    "key": k,
                }
            )

        return {"title": base_key or "menu", "fields": fields}

    @staticmethod
    def access(pack) -> FinalVis:
        op = getattr(pack, "query", {}).get("op", "get")
        by = getattr(pack, "by", "web")
        entry_key = getattr(pack, "entry", "")
        base_key = Menu._base_key(entry_key)

        if by == "api":
            if op in ["apply", "set", "submit", "post"]:
                # 提交并写回 PUB
                return Menu._apply(pack, base_key)
            # 返回 schema
            schema = Menu._schema_for(base_key)
            return FinalVis.of("menu", {"entry": base_key, **schema}, skip=True)

        # web 渲染交给 Express/vue，值中放入 entry，便于模板知道请求哪个接口
        return FinalVis.of("menu", base_key)

    @staticmethod
    def _apply(pack, base_key: str) -> FinalVis:
        q = getattr(pack, "query", {}) or {}
        schema = Menu._schema_for(base_key)
        fields_by_name = {f["name"]: f for f in schema.get("fields", [])}

        updated = []
        for name, meta in fields_by_name.items():
            if name not in q:
                continue
            new_val = q.get(name)
            dst_key = meta.get("key") or f"{base_key}.{name}"

            # 类型转换
            ftype = meta.get("type", "text")
            if ftype == "number":
                try:
                    # 允许整数或浮点
                    new_val = float(new_val) if "." in str(new_val) else int(new_val)
                except Exception:
                    new_val = 0
            elif ftype == "boolean":
                new_val = str(new_val).lower() in ["1", "true", "t", "yes", "y", "on"]
            else:
                new_val = str(new_val)

            main_table = Table.of("main")
            existed = main_table.get(dst_key)
            if isinstance(existed, entry):
                # 常见的是 text entry：更新其文本
                if existed.mime == "text":
                    text_val = existed.value if isinstance(existed.value, dict) else {}
                    text_val = dict(text_val)
                    text_val["text"] = str(new_val)
                    text_val["lastSavedTime"] = datetime.now()
                    main_table.set(dst_key, entry(mime="text", value=text_val))
                else:
                    # 其他 entry，直接覆盖其 value
                    main_table.set(dst_key, entry(mime=existed.mime, value=new_val))
            else:
                # 原为原生类型则直接写回（默认 text）
                main_table.set(dst_key, new_val)

            updated.append(dst_key)

        return FinalVis.of(
            "menu",
            {
                "success": True,
                "updated": updated,
                "entry": base_key,
            },
            skip=True,
        )

# 注册到 ShadowPort
ShadowPort.set(Menu)

# 插件注册函数
def registry():
    return {
        "mime": "menu",
        "port": Menu
    }


