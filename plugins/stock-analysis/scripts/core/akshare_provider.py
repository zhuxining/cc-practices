# /// script
# dependencies = [
#     "pandas>=3.0.0",
#     "numpy>=1.24.0",
#     "akshare>=1.12.0",
#     "python-dateutil>=2.8.0",
#     "requests>=2.31.0",
# ]
# ///

"""AKShare 数据提供者.

封装 AKShare 库，提供 A股数据获取能力。
"""

from datetime import datetime
import time

import akshare as ak
import pandas as pd


class AKShareProvider:
    """AKShare 数据提供者."""

    def __init__(self, timeout: int = 60, retry_times: int = 3, retry_delay: int = 2) -> None:
        """初始化 AKShare 数据提供者.

        Args:
            timeout: 请求超时时间（秒）
            retry_times: 重试次数
            retry_delay: 重试延迟（秒）

        """
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delay = retry_delay

    def _fetch_with_retry(self, fetch_func, *args, **kwargs):
        """带重试的数据获取.

        Args:
            fetch_func: 数据获取函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            pd.DataFrame: 获取的数据

        """
        for attempt in range(self.retry_times):
            try:
                return fetch_func(*args, **kwargs)
            except Exception:
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
        return None

    # ==================== 指数数据 ====================

    def get_indices_snapshot(self) -> pd.DataFrame:
        """获取主要指数实时行情.

        Returns:
            DataFrame with columns:
            - code: 指数代码
            - name: 指数名称
            - price: 当前点位
            - change: 涨跌点数
            - change_pct: 涨跌幅(%)
            - volume: 成交量
            - turnover: 成交额
            - timestamp: 更新时间

        """
        try:
            # 获取指数实时行情
            df = self._fetch_with_retry(ak.stock_zh_index_spot_em)

            # 筛选主要指数
            major_indices = ["sh000001", "sz399001", "sz399006", "sh000688"]
            df = df[df["代码"].isin(major_indices)].copy()

            # 重命名列
            df = df.rename(
                columns={
                    "代码": "code",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌额": "change",
                    "涨跌幅": "change_pct",
                    "成交量": "volume",
                    "成交额": "turnover",
                },
            )

            # 添加时间戳
            df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 确保数值类型
            numeric_cols = ["price", "change", "change_pct", "volume", "turnover"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df[
                ["code", "name", "price", "change", "change_pct", "volume", "turnover", "timestamp"]
            ]

        except Exception as e:
            msg = f"获取指数数据失败: {e}"
            raise RuntimeError(msg) from e

    def get_index_history(
        self,
        symbol: str,
        period: str = "daily",
        count: int = 100,
    ) -> pd.DataFrame:
        """获取指数历史数据.

        Args:
            symbol: 指数代码（如 sh000001）
            period: 周期 (daily, weekly, monthly)
            count: 数据条数

        Returns:
            DataFrame with OHLCV data

        """
        try:
            # 转换代码格式
            akshare_code = symbol.replace("sh", "s").replace("sz", "s")

            # period 映射
            period_map = {"daily": "日k", "weekly": "周k", "monthly": "月k"}
            ak_period = period_map.get(period, "日k")

            df = self._fetch_with_retry(
                ak.index_zh_a_hist,
                symbol=akshare_code[1:],
                period=ak_period,
            )

            # 取最近 count 条
            df = df.tail(count).copy()

            # 重命名列
            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "turnover",
                },
            )

            # 确保数值类型
            numeric_cols = ["open", "high", "low", "close", "volume", "turnover"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df[["date", "open", "high", "low", "close", "volume", "turnover"]]

        except Exception as e:
            msg = f"获取指数历史数据失败: {e}"
            raise RuntimeError(msg) from e

    # ==================== 市场统计 ====================

    def get_market_statistics(self) -> dict:
        """获取市场统计数据.

        Returns:
            dict with keys:
            - total_count: 总股票数
            - up_count: 上涨家数
            - down_count: 下跌家数
            - unchanged_count: 平盘家数
            - limit_up_count: 涨停家数
            - limit_down_count: 跌停家数
            - total_turnover: 总成交额
            - timestamp: 更新时间

        """
        try:
            # 获取所有 A股实时行情
            df = self._fetch_with_retry(ak.stock_zh_a_spot_em)

            # 统计涨跌
            up_count = len(df[df["涨跌幅"] > 0])
            down_count = len(df[df["涨跌幅"] < 0])
            unchanged_count = len(df[df["涨跌幅"] == 0])

            # 统计涨跌停（接近 10% 或 20%）
            limit_up_count = len(df[df["涨跌幅"] >= 9.9])
            limit_down_count = len(df[df["涨跌幅"] <= -9.9])

            # 总成交额
            total_turnover = df["成交额"].sum() if "成交额" in df.columns else 0

            return {
                "total_count": len(df),
                "up_count": up_count,
                "down_count": down_count,
                "unchanged_count": unchanged_count,
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "total_turnover": total_turnover,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            msg = f"获取市场统计失败: {e}"
            raise RuntimeError(msg) from e

    # ==================== 板块数据 ====================

    def get_sector_ranking(self, sort_by: str = "change_pct") -> pd.DataFrame:
        """获取行业板块排行.

        Args:
            sort_by: 排序字段 (change_pct, turnover, volume, flow_net)

        Returns:
            DataFrame with columns:
            - sector_code: 板块代码
            - sector_name: 板块名称
            - change_pct: 涨跌幅
            - turnover: 成交额
            - volume: 成交量
            - turnover_rate: 换手率
            - leading_stocks: 领涨股票
            - rank: 排名

        """
        try:
            # 获取行业板块实时行情
            df = self._fetch_with_retry(ak.stock_board_industry_name_em)

            # 重命名列
            df = df.rename(
                columns={
                    "板块代码": "sector_code",
                    "板块名称": "sector_name",
                    "最新价": "price",
                    "涨跌额": "change",
                    "涨跌幅": "change_pct",
                    "成交量": "volume",
                    "成交额": "turnover",
                    "换手率": "turnover_rate",
                    "领涨股票": "leading_stocks",
                },
            )

            # 确保数值类型
            numeric_cols = ["price", "change", "change_pct", "volume", "turnover", "turnover_rate"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # 排序
            df = df.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
            df["rank"] = df.index + 1

            return df[
                [
                    "sector_code",
                    "sector_name",
                    "change_pct",
                    "turnover",
                    "volume",
                    "turnover_rate",
                    "leading_stocks",
                    "rank",
                ]
            ]

        except Exception as e:
            msg = f"获取板块排行失败: {e}"
            raise RuntimeError(msg) from e

    def get_sector_constituents(self, sector_name: str, top_n: int = 20) -> pd.DataFrame:
        """获取板块成分股.

        Args:
            sector_name: 板块名称
            top_n: 返回前 N 只股票

        Returns:
            DataFrame with columns:
            - symbol: 股票代码
            - name: 股票名称
            - price: 现价
            - change_pct: 涨跌幅
            - volume: 成交量
            - turnover: 成交额
            - market_cap: 总市值

        """
        try:
            # 获取板块成分股
            df = self._fetch_with_retry(ak.stock_board_industry_cons_em, symbol=sector_name)

            # 按涨跌幅排序
            df = df.sort_values(by="涨跌幅", ascending=False).head(top_n).copy()

            # 重命名列
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "change_pct",
                    "成交量": "volume",
                    "成交额": "turnover",
                    "总市值": "market_cap",
                },
            )

            # 确保数值类型
            numeric_cols = ["price", "change_pct", "volume", "turnover", "market_cap"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df[["symbol", "name", "price", "change_pct", "volume", "turnover", "market_cap"]]

        except Exception as e:
            msg = f"获取板块成分股失败: {e}"
            raise RuntimeError(msg) from e

    def get_sector_capital_flow(self) -> pd.DataFrame:
        """获取板块资金流向.

        Returns:
            DataFrame with columns:
            - sector_name: 板块名称
            - flow_in: 主力流入
            - flow_out: 主力流出
            - flow_net: 净流入
            - flow_net_pct: 净流入占比
            - rank: 排名

        """
        try:
            # 获取行业资金流向
            df = self._fetch_with_retry(ak.stock_sector_fund_flow_rank)

            # 重命名列
            df = df.rename(
                columns={
                    "名称": "sector_name",
                    "净流入": "flow_net",
                    "净流入率": "flow_net_pct",
                    "主力流入": "flow_in",
                    "主力流出": "flow_out",
                },
            )

            # 确保数值类型
            numeric_cols = ["flow_in", "flow_out", "flow_net", "flow_net_pct"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # 按净流入排序
            df = df.sort_values(by="flow_net", ascending=False).reset_index(drop=True)
            df["rank"] = df.index + 1

            return df[["sector_name", "flow_in", "flow_out", "flow_net", "flow_net_pct", "rank"]]

        except Exception as e:
            msg = f"获取板块资金流向失败: {e}"
            raise RuntimeError(msg) from e

    # ==================== 个股数据 ====================

    def get_stock_spot(self, symbol: str) -> dict:
        """获取个股实时行情.

        Args:
            symbol: 股票代码

        Returns:
            dict with keys:
            - symbol: 股票代码
            - name: 股票名称
            - price: 现价
            - change: 涨跌额
            - change_pct: 涨跌幅
            - volume: 成交量
            - turnover: 成交额
            - market_cap: 总市值
            - circulating_cap: 流通市值

        """
        try:
            # 获取所有 A股实时行情
            df = self._fetch_with_retry(ak.stock_zh_a_spot_em)

            # 筛选目标股票
            stock = df[df["代码"] == symbol]

            if stock.empty:
                msg = f"股票 {symbol} 未找到"
                raise ValueError(msg)

            stock = stock.iloc[0]

            return {
                "symbol": stock["代码"],
                "name": stock["名称"],
                "price": float(stock["最新价"]) if pd.notna(stock["最新价"]) else None,
                "change": float(stock["涨跌额"]) if pd.notna(stock["涨跌额"]) else None,
                "change_pct": float(stock["涨跌幅"]) if pd.notna(stock["涨跌幅"]) else None,
                "volume": float(stock["成交量"]) if pd.notna(stock["成交量"]) else None,
                "turnover": float(stock["成交额"]) if pd.notna(stock["成交额"]) else None,
                "market_cap": float(stock["总市值"]) if pd.notna(stock["总市值"]) else None,
                "circulating_cap": float(stock["流通市值"])
                if pd.notna(stock["流通市值"])
                else None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        except Exception as e:
            msg = f"获取个股行情失败: {e}"
            raise RuntimeError(msg) from e

    def get_stock_candlesticks(
        self,
        symbol: str,
        period: str = "daily",
        adjust: str = "qfq",
        count: int = 100,
    ) -> pd.DataFrame:
        """获取个股 K线数据.

        Args:
            symbol: 股票代码
            period: 周期 (daily, weekly, monthly)
            adjust: 复权类型 (qfq: 前复权, hfq: 后复权, "": 不复权)
            count: 数据条数

        Returns:
            DataFrame with OHLCV data

        """
        try:
            # period 映射
            period_map = {
                "daily": "日k",
                "weekly": "周k",
                "monthly": "月k",
                "5min": "5分钟",
                "15min": "15分钟",
                "30min": "30分钟",
                "60min": "60分钟",
            }
            ak_period = period_map.get(period, "日k")

            # adjust 映射
            adjust_map = {"qfq": "qfq", "hfq": "hfq", "": ""}
            ak_adjust = adjust_map.get(adjust, "qfq")

            df = self._fetch_with_retry(
                ak.stock_zh_a_hist,
                symbol=symbol,
                period=ak_period,
                adjust=ak_adjust,
            )

            # 取最近 count 条
            df = df.tail(count).copy()

            # 重命名列
            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "turnover",
                },
            )

            # 确保数值类型
            numeric_cols = ["open", "high", "low", "close", "volume", "turnover"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df[["date", "open", "high", "low", "close", "volume", "turnover"]]

        except Exception as e:
            msg = f"获取 K线数据失败: {e}"
            raise RuntimeError(msg) from e

    # ==================== 财务数据 ====================

    def get_stock_financial_summary(self, symbol: str) -> dict:
        """获取个股财务摘要.

        Args:
            symbol: 股票代码

        Returns:
            dict with keys:
            - pe: 市盈率
            - pb: 市净率
            - ps: 市销率
            - market_cap: 总市值
            - circulating_cap: 流通市值

        """
        try:
            # 获取个股信息
            info = self._fetch_with_retry(ak.stock_individual_info_em, symbol=symbol)

            # 解析为字典
            result = {}
            for _, row in info.iterrows():
                key = row["item"]
                value = row["value"]
                result[key] = value

            return {
                "pe": self._parse_number(result.get("市盈率-动态")),
                "pb": self._parse_number(result.get("市净率")),
                "ps": self._parse_number(result.get("市销率")),
                "market_cap": self._parse_number(result.get("总市值")),
                "circulating_cap": self._parse_number(result.get("流通市值")),
            }

        except Exception as e:
            msg = f"获取财务摘要失败: {e}"
            raise RuntimeError(msg) from e

    def get_stock_growth_comparison(self, symbol: str) -> pd.DataFrame:
        """获取同行成长性比较.

        Args:
            symbol: 股票代码

        Returns:
            DataFrame with columns:
            - name: 股票名称
            - code: 股票代码
            - revenue_growth: 营收增长率
            - profit_growth: 利润增长率
            - 其他成长性指标

        """
        try:
            df = self._fetch_with_retry(ak.stock_zh_growth_comparison_em, symbol=symbol)

            # 重命名列
            df = df.rename(
                columns={
                    "名称": "name",
                    "代码": "code",
                    "营收增长率": "revenue_growth",
                    "净利润增长率": "profit_growth",
                    "ROE": "roe",
                },
            )

            # 确保数值类型
            numeric_cols = ["revenue_growth", "profit_growth", "roe"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

        except Exception as e:
            msg = f"获取同行成长性比较失败: {e}"
            raise RuntimeError(msg) from e

    def get_stock_valuation_comparison(self, symbol: str) -> pd.DataFrame:
        """获取同行估值比较.

        Args:
            symbol: 股票代码

        Returns:
            DataFrame with columns:
            - name: 股票名称
            - code: 股票代码
            - pe: 市盈率
            - pb: 市净率
            - ps: 市销率
            - market_cap: 总市值

        """
        try:
            df = self._fetch_with_retry(ak.stock_zh_valuation_comparison_em, symbol=symbol)

            # 重命名列
            df = df.rename(
                columns={
                    "名称": "name",
                    "代码": "code",
                    "市盈率-动态": "pe",
                    "市净率": "pb",
                    "市销率": "ps",
                    "总市值": "market_cap",
                },
            )

            # 确保数值类型
            numeric_cols = ["pe", "pb", "ps", "market_cap"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

        except Exception as e:
            msg = f"获取同行估值比较失败: {e}"
            raise RuntimeError(msg) from e

    def get_stock_dupont_comparison(self, symbol: str) -> pd.DataFrame:
        """获取同行杜邦分析比较.

        Args:
            symbol: 股票代码

        Returns:
            DataFrame with columns:
            - name: 股票名称
            - code: 股票代码
            - roe: 净资产收益率
            - net_profit_margin: 销售净利率
            - asset_turnover: 总资产周转率
            - equity_multiplier: 权益乘数

        """
        try:
            df = self._fetch_with_retry(ak.stock_zh_dupont_comparison_em, symbol=symbol)

            # 重命名列
            df = df.rename(
                columns={
                    "名称": "name",
                    "代码": "code",
                    "ROE": "roe",
                    "销售净利率": "net_profit_margin",
                    "总资产周转率": "asset_turnover",
                    "权益乘数": "equity_multiplier",
                },
            )

            # 确保数值类型
            numeric_cols = ["roe", "net_profit_margin", "asset_turnover", "equity_multiplier"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

        except Exception as e:
            msg = f"获取同行杜邦分析比较失败: {e}"
            raise RuntimeError(msg) from e

    def get_stock_business_composition(self, symbol: str) -> pd.DataFrame:
        """获取主营构成.

        Args:
            symbol: 股票代码

        Returns:
            DataFrame with columns:
            - product_name: 产品名称
            - revenue: 收入
            - revenue_ratio: 收入占比
            - profit: 利润
            - profit_ratio: 利润占比

        """
        try:
            df = self._fetch_with_retry(ak.stock_zygc_em, symbol=symbol)

            # 重命名列
            df = df.rename(
                columns={
                    "主营构成": "product_name",
                    "主营收入(元)": "revenue",
                    "收入占比": "revenue_ratio",
                    "主营利润(元)": "profit",
                    "利润占比": "profit_ratio",
                },
            )

            # 确保数值类型
            numeric_cols = ["revenue", "revenue_ratio", "profit", "profit_ratio"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

        except Exception as e:
            msg = f"获取主营构成失败: {e}"
            raise RuntimeError(msg) from e

    def get_market_comment(self) -> pd.DataFrame:
        """获取千股千评.

        Returns:
            DataFrame with columns:
            - date: 日期
            - multi: 多空比例
            - other indicators

        """
        try:
            df = self._fetch_with_retry(ak.stock_comment_em)

            # 确保数值类型
            numeric_cols = df.select_dtypes(include=["number"]).columns
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

        except Exception as e:
            msg = f"获取千股千评失败: {e}"
            raise RuntimeError(msg) from e

    def get_stock_news(self, symbol: str, limit: int = 10) -> list[dict]:
        """获取个股新闻.

        Args:
            symbol: 股票代码
            limit: 返回条数

        Returns:
            新闻列表, 每个元素包含:
            - title: 新闻标题
            - time: 发布时间
            - source: 来源

        """
        try:
            df = self._fetch_with_retry(ak.stock_news_em, symbol=symbol)

            # 取前 limit 条
            df = df.head(limit).copy()

            # 转换为字典列表
            news_list = []
            for _, row in df.iterrows():
                news_list.append({
                    "title": row.get("新闻标题", ""),
                    "time": row.get("发布时间", ""),
                    "source": row.get("文章来源", ""),
                    "url": row.get("新闻链接", ""),
                })

            return news_list

        except Exception as e:
            msg = f"获取个股新闻失败: {e}"
            raise RuntimeError(msg) from e

    def _parse_number(self, value: str | None) -> float | None:
        """解析数字字符串."""
        if value is None or value == "-":
            return None
        try:
            # 移除单位
            value = str(value).replace("万", "").replace("亿", "").replace("%", "").strip()
            return float(value)
        except (ValueError, TypeError):
            return None
