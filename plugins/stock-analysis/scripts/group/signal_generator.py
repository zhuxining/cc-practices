# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""交易信号生成器.

为股票生成交易信号和建议。
"""

from technical.pattern_detector import PatternDetector
from technical.signal_scanner import SignalScanner


class TradingSignalGenerator:
    """交易信号生成器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化信号生成器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}
        self.scanner = SignalScanner(provider, config)
        self.detector = PatternDetector(self.config)

        # 阈值配置
        self.buy_threshold = config.get("buy_threshold", 7.0) if config else 7.0
        self.sell_threshold = config.get("sell_threshold", 3.0) if config else 3.0
        self.hold_threshold = config.get("hold_threshold", 5.0) if config else 5.0

    def analyze_stock(self, symbol: str) -> dict:
        """分析单只股票，生成交易信号.

        Args:
            symbol: 股票代码

        Returns:
            分析结果字典

        """
        # 扫描股票
        scan_result = self.scanner.scan_stock(symbol)

        if "error" in scan_result:
            return scan_result

        # 计算信号强度
        signals = scan_result.get("patterns", [])
        overall_score = self._calculate_signal_score(signals)

        # 生成建议
        recommendation = self._generate_recommendation(overall_score, signals)

        # 计算关键价位
        key_levels = self._calculate_key_levels(scan_result)

        return {
            "symbol": scan_result["symbol"],
            "name": scan_result["name"],
            "price": scan_result["price"],
            "change_pct": scan_result["change_pct"],
            "signals": signals,
            "overall_score": overall_score,
            "recommendation": recommendation["action"],
            "risk_level": recommendation["risk_level"],
            "reason": recommendation["reason"],
            "entry_zone": key_levels["entry_zone"],
            "target_zone": key_levels["target_zone"],
            "stop_loss": key_levels["stop_loss"],
        }

    def generate_group_signals(self, symbols: list[str]) -> dict:
        """生成分组交易建议.

        Args:
            symbols: 股票代码列表

        Returns:
            分组信号字典

        """
        buy_list = []
        hold_list = []
        sell_list = []

        for symbol in symbols:
            result = self.analyze_stock(symbol)

            if "error" in result:
                continue

            rec = result["recommendation"]

            if rec == "buy":
                buy_list.append(result)
            elif rec == "hold":
                hold_list.append(result)
            else:
                sell_list.append(result)

        # 按评分排序
        buy_list = sorted(buy_list, key=lambda x: x["overall_score"], reverse=True)
        sell_list = sorted(sell_list, key=lambda x: x["overall_score"])

        # 生成总结
        summary = self._generate_group_summary(buy_list, hold_list, sell_list)

        return {"buy": buy_list, "hold": hold_list, "sell": sell_list, "summary": summary}

    def _calculate_signal_score(self, signals: list[dict]) -> float:
        """计算综合信号评分.

        Args:
            signals: 信号列表

        Returns:
            综合评分 (0-10)

        """
        if not signals:
            return 5.0

        # 加权求和
        total_strength = sum(s.get("strength", 0) for s in signals)

        # 转换到 0-10 分制
        # strength 范围大约 -8 到 +8
        score = 5.0 + (total_strength / 8) * 5

        return round(max(0, min(10, score)), 2)

    def _generate_recommendation(self, score: float, signals: list[dict]) -> dict:
        """生成交易建议.

        Args:
            score: 综合评分
            signals: 信号列表

        Returns:
            建议字典

        """
        # 判断风险等级
        positive_signals = [s for s in signals if s.get("strength", 0) > 3]
        negative_signals = [s for s in signals if s.get("strength", 0) < -3]

        if negative_signals:
            risk_level = "极高" if len(negative_signals) >= 2 else "高"
        elif positive_signals:
            risk_level = "低"
        else:
            risk_level = "中"

        # 生成建议
        if score >= self.buy_threshold:
            action = "buy"
            reason = f"综合评分 {score}/10，多个看多信号"
        elif score <= self.sell_threshold:
            action = "sell"
            reason = f"综合评分 {score}/10，出现看空信号"
        else:
            action = "hold"
            reason = f"综合评分 {score}/10，建议观望"

        return {"action": action, "risk_level": risk_level, "reason": reason}

    def _calculate_key_levels(self, scan_result: dict) -> dict:
        """计算关键价位.

        Args:
            scan_result: 扫描结果

        Returns:
            关键价位字典

        """
        price = scan_result.get("price", 0)

        if price == 0:
            return {"entry_zone": "-", "target_zone": "-", "stop_loss": "-"}

        # 支撑位和压力位
        support = scan_result.get("support_levels", [])
        resistance = scan_result.get("resistance_levels", [])

        # 入场区间：支撑位附近
        if support:
            entry_low = min(support)
            entry_high = price
            entry_zone = f"{entry_low:.2f}-{entry_high:.2f}"
        else:
            entry_zone = f"{price * 0.98:.2f}-{price:.2f}"

        # 目标区间：压力位附近
        if resistance:
            target_low = price
            target_high = max(resistance)
            target_zone = f"{target_low:.2f}-{target_high:.2f}"
        else:
            target_zone = f"{price:.2f}-{price * 1.1:.2f}"

        # 止损位：最近支撑位下方
        stop_loss = min(support) * 0.97 if support else price * 0.95

        return {
            "entry_zone": entry_zone,
            "target_zone": target_zone,
            "stop_loss": f"{stop_loss:.2f}",
        }

    def _generate_group_summary(self, buy_list: list, hold_list: list, sell_list: list) -> str:
        """生成分组总结.

        Args:
            buy_list: 建议买入列表
            hold_list: 建议持有列表
            sell_list: 建议卖出列表

        Returns:
            总结字符串

        """
        total = len(buy_list) + len(hold_list) + len(sell_list)

        if total == 0:
            return "暂无分析结果"

        buy_ratio = len(buy_list) / total * 100

        if buy_ratio > 50:
            return f"市场机会较多，{len(buy_list)}只股票建议关注"
        if buy_ratio > 30:
            return f"市场温和偏多，{len(buy_list)}只股票值得关注"
        if buy_ratio > 10:
            return f"市场分化明显，{len(buy_list)}只股票存在机会"
        return "市场整体偏弱，建议谨慎操作"

    def get_signal_summary(self, signals: list[dict]) -> dict:
        """获取信号汇总.

        Args:
            signals: 信号列表

        Returns:
            信号汇总字典

        """
        summary = {
            "golden_cross": [],
            "death_cross": [],
            "oversold": [],
            "overbought": [],
            "breakout": [],
            "other": [],
        }

        for signal in signals:
            signal_type = signal.get("type", "")

            if "golden_cross" in signal_type:
                summary["golden_cross"].append(signal)
            elif "death_cross" in signal_type:
                summary["death_cross"].append(signal)
            elif "oversold" in signal_type:
                summary["oversold"].append(signal)
            elif "overbought" in signal_type:
                summary["overbought"].append(signal)
            elif "breakout" in signal_type:
                summary["breakout"].append(signal)
            else:
                summary["other"].append(signal)

        return summary
