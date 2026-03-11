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

    def get_business_composition(self, symbol: str) -> dict:
        """获取主营构成分析.

        Args:
            symbol: 股票代码

        Returns:
            主营构成分析结果

        """
        try:
            df = self.provider.get_stock_business_composition(symbol)

            if df.empty:
                return {"symbol": symbol, "error": "无主营构成数据"}

            # 获取股票基本信息
            spot = self.provider.get_stock_spot(symbol)

            # 解析业务构成
            products = []
            for _, row in df.iterrows():
                products.append(
                    {
                        "name": row.get("product_name", ""),
                        "revenue": row.get("revenue"),
                        "revenue_ratio": row.get("revenue_ratio"),
                        "profit": row.get("profit"),
                        "profit_ratio": row.get("profit_ratio"),
                    }
                )

            # 计算集中度（前三大业务占比）
            top_3_ratio = 0
            if len(products) >= 3:
                top_3_ratio = sum(
                    [p.get("revenue_ratio", 0) or 0 for p in products[:3]]
                )

            return {
                "symbol": symbol,
                "name": spot.get("name", ""),
                "products": products,
                "product_count": len(products),
                "top_3_concentration": round(top_3_ratio, 2),
                "analysis": self._analyze_concentration(top_3_ratio),
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def _analyze_concentration(self, concentration: float) -> str:
        """分析业务集中度."""
        if concentration > 0.8:
            return "高度集中，单一业务风险较高"
        if concentration > 0.5:
            return "适度集中，业务相对专注"
        return "多元化布局，业务分布广泛"

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

    def get_peer_valuation_comparison(self, symbol: str) -> dict:
        """获取同行估值比较（使用 AKShare）.

        Args:
            symbol: 股票代码

        Returns:
            同行估值比较结果

        """
        try:
            df = self.provider.get_stock_valuation_comparison(symbol)

            if df.empty:
                return {"symbol": symbol, "error": "无同行估值数据"}

            # 找到目标股票
            target = df[df["code"] == symbol]

            if target.empty:
                return {"symbol": symbol, "error": "未在同行数据中找到"}

            target_row = target.iloc[0]

            # 计算行业平均值
            industry_pe = df["pe"].mean()
            industry_pb = df["pb"].mean()

            # PE 百分位
            pe_sorted = df["pe"].dropna().sort_values().tolist()
            pe_percentile = (
                pe_sorted.index(target_row["pe"]) / len(pe_sorted) * 100
                if target_row["pe"] in pe_sorted
                else None
            )

            return {
                "symbol": symbol,
                "name": target_row.get("name", ""),
                "pe": target_row.get("pe"),
                "pb": target_row.get("pb"),
                "ps": target_row.get("ps"),
                "industry_pe": round(industry_pe, 2),
                "industry_pb": round(industry_pb, 2),
                "peer_count": len(df),
                "pe_percentile": round(pe_percentile, 1) if pe_percentile else None,
                "valuation": "undervalued"
                if target_row.get("pe") and target_row["pe"] < industry_pe * 0.8
                else "overvalued"
                if target_row.get("pe") and target_row["pe"] > industry_pe * 1.2
                else "neutral",
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}


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

    def get_peer_growth_comparison(self, symbol: str) -> dict:
        """获取同行成长性比较（使用 AKShare）.

        Args:
            symbol: 股票代码

        Returns:
            同行成长性比较结果

        """
        try:
            df = self.provider.get_stock_growth_comparison(symbol)

            if df.empty:
                return {"symbol": symbol, "error": "无同行成长性数据"}

            # 找到目标股票
            target = df[df["code"] == symbol]

            if target.empty:
                return {"symbol": symbol, "error": "未在同行数据中找到"}

            target_row = target.iloc[0]

            # 计算行业平均值
            industry_revenue_growth = df["revenue_growth"].mean()
            industry_profit_growth = df["profit_growth"].mean()

            # 营收增长率百分位
            revenue_sorted = df["revenue_growth"].dropna().sort_values().tolist()
            revenue_percentile = (
                revenue_sorted.index(target_row["revenue_growth"]) / len(revenue_sorted) * 100
                if target_row["revenue_growth"] in revenue_sorted
                else None
            )

            # 利润增长率百分位
            profit_sorted = df["profit_growth"].dropna().sort_values().tolist()
            profit_percentile = (
                profit_sorted.index(target_row["profit_growth"]) / len(profit_sorted) * 100
                if target_row["profit_growth"] in profit_sorted
                else None
            )

            # 成长性等级
            growth_level = "high"
            if target_row.get("revenue_growth") and target_row.get("profit_growth"):
                avg_growth = (target_row["revenue_growth"] + target_row["profit_growth"]) / 2
                industry_avg = (industry_revenue_growth + industry_profit_growth) / 2
                if avg_growth > industry_avg * 1.2:
                    growth_level = "high"
                elif avg_growth < industry_avg * 0.8:
                    growth_level = "low"
                else:
                    growth_level = "medium"

            return {
                "symbol": symbol,
                "name": target_row.get("name", ""),
                "revenue_growth": target_row.get("revenue_growth"),
                "profit_growth": target_row.get("profit_growth"),
                "roe": target_row.get("roe"),
                "industry_revenue_growth": round(industry_revenue_growth, 2),
                "industry_profit_growth": round(industry_profit_growth, 2),
                "peer_count": len(df),
                "revenue_percentile": round(revenue_percentile, 1) if revenue_percentile else None,
                "profit_percentile": round(profit_percentile, 1) if profit_percentile else None,
                "growth_level": growth_level,
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}
