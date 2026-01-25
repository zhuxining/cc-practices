# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""千股千评模块.

获取市场整体评论情绪数据。
"""

import pandas as pd


class MarketComment:
    """千股千评分析器."""

    def __init__(self, provider) -> None:
        """初始化千股千评分析器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def get_market_comment(self) -> dict:
        """获取市场千股千评数据.

        Returns:
            千股千评分析结果

        """
        try:
            df = self.provider.get_market_comment()

            if df.empty:
                return {"error": "无千股千评数据"}

            # 获取最新数据
            latest = df.iloc[-1]

            return {
                "timestamp": latest.get("date") if "date" in latest else None,
                "multi_ratio": self._extract_multi_ratio(latest),
                "data": latest.to_dict(),
            }

        except Exception as e:
            return {"error": str(e)}

    def _extract_multi_ratio(self, row: pd.Series) -> dict | None:
        """提取多空比例."""
        # 尝试从不同列名中获取多空比例
        multi_columns = ["多空", "多空比例", "multi", "multi_ratio"]

        for col in multi_columns:
            if col in row:
                value = row[col]
                if pd.notna(value):
                    return {"raw": str(value)}

        return None

    def analyze_market_sentiment_from_comment(self) -> dict:
        """从千股千评分析市场情绪.

        Returns:
            市场情绪分析结果

        """
        try:
            comment_data = self.get_market_comment()

            if "error" in comment_data:
                return comment_data

            multi_ratio = comment_data.get("multi_ratio")

            if not multi_ratio:
                return {
                    "sentiment": "neutral",
                    "description": "无法从千股千评判断情绪",
                }

            # 解析多空比例（这里简化处理）
            raw = multi_ratio.get("raw", "")

            sentiment = "neutral"
            description = "多空平衡"

            if "多" in raw and "空" not in raw:
                sentiment = "positive"
                description = "市场情绪偏多"
            elif "空" in raw and "多" not in raw:
                sentiment = "negative"
                description = "市场情绪偏空"

            return {
                "sentiment": sentiment,
                "description": description,
                "raw_data": raw,
            }

        except Exception as e:
            return {"error": str(e)}
