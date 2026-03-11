# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""技术信号扫描器.

扫描多只股票的技术信号。
"""

from technical.pattern_detector import PatternDetector


class SignalScanner:
    """技术信号扫描器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化信号扫描器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}
        self.detector = PatternDetector(config)

    def scan_stock(self, symbol: str, period: str = "daily", count: int = 100) -> dict:
        """扫描单只股票.

        Args:
            symbol: 股票代码
            period: 周期
            count: 数据条数

        Returns:
            扫描结果字典

        """
        try:
            # 获取 K线数据
            df = self.provider.get_stock_candlesticks(symbol, period=period, count=count)

            if df.empty:
                return {"symbol": symbol, "error": "无法获取数据"}

            # 获取实时行情
            spot = self.provider.get_stock_spot(symbol)

            # 检测形态
            patterns = self.detector.detect_patterns(df)

            # 获取支撑压力位
            levels = self.detector.get_support_resistance(df)

            return {
                "symbol": symbol,
                "name": spot.get("name", ""),
                "price": spot.get("price"),
                "change_pct": spot.get("change_pct"),
                "patterns": patterns,
                "support_levels": levels["support_levels"],
                "resistance_levels": levels["resistance_levels"],
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def scan_group(self, symbols: list[str], period: str = "daily", count: int = 100) -> list[dict]:
        """批量扫描股票.

        Args:
            symbols: 股票代码列表
            period: 周期
            count: 数据条数

        Returns:
            扫描结果列表

        """
        results = []

        for symbol in symbols:
            result = self.scan_stock(symbol, period, count)
            results.append(result)

        return results

    def find_golden_cross(self, symbols: list[str]) -> list[dict]:
        """查找出现金叉的股票.

        Args:
            symbols: 股票代码列表

        Returns:
            出现金叉的股票列表

        """
        results = []

        for symbol in symbols:
            try:
                df = self.provider.get_stock_candlesticks(symbol, period="daily", count=100)

                if df.empty:
                    continue

                patterns = self.detector.detect_patterns(df)

                # 筛选金叉信号
                golden_crosses = [
                    p for p in patterns if "cross" in p.get("type", "") and p.get("strength", 0) > 0
                ]

                if golden_crosses:
                    spot = self.provider.get_stock_spot(symbol)
                    results.append({
                        "symbol": symbol,
                        "name": spot.get("name", ""),
                        "price": spot.get("price"),
                        "change_pct": spot.get("change_pct"),
                        "signals": golden_crosses,
                    })

            except Exception:
                continue

        return results

    def find_oversold(self, symbols: list[str], rsi_threshold: float = 30) -> list[dict]:
        """查找超卖股票.

        Args:
            symbols: 股票代码列表
            rsi_threshold: RSI 阈值

        Returns:
            超卖股票列表

        """
        results = []

        for symbol in symbols:
            try:
                df = self.provider.get_stock_candlesticks(symbol, period="daily", count=100)

                if df.empty:
                    continue

                patterns = self.detector.detect_patterns(df)

                # 筛选超卖信号
                oversold = [p for p in patterns if p.get("type", "") == "rsi_oversold"]

                if oversold:
                    spot = self.provider.get_stock_spot(symbol)
                    results.append({
                        "symbol": symbol,
                        "name": spot.get("name", ""),
                        "price": spot.get("price"),
                        "change_pct": spot.get("change_pct"),
                        "signals": oversold,
                    })

            except Exception:
                continue

        return results

    def find_breakout(self, symbols: list[str]) -> list[dict]:
        """查找放量突破的股票.

        Args:
            symbols: 股票代码列表

        Returns:
            放量突破股票列表

        """
        results = []

        for symbol in symbols:
            try:
                df = self.provider.get_stock_candlesticks(symbol, period="daily", count=100)

                if df.empty:
                    continue

                patterns = self.detector.detect_patterns(df)

                # 筛选突破信号
                breakouts = [
                    p
                    for p in patterns
                    if "breakout" in p.get("type", "") and p.get("strength", 0) > 0
                ]

                if breakouts:
                    spot = self.provider.get_stock_spot(symbol)
                    results.append({
                        "symbol": symbol,
                        "name": spot.get("name", ""),
                        "price": spot.get("price"),
                        "change_pct": spot.get("change_pct"),
                        "signals": breakouts,
                    })

            except Exception:
                continue

        return results
