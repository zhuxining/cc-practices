# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""分组分析器.

分析自选分组中的股票。
"""

import pathlib

from fundamental.dupont_analyzer import DuPontAnalyzer
from fundamental.financial_analyzer import FinancialAnalyzer, GrowthAnalyzer, ValuationAnalyzer
from fundamental.news_analyzer import NewsAnalyzer

from group.scoring_engine import ScoringEngine
from group.signal_generator import TradingSignalGenerator


class GroupAnalyzer:
    """自选分组分析器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化分组分析器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}
        self.signal_gen = TradingSignalGenerator(provider, config)
        self.scoring = ScoringEngine(provider, config)
        self.financial = FinancialAnalyzer(provider)
        self.growth = GrowthAnalyzer(provider)
        self.valuation = ValuationAnalyzer(provider)
        self.dupont = DuPontAnalyzer(provider)
        self.news = NewsAnalyzer(provider)

    def analyze_group(self, symbols: list[str], group_name: str | None = None) -> dict:
        """分析整个分组.

        Args:
            symbols: 股票代码列表
            group_name: 分组名称

        Returns:
            分组分析结果

        """
        # 生成交易信号
        signals = self.signal_gen.generate_group_signals(symbols)

        # 计算分组概览
        summary = self._calculate_group_summary(symbols)

        # 分析表现最好和最差的股票
        top_performers = self._get_top_performers(symbols, top_n=5)
        laggards = self._get_laggards(symbols, top_n=5)

        # 基本面评分
        fundamental_scores = self._calculate_fundamental_scores(symbols)

        return {
            "group_name": group_name or "未命名分组",
            "stock_count": len(symbols),
            "summary": summary,
            "signals": signals,
            "top_performers": top_performers,
            "laggards": laggards,
            "fundamental_scores": fundamental_scores,
        }

    def _calculate_group_summary(self, symbols: list[str]) -> dict:
        """计算分组概览.

        Args:
            symbols: 股票代码列表

        Returns:
            概览统计

        """
        up_count = 0
        down_count = 0
        total_change = 0
        valid_count = 0

        for symbol in symbols:
            try:
                spot = self.provider.get_stock_spot(symbol)
                change_pct = spot.get("change_pct", 0)

                if change_pct > 0:
                    up_count += 1
                elif change_pct < 0:
                    down_count += 1

                total_change += change_pct
                valid_count += 1

            except Exception:
                continue

        avg_change = total_change / valid_count if valid_count > 0 else 0

        return {
            "up_count": up_count,
            "down_count": down_count,
            "avg_change": round(avg_change, 2),
            "total_count": len(symbols),
        }

    def _get_top_performers(self, symbols: list[str], top_n: int = 5) -> list[dict]:
        """获取表现最好的股票.

        Args:
            symbols: 股票代码列表
            top_n: 返回前 N 只

        Returns:
            表现最好的股票列表

        """
        performers = []

        for symbol in symbols:
            try:
                spot = self.provider.get_stock_spot(symbol)
                performers.append({
                    "symbol": symbol,
                    "name": spot.get("name", ""),
                    "price": spot.get("price"),
                    "change_pct": spot.get("change_pct", 0),
                })
            except Exception:
                continue

        # 按涨跌幅排序
        performers.sort(key=lambda x: x["change_pct"], reverse=True)

        return performers[:top_n]

    def _get_laggards(self, symbols: list[str], top_n: int = 5) -> list[dict]:
        """获取表现最差的股票.

        Args:
            symbols: 股票代码列表
            top_n: 返回前 N 只

        Returns:
            表现最差的股票列表

        """
        performers = []

        for symbol in symbols:
            try:
                spot = self.provider.get_stock_spot(symbol)
                performers.append({
                    "symbol": symbol,
                    "name": spot.get("name", ""),
                    "price": spot.get("price"),
                    "change_pct": spot.get("change_pct", 0),
                })
            except Exception:
                continue

        # 按涨跌幅排序（升序）
        performers.sort(key=lambda x: x["change_pct"])

        return performers[:top_n]

    def _calculate_fundamental_scores(self, symbols: list[str]) -> list[dict]:
        """计算基本面评分.

        Args:
            symbols: 股票代码列表

        Returns:
            基本面评分列表

        """
        scores = []

        for symbol in symbols:
            try:
                result = self.scoring.calculate_fundamental_score(symbol)

                # 获取基本信息
                spot = self.provider.get_stock_spot(symbol)

                scores.append({
                    "symbol": symbol,
                    "name": spot.get("name", ""),
                    "score": result["score"],
                    "components": result.get("components", {}),
                })

            except Exception:
                continue

        # 按评分排序
        scores.sort(key=lambda x: x["score"], reverse=True)

        return scores

    def get_signal_summary(self, signals: dict) -> dict:
        """获取信号汇总.

        Args:
            signals: 信号字典

        Returns:
            信号汇总

        """
        buy_list = signals.get("buy", [])
        hold_list = signals.get("hold", [])
        sell_list = signals.get("sell", [])

        # 统计各类信号
        summary = {
            "golden_cross": [],
            "oversold": [],
            "breakout": [],
            "death_cross": [],
            "overbought": [],
        }

        for stock in buy_list + hold_list + sell_list:
            for signal in stock.get("signals", []):
                signal_type = signal.get("type", "")

                if "golden_cross" in signal_type:
                    summary["golden_cross"].append(stock)
                elif "oversold" in signal_type:
                    summary["oversold"].append(stock)
                elif "breakout" in signal_type:
                    summary["breakout"].append(stock)
                elif "death_cross" in signal_type:
                    summary["death_cross"].append(stock)
                elif "overbought" in signal_type:
                    summary["overbought"].append(stock)

        return summary

    def analyze_from_longport_group(self, group_id: str) -> dict:
        """从 LongPort 分组 ID 分析.

        Args:
            group_id: LongPort 分组 ID

        Returns:
            分组分析结果

        """
        try:
            # 这里需要导入 LongPort 分组管理模块
            # 暂时返回空结果
            return {"error": "需要集成 LongPort 分组管理功能", "group_id": group_id}
        except Exception as e:
            return {"error": str(e), "group_id": group_id}

    def read_symbols_from_file(self, file_path: str) -> list[str]:
        """从文件读取股票代码.

        Args:
            file_path: 文件路径

        Returns:
            股票代码列表

        """
        symbols = []

        try:
            with pathlib.Path(file_path).open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # 支持多种格式：纯数字、带后缀等
                        symbols.append(line)

            return symbols

        except Exception:
            return []

    def analyze_stock_comprehensive(self, symbol: str) -> dict:
        """综合分析单只股票.

        Args:
            symbol: 股票代码

        Returns:
            综合分析结果

        """
        result = {
            "symbol": symbol,
            "basic": {},
            "peer_comparison": {},
            "business_composition": {},
            "dupont_analysis": {},
            "news": {},
        }

        # 获取基本信息
        try:
            spot = self.provider.get_stock_spot(symbol)
            result["basic"] = {
                "name": spot.get("name", ""),
                "price": spot.get("price"),
                "change_pct": spot.get("change_pct"),
            }
        except Exception as e:
            result["basic"] = {"error": str(e)}

        # 同行估值比较
        try:
            valuation_comp = self.valuation.get_peer_valuation_comparison(symbol)
            result["peer_comparison"]["valuation"] = valuation_comp
        except Exception as e:
            result["peer_comparison"]["valuation"] = {"error": str(e)}

        # 同行成长性比较
        try:
            growth_comp = self.growth.get_peer_growth_comparison(symbol)
            result["peer_comparison"]["growth"] = growth_comp
        except Exception as e:
            result["peer_comparison"]["growth"] = {"error": str(e)}

        # 主营构成分析
        try:
            business = self.financial.get_business_composition(symbol)
            result["business_composition"] = business
        except Exception as e:
            result["business_composition"] = {"error": str(e)}

        # 杜邦分析
        try:
            dupont = self.dupont.analyze_dupont(symbol)
            result["dupont_analysis"] = dupont
        except Exception as e:
            result["dupont_analysis"] = {"error": str(e)}

        # 获取新闻
        try:
            news = self.news.get_stock_news(symbol, limit=5)
            news_sentiment = self.news.analyze_news_sentiment(symbol, limit=5)
            result["news"] = {
                "latest": news.get("latest_news"),
                "sentiment": news_sentiment,
            }
        except Exception as e:
            result["news"] = {"error": str(e)}

        return result

    def analyze_group_with_peer_comparison(self, symbols: list[str], group_name: str | None = None) -> dict:
        """分析分组并包含同行比较.

        Args:
            symbols: 股票代码列表
            group_name: 分组名称

        Returns:
            增强的分组分析结果

        """
        # 基础分组分析
        base_result = self.analyze_group(symbols, group_name)

        # 添加同行比较数据
        peer_data = {}
        for symbol in symbols:
            try:
                # 估值比较
                valuation = self.valuation.get_peer_valuation_comparison(symbol)
                # 成长性比较
                growth = self.growth.get_peer_growth_comparison(symbol)
                # 杜邦分析
                dupont = self.dupont.analyze_dupont(symbol)

                peer_data[symbol] = {
                    "valuation": valuation,
                    "growth": growth,
                    "dupont": dupont,
                }
            except Exception:
                continue

        base_result["peer_comparison"] = peer_data

        return base_result

    def get_group_news_summary(self, symbols: list[str], limit_per_stock: int = 3) -> dict:
        """获取分组股票新闻汇总.

        Args:
            symbols: 股票代码列表
            limit_per_stock: 每只股票新闻条数

        Returns:
            新闻汇总结果

        """
        all_news = {}
        sentiment_summary = {"positive": 0, "negative": 0, "neutral": 0}

        for symbol in symbols:
            try:
                sentiment = self.news.analyze_news_sentiment(symbol, limit=limit_per_stock)
                all_news[symbol] = sentiment

                # 汇总情绪
                if not sentiment.get("error"):
                    sentiment_summary[sentiment.get("sentiment", "neutral")] += 1
            except Exception:
                continue

        return {
            "by_stock": all_news,
            "sentiment_summary": sentiment_summary,
            "overall_sentiment": self._get_overall_sentiment(sentiment_summary),
        }

    def _get_overall_sentiment(self, summary: dict) -> str:
        """获取整体情绪."""
        positive = summary.get("positive", 0)
        negative = summary.get("negative", 0)
        neutral = summary.get("neutral", 0)

        total = positive + negative + neutral
        if total == 0:
            return "数据不足"

        if positive > negative * 1.5:
            return "整体偏正面"
        if negative > positive * 1.5:
            return "整体偏负面"
        return "整体中性"
