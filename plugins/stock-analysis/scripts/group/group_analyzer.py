# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""分组分析器.

分析自选分组中的股票。
"""

import pathlib

from fundamental.financial_analyzer import FinancialAnalyzer

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
