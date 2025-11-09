import os
import importlib
from typing import Callable, Dict, Optional, Any
from Common.base import FinalVis
from Database import Table
from Common.logger import get_logger

logger = get_logger("port")

# 默认 Port - 处理原始数据
class DefaultPort:
    @staticmethod
    def access(pack):
        main_table = Table.of("main")
        data = main_table.get(pack.entry)
        display_data = data if data is not None else ""
        # 如果data是entry对象，提取其文本内容
        if hasattr(display_data, 'value'):
            if isinstance(display_data.value, dict) and 'text' in display_data.value:
                display_data = display_data.value['text']
            elif hasattr(display_data, 'to_raw') and callable(display_data.to_raw):
                display_data = display_data.to_raw()
        # Web请求：只需要payload
        return FinalVis.of("raw", payload={"text": str(display_data),"title":"" if main_table.get(pack.entry) else "-"})

# Port 注册表
ports: Dict[str, type] = {}

class PortRegistry:
    def __init__(self, initial: Optional[Dict[str, type]] = None):
        self._ports = ports if initial is None else initial
    
    def register_mime(self, mime: str, port_class: type):
        """注册 mime 类型对应的 Port 类"""
        if not mime or not hasattr(port_class, "access"):
            raise ValueError("Invalid mime or port_class")
        self._ports[mime] = port_class
    
    def get_port(self, mime: str) -> type:
        """获取 mime 类型对应的 Port 类"""
        return self._ports.get(mime, DefaultPort)

registry = PortRegistry()

def register_port(mime: str, port_class: type):
    """注册 Port 类"""
    registry.register_mime(mime, port_class)
    # logger.debug(f"注册 Port: mime={mime}, class={port_class.__name__}")

def dispatch(mime: str) -> type:
    """根据 mime 类型分发到对应的 Port"""
    return registry.get_port(mime)

def _load_plugins_from_port_root():
    """从 Port 目录自动加载所有插件"""
    base_dir = os.path.dirname(__file__)
    package_name = __name__
    
    for fname in os.listdir(base_dir):
        # 跳过 __init__.py 和非 Python 文件
        if fname == "__init__.py" or not fname.endswith(".py"):
            continue
        
        module_name = f"{package_name}.{fname[:-3]}"
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "registry") and callable(getattr(mod, "registry")):
                info = mod.registry()
                _register_plugin_dict(info)
                # logger.debug(f"加载插件: {fname}")
        except Exception as e:
            pass
            # logger.warning(f"加载插件失败: {module_name}, 错误: {e}")
    
    # 加载子目录中的插件（如 Gen）
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and not item.startswith("__"):
            try:
                module_name = f"{package_name}.{item}"
                mod = importlib.import_module(module_name)
                if hasattr(mod, "registry") and callable(getattr(mod, "registry")):
                    info = mod.registry()
                    _register_plugin_dict(info)
            except Exception as e:
                pass
                # print(f"Warning: Failed to load Port plugin {module_name}: {e}")

def _register_plugin_dict(info: Dict[str, Any]):
    """
    从插件信息字典注册 Port：
    - mime: MIME 类型（字符串或数组）
    - port/handler/class: Port 类或处理函数
    """
    if not isinstance(info, dict):
        return
    
    mime_types = info.get("mime")
    port_obj = info.get("port") or info.get("handler") or info.get("class")
    
    if not port_obj or mime_types is None:
        return
    
    # 如果是函数，包装成 Port 类
    if callable(port_obj) and not isinstance(port_obj, type):
        class WrapperPort:
            @staticmethod
            def access(pack):
                return port_obj(pack)
        port_class = WrapperPort
    else:
        port_class = port_obj
    
    # 注册 mime 类型
    if isinstance(mime_types, (list, tuple)):
        for mime in mime_types:
            if isinstance(mime, str) and mime:
                register_port(mime, port_class)
    elif isinstance(mime_types, str) and mime_types:
        register_port(mime_types, port_class)

def load_plugins():
    """加载所有插件"""
    # logger.info("开始加载 Port 插件...")
    _load_plugins_from_port_root()
    
    # 支持环境变量加载外部插件
    env = os.environ.get("PORT_PLUGINS", "").strip()
    if env:
        for mod_name in [x.strip() for x in env.split(",") if x.strip()]:
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "registry") and callable(getattr(mod, "registry")):
                    info = mod.registry()
                    _register_plugin_dict(info)
                    # logger.info(f"加载外部插件: {mod_name}")
            except Exception as e:
                pass
                # logger.warning(f"加载外部插件失败: {mod_name}, 错误: {e}")
    
    # logger.info(f"Port 插件加载完成，共注册 {len(ports)} 个 MIME 类型")

# 模块导入时自动加载插件
load_plugins()

# 向后兼容：提供 Default 别名
Default = DefaultPort
