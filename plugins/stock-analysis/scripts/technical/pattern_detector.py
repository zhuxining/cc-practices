# /// script
# dependencies = [
#     "pandas>=3.0.0",
#     "numpy>=1.24.0",
#     "ta-lib>=0.6.8",
# ]
# ///

"""
技术形态识别模块

识别 K线形态和技术信号。
"""

import pandas as pd
import talib


class PatternDetector:
    """技术形态识别器"""

    def __init__(self, config: dict | None = None):
        """
        初始化形态识别器

        Args:
            config: 配置字典
        """
        self.config = config or {}

        # 获取指标参数
        self.ma_periods = self.config.get("ma", {}).get("periods", [5, 10, 20, 60])
        self.macd_params = self.config.get("macd", {"fast": 12, "slow": 26, "signal": 9})
        self.rsi_params = self.config.get("rsi", {"period": 14, "oversold": 30, "overbought": 70})
        self.bollinger_params = self.config.get("bollinger", {"period": 20, "std_dev": 2.0})

    def detect_patterns(self, df: pd.DataFrame) -> list[dict]:
        """
        检测所有技术形态

        Args:
            df: K线数据 (包含 OHLCV)

        Returns:
            形态列表
        """
        patterns = []

        # 计算技术指标
        df = self._calculate_indicators(df)

        if df.empty or len(df) < self.ma_periods[-1]:
            return patterns

        # 获取最新数据
        df.iloc[-1]
        df.iloc[-2] if len(df) >= 2 else None

        # 检测金叉/死叉
        patterns.extend(self._detect_crosses(df))

        # 检测超买超卖
        patterns.extend(self._detect_overbought_oversold(df))

        # 检测突破
        patterns.extend(self._detect_breakout(df))

        # 检测 K线形态
        patterns.extend(self._detect_candlestick_patterns(df))

        return patterns

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        df = df.copy()

        # 移动平均线
        for period in self.ma_periods:
            df[f"ma_{period}"] = talib.MA(df["close"], timeperiod=period)

        # MACD
        macd, macdsignal, macdhist = talib.MACD(
            df["close"],
            fastperiod=self.macd_params["fast"],
            slowperiod=self.macd_params["slow"],
            signalperiod=self.macd_params["signal"],
        )
        df["macd"] = macd
        df["macd_signal"] = macdsignal
        df["macd_hist"] = macdhist

        # RSI
        df["rsi"] = talib.RSI(df["close"], timeperiod=self.rsi_params["period"])

        # 布林带
        upper, middle, lower = talib.BBANDS(
            df["close"],
            timeperiod=self.bollinger_params["period"],
            nbdevup=self.bollinger_params["std_dev"],
            nbdevdn=self.bollinger_params["std_dev"],
        )
        df["bb_upper"] = upper
        df["bb_middle"] = middle
        df["bb_lower"] = lower

        # ATR
        df["atr"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=14)

        return df

    def _detect_crosses(self, df: pd.DataFrame) -> list[dict]:
        """检测金叉和死叉"""
        patterns = []

        if len(df) < 2:
            return patterns

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # MA 金叉
        for i, period in enumerate(self.ma_periods[:-1]):
            fast_period = period
            slow_period = self.ma_periods[i + 1]

            fast_col = f"ma_{fast_period}"
            slow_col = f"ma_{slow_period}"

            if fast_col in df.columns and slow_col in df.columns:
                # 金叉：快线上穿慢线
                if prev[fast_col] <= prev[slow_col] and latest[fast_col] > latest[slow_col]:
                    patterns.append({
                        "type": "golden_cross",
                        "name": f"MA{fast_period}金叉MA{slow_period}",
                        "strength": 8,
                        "reason": f"{fast_period}日线上穿{slow_period}日线",
                    })
                # 死叉：快线下穿慢线
                elif prev[fast_col] >= prev[slow_col] and latest[fast_col] < latest[slow_col]:
                    patterns.append({
                        "type": "death_cross",
                        "name": f"MA{fast_period}死叉MA{slow_period}",
                        "strength": -8,
                        "reason": f"{fast_period}日线下穿{slow_period}日线",
                    })

        # MACD 金叉
        if (
            "macd" in df.columns
            and "macd_signal" in df.columns
            and pd.notna(latest["macd"])
            and pd.notna(latest["macd_signal"])
            and pd.notna(prev["macd"])
            and pd.notna(prev["macd_signal"])
        ):
            if prev["macd"] <= prev["macd_signal"] and latest["macd"] > latest["macd_signal"]:
                patterns.append({
                    "type": "macd_golden_cross",
                    "name": "MACD金叉",
                    "strength": 6,
                    "reason": "MACD快线上穿慢线",
                })
            elif prev["macd"] >= prev["macd_signal"] and latest["macd"] < latest["macd_signal"]:
                patterns.append({
                    "type": "macd_death_cross",
                    "name": "MACD死叉",
                    "strength": -6,
                    "reason": "MACD快线下穿慢线",
                })

        return patterns

    def _detect_overbought_oversold(self, df: pd.DataFrame) -> list[dict]:
        """检测超买超卖"""
        patterns = []

        if len(df) < 2 or "rsi" not in df.columns:
            return patterns

        latest = df.iloc[-1]
        rsi = latest["rsi"]

        if pd.isna(rsi):
            return patterns

        # 超卖
        if rsi < self.rsi_params["oversold"]:
            patterns.append({
                "type": "rsi_oversold",
                "name": f"RSI超卖({rsi:.0f})",
                "strength": 7,
                "reason": f"RSI={rsi:.0f}，接近超卖区域",
            })
        # 超买
        elif rsi > self.rsi_params["overbought"]:
            patterns.append({
                "type": "rsi_overbought",
                "name": f"RSI超买({rsi:.0f})",
                "strength": -7,
                "reason": f"RSI={rsi:.0f}，进入超买区域",
            })

        return patterns

    def _detect_breakout(self, df: pd.DataFrame) -> list[dict]:
        """检测突破"""
        patterns = []

        if len(df) < 2:
            return patterns

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # 放量突破
        if "volume" in df.columns and pd.notna(latest["volume"]) and pd.notna(prev["volume"]):
            volume_ratio = latest["volume"] / prev["volume"] if prev["volume"] > 0 else 1

            # 价格上涨且成交量放大
            if latest["close"] > prev["close"] and volume_ratio > 1.5:
                patterns.append({
                    "type": "volume_breakout",
                    "name": "放量突破",
                    "strength": 7,
                    "reason": f"成交量为前{volume_ratio:.1f}倍，价格突破",
                })

        # 布林带突破
        if (
            "bb_upper" in df.columns
            and "bb_lower" in df.columns
            and pd.notna(latest["bb_upper"])
            and pd.notna(latest["close"])
        ):
            if latest["close"] > latest["bb_upper"]:
                patterns.append({
                    "type": "bollinger_breakout_upper",
                    "name": "突破布林带上轨",
                    "strength": 7,
                    "reason": "价格突破布林带上轨，强势特征",
                })
            elif latest["close"] < latest["bb_lower"]:
                patterns.append({
                    "type": "bollinger_breakout_lower",
                    "name": "跌破布林带下轨",
                    "strength": -7,
                    "reason": "价格跌破布林带下轨，弱势特征",
                })

        return patterns

    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> list[dict]:
        """检测 K线形态"""
        patterns = []

        if len(df) < 3:
            return patterns

        open_prices = df["open"].to_numpy()
        high_prices = df["high"].to_numpy()
        low_prices = df["low"].to_numpy()
        close_prices = df["close"].to_numpy()

        # 检测各种 K线形态

        for pattern_key, pattern_func in [
            ("doji", talib.CDLDOJI),
            ("hammer", talib.CDLHAMMER),
            ("morning_star", talib.CDLMORNINGSTAR),
            ("evening_star", talib.CDLEVENINGSTAR),
            ("engulfing", talib.CDLENGULFING),
        ]:
            try:
                result = pattern_func(open_prices, high_prices, low_prices, close_prices)
                latest_signal = result[-1]

                if latest_signal != 0:
                    # 看涨形态
                    if latest_signal > 0:
                        patterns.append({
                            "type": f"bullish_{pattern_key}",
                            "name": f"看涨-{pattern_func.__name__.replace('CDL', '')}",
                            "strength": 5,
                            "reason": "出现看涨 K线形态",
                        })
                    # 看跌形态
                    else:
                        patterns.append({
                            "type": f"bearish_{pattern_key}",
                            "name": f"看跌-{pattern_func.__name__.replace('CDL', '')}",
                            "strength": -5,
                            "reason": "出现看跌 K线形态",
                        })
            except Exception:
                pass

        return patterns

    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> dict:
        """
        识别支撑位和压力位

        Args:
            df: K线数据
            window: 窗口大小

        Returns:
            dict with support_levels and resistance_levels
        """
        if df.empty or len(df) < window:
            return {"support_levels": [], "resistance_levels": []}

        recent = df.tail(window)

        # 简单方法:找出最近的低点和高点
        lows = recent["low"].to_numpy()
        highs = recent["high"].to_numpy()

        # 支撑位:低点
        support_levels = sorted({round(v, 2) for v in lows})[-3:]

        # 压力位:高点
        resistance_levels = sorted({round(v, 2) for v in highs})[-3:]

        return {"support_levels": support_levels, "resistance_levels": resistance_levels}
