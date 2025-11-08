class Table:
    def __init__(self, string):
        self.inner = {}
        self.name = string
        self._sync_required = False  # 标记是否需要备份
        from . import tables
        tables[string] = self
    
    @staticmethod
    def of(string):
        from . import tables
        if string in tables:
            return tables[string]
        else:
            return Table(string)
    @staticmethod
    def the(string):
        return Table.of(string)
    
    def get(self, key, otherwise=None):
        return self.inner.get(key, otherwise)
    
    def set(self, key, value):
        self.inner[key] = value
        # 当数据发生变化时，标记需要备份
        self._sync_required = True
    
    def __getitem__(self, key):
        return self.get(key, None)
    
    def __setitem__(self, key, value):
        self.set(key, value)
    
    def sync(self):
        """标记此表需要被备份"""
        self._sync_required = True
        return self
    
    def is_sync_required(self):
        """检查此表是否需要备份"""
        return self._sync_required
    
    def mark_synced(self):
        """标记此表已经备份完成"""
        self._sync_required = False
    
    def get_all_data(self):
        """获取表的所有数据，用于备份"""
        return {
            "name": self.name,
            "data": self.inner.copy(),
            "sync_required": self._sync_required
        }
    
    @staticmethod
    def table_names():
        from . import tables
        return list(tables.keys())
    
    @staticmethod
    def get_tables_need_sync():
        """获取所有需要备份的表"""
        from . import tables
        return [table for table in tables.values() if table._sync_required]
