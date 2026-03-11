# /// script
# dependencies = [
#     "pandas>=3.0.0",
#     "pyyaml>=6.0",
# ]
# ///

"""数据路由器.

根据股票代码和市场类型路由到不同的数据源。
"""

from pathlib import Path
import re

import yaml


class DataRouter:
    """数据源路由器."""

    def __init__(self, config_path: str | None = None) -> None:
        """初始化数据路由器.

        Args:
            config_path: 配置文件路径

        """
        if config_path is None:
            # 默认配置文件路径
            config_path = str(Path(__file__).parent.parent.parent / "config" / "default.yaml")

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._providers = {}

    def _load_config(self) -> dict:
        """加载配置文件."""
        if self.config_path.exists():
            with Path(self.config_path).open(encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def get_provider(self, symbol: str):
        """根据股票代码路由到对应的数据提供者.

        Args:
            symbol: 股票代码

        Returns:
            数据提供者实例

        """
        # 延迟导入, 避免循环依赖
        if not self._providers:
            from core.akshare_provider import AKShareProvider

            self._providers["akshare"] = AKShareProvider()

        # A股代码格式: 6 位数字 + .SH/.SZ
        if re.match(r"^\d{6}\.[SZ]H$", symbol):
            return self._providers["akshare"]

        # 默认使用 AKShare
        return self._providers["akshare"]

    def get_provider_for_market(self, market: str):
        """根据市场类型获取数据提供者.

        Args:
            market: 市场类型 (SH, SZ, HK, US)

        Returns:
            数据提供者实例

        """
        if not self._providers:
            from core.akshare_provider import AKShareProvider

            self._providers["akshare"] = AKShareProvider()

        # A股市场
        if market in ["SH", "SZ"]:
            return self._providers["akshare"]

        # 默认
        return self._providers["akshare"]

    def get_config(self, key_path: str, default=None):
        """获取配置值.

        Args:
            key_path: 配置键路径（使用点号分隔）
            default: 默认值

        Returns:
            配置值

        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value
