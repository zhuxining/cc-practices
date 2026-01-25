# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""评分引擎.

计算股票的综合评分（技术面 + 基本面）。
"""

import pandas as pd


class ScoringEngine:
    """综合评分引擎."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化评分引擎.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}

        # 获取评分权重配置
        scoring_config = self.config.get("scoring", {})

        self.technical_weights = scoring_config.get(
            "technical",
            {"trend": 0.4, "momentum": 0.3, "volume": 0.3},
        )

        self.fundamental_weights = scoring_config.get(
            "fundamental",
            {"valuation": 0.3, "growth": 0.4, "quality": 0.3},
        )

        self.overall_weights = scoring_config.get("overall", {"technical": 0.6, "fundamental": 0.4})

    def calculate_technical_score(self, symbol: str) -> dict:
        """计算技术面评分.

        Args:
            symbol: 股票代码

        Returns:
            评分结果字典

        """
        try:
            # 获取 K线数据
            df = self.provider.get_stock_candlesticks(symbol, period="daily", count=100)

            if df.empty:
                return {"score": 5.0, "components": {}}

            # 计算各项指标
            trend_score = self._calculate_trend_score(df)
            momentum_score = self._calculate_momentum_score(df)
            volume_score = self._calculate_volume_score(df)

            # 加权求和
            overall_score = (
                trend_score * self.technical_weights["trend"]
                + momentum_score * self.technical_weights["momentum"]
                + volume_score * self.technical_weights["volume"]
            )

            return {
                "score": round(overall_score, 2),
                "components": {
                    "trend": round(trend_score, 2),
                    "momentum": round(momentum_score, 2),
                    "volume": round(volume_score, 2),
                },
            }

        except Exception:
            return {"score": 5.0, "components": {}}

    def _calculate_trend_score(self, df: pd.DataFrame) -> float:
        """计算趋势评分."""
        if len(df) < 20:
            return 5.0

        latest = df.iloc[-1]

        # MA 排列
        score = 5.0

        # 检查短期是否在长期之上
        if "ma_5" in df.columns and "ma_20" in df.columns:
            if pd.notna(latest["ma_5"]) and pd.notna(latest["ma_20"]):
                if latest["ma_5"] > latest["ma_20"]:
                    score += 1.0
                else:
                    score -= 1.0

        # 检查价格相对于 MA 的位置
        if "ma_20" in df.columns:
            if pd.notna(latest["close"]) and pd.notna(latest["ma_20"]):
                if latest["close"] > latest["ma_20"]:
                    score += 0.5

        # 检查趋势方向（最近10天）
        recent = df.tail(10)
        if len(recent) >= 2:
            start_price = recent.iloc[0]["close"]
            end_price = recent.iloc[-1]["close"]
            if end_price > start_price:
                score += 0.5

        return max(0, min(10, score))

    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """计算动量评分."""
        if len(df) < 20:
            return 5.0

        score = 5.0

        # RSI 评分
        if "rsi" in df.columns:
            latest_rsi = df.iloc[-1]["rsi"]
            if pd.notna(latest_rsi):
                if 40 <= latest_rsi <= 60:
                    score += 1.0  # 中性区域
                elif 30 <= latest_rsi < 40:
                    score += 0.5  # 偏弱但非超卖
                elif 60 < latest_rsi <= 70:
                    score += 0.5  # 偏强但非超买
                elif latest_rsi < 30:
                    score += 1.0  # 超卖反弹机会
                elif latest_rsi > 70:
                    score -= 1.0  # 超买风险

        # MACD 评分
        if "macd_hist" in df.columns:
            latest_hist = df.iloc[-1]["macd_hist"]
            if pd.notna(latest_hist):
                if latest_hist > 0:
                    score += 0.5
                else:
                    score -= 0.5

        return max(0, min(10, score))

    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """计算成交量评分."""
        if len(df) < 20:
            return 5.0

        score = 5.0

        # 量价关系
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        if (
            pd.notna(latest["close"])
            and pd.notna(prev["close"])
            and pd.notna(latest["volume"])
            and pd.notna(prev["volume"])
        ):
            price_change = (latest["close"] - prev["close"]) / prev["close"]
            volume_change = (
                (latest["volume"] - prev["volume"]) / prev["volume"] if prev["volume"] > 0 else 0
            )

            # 量价齐升
            if price_change > 0 and volume_change > 0:
                score += 1.5
            # 量价齐跌
            elif price_change < 0 and volume_change < 0:
                score -= 0.5
            # 价涨量缩
            elif price_change > 0 and volume_change < 0:
                score += 0.5
            # 价跌量增
            elif price_change < 0 and volume_change > 0:
                score -= 1.0

        return max(0, min(10, score))

    def calculate_fundamental_score(self, symbol: str) -> dict:
        """计算基本面评分.

        Args:
            symbol: 股票代码

        Returns:
            评分结果字典

        """
        try:
            # 获取财务摘要
            financial = self.provider.get_stock_financial_summary(symbol)

            # 计算各项指标
            valuation_score = self._calculate_valuation_score(financial)
            growth_score = self._calculate_growth_score(financial)
            quality_score = self._calculate_quality_score(financial)

            # 加权求和
            overall_score = (
                valuation_score * self.fundamental_weights["valuation"]
                + growth_score * self.fundamental_weights["growth"]
                + quality_score * self.fundamental_weights["quality"]
            )

            return {
                "score": round(overall_score, 2),
                "components": {
                    "valuation": round(valuation_score, 2),
                    "growth": round(growth_score, 2),
                    "quality": round(quality_score, 2),
                },
            }

        except Exception:
            return {"score": 5.0, "components": {}}

    def _calculate_valuation_score(self, financial: dict) -> float:
        """计算估值评分."""
        score = 5.0

        pe = financial.get("pe")
        pb = financial.get("pb")

        # PE 评分
        if pe is not None:
            if pe < 15:
                score += 2.0
            elif pe < 30:
                score += 1.0
            elif pe > 50:
                score -= 1.0

        # PB 评分
        if pb is not None:
            if pb < 1.5:
                score += 1.0
            elif pb < 3:
                score += 0.5
            elif pb > 5:
                score -= 1.0

        return max(0, min(10, score))

    def _calculate_growth_score(self, financial: dict) -> float:
        """计算成长评分."""
        # 这里简化处理，实际需要获取财报数据
        # 暂时返回中性评分
        return 5.0

    def _calculate_quality_score(self, financial: dict) -> float:
        """计算质量评分."""
        # 这里简化处理，实际需要获取财报数据
        # 暂时返回中性评分
        return 5.0

    def calculate_overall_score(
        self,
        symbol: str,
        technical_score: float | None = None,
        fundamental_score: float | None = None,
    ) -> dict:
        """计算综合评分.

        Args:
            symbol: 股票代码
            technical_score: 技术面评分（可选）
            fundamental_score: 基本面评分（可选）

        Returns:
            综合评分结果

        """
        if technical_score is None:
            technical_result = self.calculate_technical_score(symbol)
            technical_score = technical_result["score"]

        if fundamental_score is None:
            fundamental_result = self.calculate_fundamental_score(symbol)
            fundamental_score = fundamental_result["score"]

        # 加权求和
        overall_score = (
            technical_score * self.overall_weights["technical"]
            + fundamental_score * self.overall_weights["fundamental"]
        )

        return {
            "overall_score": round(overall_score, 2),
            "technical_score": round(technical_score, 2),
            "fundamental_score": round(fundamental_score, 2),
            "weights": self.overall_weights,
        }
