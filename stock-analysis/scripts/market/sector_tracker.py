# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""板块跟踪模块.

跟踪热点行业板块和资金流向。
"""

import pandas as pd


class SectorTracker:
    """板块跟踪器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化板块跟踪器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}

        # 热点板块阈值
        self.hot_threshold = self.config.get("hot_threshold", 2.0)
        self.top_n = self.config.get("hot_sectors_top_n", 5)

    def get_hot_sectors(
        self, threshold: float | None = None, top_n: int | None = None
    ) -> pd.DataFrame:
        """获取热点板块.

        Args:
            threshold: 涨跌幅阈值
            top_n: 返回前 N 个

        Returns:
            DataFrame with columns:
            - rank: 排名
            - sector_code: 板块代码
            - sector_name: 板块名称
            - change_pct: 涨跌幅
            - turnover: 成交额
            - volume: 成交量
            - turnover_rate: 换手率
            - flow_net: 净流入
            - leading_stocks: 领涨股票

        """
        if threshold is None:
            threshold = self.hot_threshold
        if top_n is None:
            top_n = self.top_n

        # 获取板块排行
        ranking = self.provider.get_sector_ranking(sort_by="change_pct")

        # 筛选热点板块
        hot_sectors = ranking[ranking["change_pct"] >= threshold].head(top_n).copy()

        # 获取资金流向
        flow_df = self.provider.get_sector_capital_flow()

        # 合并资金流向数据
        if not flow_df.empty:
            hot_sectors = hot_sectors.merge(
                flow_df[["sector_name", "flow_net"]],
                on="sector_name",
                how="left",
            )

        return hot_sectors

    def get_sector_flow_ranking(self) -> pd.DataFrame:
        """获取板块资金流向排行.

        Returns:
            DataFrame with columns:
            - rank: 排名
            - sector_name: 板块名称
            - flow_in: 主力流入
            - flow_out: 主力流出
            - flow_net: 净流入
            - flow_net_pct: 净流入占比

        """
        return self.provider.get_sector_capital_flow()

    def get_hot_sectors_detail(
        self, threshold: float | None = None, top_n: int | None = None
    ) -> list[dict]:
        """获取热点板块详细信息.

        Args:
            threshold: 涨跌幅阈值
            top_n: 返回前 N 个

        Returns:
            板块详细信息列表

        """
        hot_df = self.get_hot_sectors(threshold, top_n)

        sectors = []
        for _, row in hot_df.iterrows():
            sector_name = row["sector_name"]

            # 获取成分股
            try:
                constituents = self.provider.get_sector_constituents(sector_name, top_n=3)

                leading_stocks = []
                for _, stock in constituents.iterrows():
                    leading_stocks.append({
                        "symbol": stock["symbol"],
                        "name": stock["name"],
                        "price": stock["price"],
                        "change_pct": stock["change_pct"],
                    })
            except Exception:
                leading_stocks = []

            sectors.append({
                "rank": int(row["rank"]),
                "sector_code": row["sector_code"],
                "sector_name": sector_name,
                "change_pct": round(row["change_pct"], 2),
                "turnover": row["turnover"],
                "flow_net": round(row.get("flow_net", 0), 2),
                "leading_stocks": leading_stocks,
            })

        return sectors

    def get_sector_distribution(self, symbols: list[str]) -> pd.DataFrame:
        """获取股票列表的行业分布.

        Args:
            symbols: 股票代码列表

        Returns:
            DataFrame with columns:
            - sector: 行业名称
            - count: 股票数量
            - percentage: 占比

        """
        # 这里简化处理,实际需要获取每只股票的行业信息
        # 暂时返回空数据
        return pd.DataFrame(columns=["sector", "count", "percentage"])
