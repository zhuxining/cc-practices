# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""财务分析模块.

分析股票财务指标和估值水平。
"""


class FinancialAnalyzer:
    """财务分析器."""

    def __init__(self, provider) -> None:
        """初始化财务分析器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def get_financial_summary(self, symbol: str) -> dict:
        """获取财务摘要.

        Args:
            symbol: 股票代码

        Returns:
            财务摘要字典

        """
        try:
            # 获取财务数据
            financial = self.provider.get_stock_financial_summary(symbol)

            # 获取实时行情
            spot = self.provider.get_stock_spot(symbol)

            return {
                "symbol": symbol,
                "name": spot.get("name", ""),
                "price": spot.get("price"),
                "market_cap": spot.get("market_cap"),
                "circulating_cap": spot.get("circulating_cap"),
                "pe": financial.get("pe"),
                "pb": financial.get("pb"),
                "ps": financial.get("ps"),
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def analyze_valuation(self, symbol: str, industry_pe: float | None = None) -> dict:
        """分析估值水平.

        Args:
            symbol: 股票代码
            industry_pe: 行业平均 PE

        Returns:
            估值分析结果

        """
        financial = self.get_financial_summary(symbol)

        if "error" in financial:
            return financial

        pe = financial.get("pe")
        pb = financial.get("pb")

        # 估值等级
        valuation_level = "neutral"
        valuation_reason = []

        if pe is not None:
            if pe < 15:
                valuation_level = "undervalued"
                valuation_reason.append(f"PE={pe:.1f}，偏低")
            elif pe > 50:
                valuation_level = "overvalued"
                valuation_reason.append(f"PE={pe:.1f}，偏高")

        if industry_pe and pe:
            ratio = pe / industry_pe
            if ratio < 0.7:
                valuation_reason.append(f"低于行业平均 {industry_pe:.1f}")
            elif ratio > 1.5:
                valuation_reason.append(f"高于行业平均 {industry_pe:.1f} 较多")

        return {
            "symbol": symbol,
            "name": financial["name"],
            "pe": pe,
            "pb": pb,
            "valuation_level": valuation_level,
            "reason": "，".join(valuation_reason) if valuation_reason else "估值适中",
        }

    def batch_analyze(self, symbols: list[str]) -> list[dict]:
        """批量分析财务数据.

        Args:
            symbols: 股票代码列表

        Returns:
            分析结果列表

        """
        results = []

        for symbol in symbols:
            try:
                result = self.get_financial_summary(symbol)
                results.append(result)
            except Exception as e:
                results.append({"symbol": symbol, "error": str(e)})

        return results


class ValuationAnalyzer:
    """估值分析器."""

    def __init__(self, provider) -> None:
        """初始化估值分析器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def compare_with_industry(self, symbol: str, industry_symbols: list[str]) -> dict:
        """与行业内其他股票比较估值.

        Args:
            symbol: 股票代码
            industry_symbols: 行业内股票代码列表

        Returns:
            比较结果

        """
        # 获取目标股票估值
        target_financial = self.provider.get_stock_financial_summary(symbol)
        target_pe = target_financial.get("pe")

        if target_pe is None:
            return {"error": "无法获取 PE 数据"}

        # 获取行业内其他股票的 PE
        pes = []
        for s in industry_symbols:
            if s == symbol:
                continue
            try:
                f = self.provider.get_stock_financial_summary(s)
                pe = f.get("pe")
                if pe is not None and 0 < pe < 100:  # 过滤异常值
                    pes.append(pe)
            except Exception:
                continue

        if not pes:
            return {"error": "无法获取行业数据"}

        # 计算行业平均 PE
        industry_pe = sum(pes) / len(pes)

        # 计算百分位
        all_pes = [*pes, target_pe]
        all_pes.sort()
        percentile = all_pes.index(target_pe) / len(all_pes) * 100

        return {
            "symbol": symbol,
            "pe": target_pe,
            "industry_pe": industry_pe,
            "industry_count": len(pes),
            "percentile": round(percentile, 1),
            "valuation": "undervalued"
            if target_pe < industry_pe * 0.8
            else "overvalued"
            if target_pe > industry_pe * 1.2
            else "neutral",
        }


class GrowthAnalyzer:
    """成长性分析器."""

    def __init__(self, provider) -> None:
        """初始化成长分析器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def analyze_growth(self, symbol: str) -> dict:
        """分析成长性.

        Args:
            symbol: 股票代码

        Returns:
            成长性分析结果

        """
        # 这里简化处理
        # 实际需要获取财报数据计算营收和利润增长率
        return {
            "symbol": symbol,
            "revenue_growth": None,
            "profit_growth": None,
            "note": "成长性分析需要更详细的财报数据",
        }
