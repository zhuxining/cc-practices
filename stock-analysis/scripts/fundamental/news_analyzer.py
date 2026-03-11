# /// script
# dependencies = [
#     "pandas>=3.0.0",
# ]
# ///

"""新闻分析模块.

获取和分析个股最新新闻资讯。
"""


class NewsAnalyzer:
    """新闻分析器."""

    def __init__(self, provider) -> None:
        """初始化新闻分析器.

        Args:
            provider: 数据提供者实例

        """
        self.provider = provider

    def get_stock_news(self, symbol: str, limit: int = 10) -> dict:
        """获取个股新闻.

        Args:
            symbol: 股票代码
            limit: 返回条数

        Returns:
            新闻分析结果

        """
        try:
            news_list = self.provider.get_stock_news(symbol, limit)

            if not news_list:
                return {"symbol": symbol, "error": "无新闻数据"}

            # 获取股票基本信息
            spot = self.provider.get_stock_spot(symbol)

            return {
                "symbol": symbol,
                "name": spot.get("name", ""),
                "news_count": len(news_list),
                "news": news_list,
                "latest_news": news_list[0] if news_list else None,
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def analyze_news_sentiment(self, symbol: str, limit: int = 10) -> dict:
        """分析新闻情绪（简化版）.

        Args:
            symbol: 股票代码
            limit: 分析条数

        Returns:
            情绪分析结果

        """
        try:
            news_data = self.get_stock_news(symbol, limit)

            if "error" in news_data:
                return news_data

            news_list = news_data["news"]

            # 简化的情绪分析（基于关键词）
            positive_keywords = ["利好", "增长", "突破", "上涨", "盈利", "回购", "增持"]
            negative_keywords = ["利空", "下跌", "亏损", "减持", "风险", "调查", "处罚"]

            positive_count = 0
            negative_count = 0

            for news in news_list:
                title = news.get("title", "")
                for keyword in positive_keywords:
                    if keyword in title:
                        positive_count += 1
                        break
                for keyword in negative_keywords:
                    if keyword in title:
                        negative_count += 1
                        break

            total = len(news_list)
            sentiment = "neutral"
            if positive_count > negative_count * 2:
                sentiment = "positive"
            elif negative_count > positive_count * 2:
                sentiment = "negative"

            return {
                "symbol": symbol,
                "name": news_data.get("name", ""),
                "total_news": total,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "sentiment": sentiment,
                "sentiment_text": self._get_sentiment_text(sentiment),
            }

        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    def _get_sentiment_text(self, sentiment: str) -> str:
        """获取情绪描述."""
        texts = {
            "positive": "整体情绪偏正面",
            "negative": "整体情绪偏负面",
            "neutral": "整体情绪中性",
        }
        return texts.get(sentiment, "情绪分析不足")

    def batch_get_news(self, symbols: list[str], limit: int = 5) -> dict:
        """批量获取多只股票新闻.

        Args:
            symbols: 股票代码列表
            limit: 每只股票返回条数

        Returns:
            批量新闻结果

        """
        results = {}

        for symbol in symbols:
            try:
                news_data = self.get_stock_news(symbol, limit)
                results[symbol] = news_data
            except Exception as e:
                results[symbol] = {"symbol": symbol, "error": str(e)}

        return results
