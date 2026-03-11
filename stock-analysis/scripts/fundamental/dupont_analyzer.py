# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""杜邦分析模块.

通过杜邦分析法分解 ROE，评估公司盈利能力、运营效率和财务杠杆。
"""


class DuPontAnalyzer:
    """杜邦分析器."""

    def __init__(self, provider) -> None:
        """初始化杜邦分析器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def analyze_dupont(self, symbol: str) -> dict:
        """分析杜邦指标.

        Args:
            symbol: 股票代码

        Returns:
            杜邦分析结果

        """
        try:
            df = self.provider.get_stock_dupont_comparison(symbol)

            if df.empty:
                return {"symbol": symbol, "error": "无杜邦分析数据"}

            # 找到目标股票
            target = df[df["code"] == symbol]

            if target.empty:
                return {"symbol": symbol, "error": "未在同行数据中找到"}

            target_row = target.iloc[0]

            roe = target_row.get("roe")
            net_profit_margin = target_row.get("net_profit_margin")
            asset_turnover = target_row.get("asset_turnover")
            equity_multiplier = target_row.get("equity_multiplier")

            # 分析各指标
            return {
                "symbol": symbol,
                "name": target_row.get("name", ""),
                "roe": roe,
                "net_profit_margin": net_profit_margin,
                "asset_turnover": asset_turnover,
                "equity_multiplier": equity_multiplier,
                "profitability_analysis": self._analyze_profitability(net_profit_margin),
                "efficiency_analysis": self._analyze_efficiency(asset_turnover),
                "leverage_analysis": self._analyze_leverage(equity_multiplier),
                "overall_analysis": self._analyze_overall(roe, net_profit_margin, asset_turnover, equity_multiplier),
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def get_peer_dupont_comparison(self, symbol: str) -> dict:
        """获取同行杜邦分析比较.

        Args:
            symbol: 股票代码

        Returns:
            同行杜邦比较结果

        """
        try:
            df = self.provider.get_stock_dupont_comparison(symbol)

            if df.empty:
                return {"symbol": symbol, "error": "无杜邦分析数据"}

            # 找到目标股票
            target = df[df["code"] == symbol]

            if target.empty:
                return {"symbol": symbol, "error": "未在同行数据中找到"}

            target_row = target.iloc[0]

            # 计算行业平均值
            industry_roe = df["roe"].mean()
            industry_net_profit_margin = df["net_profit_margin"].mean()
            industry_asset_turnover = df["asset_turnover"].mean()
            industry_equity_multiplier = df["equity_multiplier"].mean()

            # ROE 百分位
            roe_sorted = df["roe"].dropna().sort_values().tolist()
            roe_percentile = (
                roe_sorted.index(target_row["roe"]) / len(roe_sorted) * 100
                if target_row["roe"] in roe_sorted
                else None
            )

            return {
                "symbol": symbol,
                "name": target_row.get("name", ""),
                "roe": target_row.get("roe"),
                "net_profit_margin": target_row.get("net_profit_margin"),
                "asset_turnover": target_row.get("asset_turnover"),
                "equity_multiplier": target_row.get("equity_multiplier"),
                "industry_roe": round(industry_roe, 2),
                "industry_net_profit_margin": round(industry_net_profit_margin, 2),
                "industry_asset_turnover": round(industry_asset_turnover, 2),
                "industry_equity_multiplier": round(industry_equity_multiplier, 2),
                "peer_count": len(df),
                "roe_percentile": round(roe_percentile, 1) if roe_percentile else None,
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def _analyze_profitability(self, net_profit_margin: float | None) -> str:
        """分析盈利能力."""
        if net_profit_margin is None:
            return "数据不足"

        if net_profit_margin > 0.2:
            return "盈利能力优秀"
        if net_profit_margin > 0.1:
            return "盈利能力良好"
        if net_profit_margin > 0.05:
            return "盈利能力一般"
        return "盈利能力较弱"

    def _analyze_efficiency(self, asset_turnover: float | None) -> str:
        """分析运营效率."""
        if asset_turnover is None:
            return "数据不足"

        if asset_turnover > 1.5:
            return "资产利用效率高"
        if asset_turnover > 0.8:
            return "资产利用效率一般"
        return "资产利用效率较低"

    def _analyze_leverage(self, equity_multiplier: float | None) -> str:
        """分析财务杠杆."""
        if equity_multiplier is None:
            return "数据不足"

        if equity_multiplier > 3:
            return "杠杆较高，财务风险较大"
        if equity_multiplier > 1.5:
            return "杠杆适中"
        return "杠杆较低，财务保守"

    def _analyze_overall(
        self,
        roe: float | None,
        net_profit_margin: float | None,
        asset_turnover: float | None,
        equity_multiplier: float | None,
    ) -> str:
        """综合分析."""
        if all(v is None for v in [roe, net_profit_margin, asset_turnover, equity_multiplier]):
            return "数据不足"

        parts = []

        if roe is not None:
            if roe > 0.15:
                parts.append("ROE 优秀")
            elif roe > 0.1:
                parts.append("ROE 良好")

        if net_profit_margin is not None:
            parts.append(self._analyze_profitability(net_profit_margin))

        if asset_turnover is not None:
            parts.append(self._analyze_efficiency(asset_turnover))

        if equity_multiplier is not None:
            parts.append(self._analyze_leverage(equity_multiplier))

        return "，".join(parts) if parts else "数据不足"
