# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""市场快照模块.

获取 A股市场整体状况快照。
"""

from datetime import datetime

import pandas as pd


class MarketSnapshot:
    """市场快照生成器."""

    def __init__(self, provider) -> None:
        """初始化市场快照生成器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def generate(self) -> dict:
        """生成市场快照.

        Returns:
            dict with keys:
            - timestamp: 生成时间
            - indices: 指数数据列表
            - statistics: 市场统计

        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取指数数据
        indices = self._get_indices_data()

        # 获取市场统计
        statistics = self.provider.get_market_statistics()

        return {
            "timestamp": timestamp,
            "indices": indices,
            "statistics": statistics,
        }

    def _get_indices_data(self) -> list[dict]:
        """获取指数数据.

        Returns:
            指数数据列表

        """
        try:
            df = self.provider.get_indices_snapshot()

            indices = []
            for _, row in df.iterrows():
                indices.append({
                    "code": row["code"],
                    "name": row["name"],
                    "price": round(row["price"], 2),
                    "change": round(row["change"], 2),
                    "change_pct": round(row["change_pct"], 2),
                })

            return indices

        except Exception:
            return []

    def to_dataframe(self) -> pd.DataFrame:
        """将快照转换为 DataFrame（用于 CSV 输出）.

        Returns:
            DataFrame 包含市场快照数据

        """
        snapshot = self.generate()

        # 创建一行数据
        data = {
            "timestamp": snapshot["timestamp"],
        }

        # 添加指数数据
        for idx in snapshot["indices"]:
            data[f"{idx['name']}_点位"] = idx["price"]
            data[f"{idx['name']}_涨跌幅"] = idx["change_pct"]

        # 添加统计数据
        stats = snapshot["statistics"]
        data["total_count"] = stats["total_count"]
        data["up_count"] = stats["up_count"]
        data["down_count"] = stats["down_count"]
        data["limit_up_count"] = stats["limit_up_count"]
        data["limit_down_count"] = stats["limit_down_count"]
        data["total_turnover"] = stats["total_turnover"]

        return pd.DataFrame([data])
