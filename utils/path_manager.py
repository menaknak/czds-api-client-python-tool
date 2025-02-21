import json
import os
from pathlib import Path

class PathManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PathManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        config_path = Path(__file__).parent.parent / 'config.json'
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.base_paths = self.config['base_paths']
        # 先展开基础路径
        self._expand_base_paths()
        # 再展开其他路径
        self._expand_paths()
        # 处理working.directory
        self._process_working_directory()
        
        # 确保所有必要的目录存在
        self._ensure_directories()

    def _expand_base_paths(self):
        """展开基础路径中的变量"""
        self.base_paths['data_root'] = self.base_paths['data_root'].format(**self.base_paths)
        self.base_paths['log_root'] = self.base_paths['log_root'].format(**self.base_paths)
    
    def _process_working_directory(self):
        """处理working.directory配置"""
        working_dir = self.config['working.directory']
        if '{' in working_dir:
            # 支持引用base_paths.paths中的路径
            path_ref = working_dir[1:-1].split('.')[-1]
            self.config['working.directory'] = self.get_path(path_ref)

    def _expand_paths(self):
        """展开paths中的所有路径变量"""
        for key, path in self.base_paths['paths'].items():
            self.base_paths['paths'][key] = path.format(**self.base_paths)
    
    def _ensure_directories(self):
        """确保所有必要的目录存在"""
        for path in self.base_paths['paths'].values():
            os.makedirs(path, exist_ok=True)
    
    def get_path(self, key):
        """获取指定的路径"""
        return self.base_paths['paths'].get(key)
    
    def get_dated_path(self, key, date):
        """获取带日期的路径"""
        base = self.get_path(key)
        return os.path.join(base, date)

