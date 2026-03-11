# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""市场情绪分析模块.

计算市场情绪指标和综合情绪评分。
"""

from datetime import datetime


class SentimentAnalyzer:
    """市场情绪分析器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化情绪分析器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}

        # 情绪权重配置
        self.weights = self.config.get(
            "sentiment_weights",
            {"breadth": 0.4, "volume": 0.3, "limit_up": 0.3},
        )

        # 情绪级别配置
        self.levels = self.config.get(
            "sentiment_levels",
            {
                "very_fearful": 2.0,
                "fearful": 3.0,
                "neutral": 4.0,
                "greedy": 4.5,
                "very_greedy": 5.0,
            },
        )

    def analyze(self) -> dict:
        """分析市场情绪.

        Returns:
            dict with keys:
            - breadth_ratio: 市场广度（涨跌比）
            - breadth_score: 广度评分
            - volume_ratio: 量比
            - volume_score: 量比评分
            - limit_up_ratio: 涨停比例
            - limit_up_score: 涨停评分
            - overall_score: 综合情绪评分 (0-5)
            - level: 情绪级别 (very_fearful, fearful, neutral, greedy, very_greedy)
            - status: 情绪状态描述
            - timestamp: 分析时间

        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取市场统计
        stats = self.provider.get_market_statistics()

        # 计算各项指标
        breadth = self._calculate_breadth(stats)
        volume_ratio = self._calculate_volume_ratio(stats)
        limit_up_ratio = self._calculate_limit_up_ratio(stats)

        # 计算综合评分
        overall_score = (
            breadth["score"] * self.weights["breadth"]
            + volume_ratio["score"] * self.weights["volume"]
            + limit_up_ratio["score"] * self.weights["limit_up"]
        )

        # 确定情绪级别
        level = self._get_sentiment_level(overall_score)

        return {
            "breadth_ratio": breadth["ratio"],
            "breadth_score": breadth["score"],
            "volume_ratio": volume_ratio["ratio"],
            "volume_score": volume_ratio["score"],
            "limit_up_ratio": limit_up_ratio["ratio"],
            "limit_up_score": limit_up_ratio["score"],
            "overall_score": round(overall_score, 2),
            "level": level["level"],
            "status": level["status"],
            "timestamp": timestamp,
        }

    def _calculate_breadth(self, stats: dict) -> dict:
        """计算市场广度.

        Args:
            stats: 市场统计数据

        Returns:
            dict with ratio and score

        """
        total = stats["total_count"]
        up = stats["up_count"]
        down = stats["down_count"]

        if total == 0:
            return {"ratio": 1.0, "score": 2.5}

        # 涨跌比
        ratio = up / down if down > 0 else 2.0

        # 评分 (0-5)
        # ratio < 0.5: 1分
        # ratio = 1: 2.5分
        # ratio > 2: 5分
        if ratio <= 0.5:
            score = 1.0
        elif ratio <= 1.0:
            score = 1.0 + (ratio - 0.5) * 3  # 1.0 -> 2.5
        elif ratio <= 2.0:
            score = 2.5 + (ratio - 1.0) * 1.5  # 2.5 -> 4.0
        else:
            score = min(4.0 + (ratio - 2.0) * 0.5, 5.0)  # 4.0 -> 5.0

        return {"ratio": round(ratio, 2), "score": score}

    def _calculate_volume_ratio(self, stats: dict) -> dict:
        """计算量比.

        Args:
            stats: 市场统计数据

        Returns:
            dict with ratio and score

        """
        # 这里简化处理，实际应该和20日均量比较
        # 暂时用涨停数作为成交量活跃度的代理指标
        turnover = stats["total_turnover"]

        # 假设正常成交额为 5000 亿
        normal_turnover = 500000000000

        if normal_turnover == 0:
            return {"ratio": 1.0, "score": 2.5}

        ratio = turnover / normal_turnover

        # 评分 (0-5)
        if ratio < 0.7:
            score = 1.0 + (ratio / 0.7) * 1.0  # 1.0 -> 2.0
        elif ratio < 1.0:
            score = 2.0 + ((ratio - 0.7) / 0.3) * 1.0  # 2.0 -> 3.0
        elif ratio < 1.5:
            score = 3.0 + ((ratio - 1.0) / 0.5) * 1.0  # 3.0 -> 4.0
        else:
            score = min(4.0 + ((ratio - 1.5) / 0.5) * 1.0, 5.0)  # 4.0 -> 5.0

        return {"ratio": round(ratio, 2), "score": score}

    def _calculate_limit_up_ratio(self, stats: dict) -> dict:
        """计算涨停比例.

        Args:
            stats: 市场统计数据

        Returns:
            dict with ratio and score

        """
        total = stats["total_count"]
        limit_up = stats["limit_up_count"]
        limit_down = stats["limit_down_count"]

        if total == 0:
            return {"ratio": 0.0, "score": 2.5}

        # 涨停比例
        ratio = (limit_up - limit_down) / total

        # 评分 (0-5)
        # ratio < -0.01: 1分
        # ratio = 0: 2.5分
        # ratio > 0.03: 5分
        if ratio < -0.01:
            score = max(1.0, 2.5 + (ratio + 0.01) * 150)
        elif ratio < 0:
            score = 2.5 + (ratio + 0.01) * 50
        elif ratio < 0.03:
            score = 2.5 + (ratio / 0.03) * 1.5
        else:
            score = min(4.0 + ((ratio - 0.03) / 0.02) * 1.0, 5.0)

        return {"ratio": round(ratio, 4), "score": score}

    def _get_sentiment_level(self, score: float) -> dict:
        """根据评分确定情绪级别.

        Args:
            score: 情绪评分

        Returns:
            dict with level and status

        """
        if score <= self.levels["very_fearful"]:
            return {"level": "very_fearful", "status": "极度恐慌"}
        if score <= self.levels["fearful"]:
            return {"level": "fearful", "status": "恐慌"}
        if score <= self.levels["neutral"]:
            return {"level": "neutral", "status": "中性"}
        if score <= self.levels["greedy"]:
            return {"level": "greedy", "status": "贪婪"}
        return {"level": "very_greedy", "status": "极度贪婪"}
