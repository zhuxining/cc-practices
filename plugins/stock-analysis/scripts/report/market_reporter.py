# /// script
# dependencies = [
#     "pandas>=3.0.0",
#     "jinja2>=3.1.0",
#     "pyyaml>=6.0",
# ]
# ///

"""市场报告生成器.

生成 A股市场整体报告。
"""

from pathlib import Path

from jinja2 import Template


class MarketReporter:
    """市场报告生成器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化报告生成器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}

        # 导入分析模块
        from market.market_snapshot import MarketSnapshot
        from market.sector_tracker import SectorTracker
        from market.sentiment_analyzer import SentimentAnalyzer

        self.snapshot = MarketSnapshot(provider)
        self.sentiment = SentimentAnalyzer(provider, config)
        self.tracker = SectorTracker(provider, config)

    def generate_data(self) -> dict:
        """生成报告数据.

        Returns:
            报告数据字典

        """
        # 获取市场快照
        snapshot_data = self.snapshot.generate()

        # 获取情绪分析
        sentiment_data = self.sentiment.analyze()

        # 获取热点板块
        hot_sectors = self.tracker.get_hot_sectors_detail()

        # 获取资金流向排行
        flow_ranking = self.tracker.get_sector_flow_ranking()

        return {
            "timestamp": snapshot_data["timestamp"],
            "indices": snapshot_data["indices"],
            "statistics": snapshot_data["statistics"],
            "sentiment": sentiment_data,
            "hot_sectors": hot_sectors,
            "flow_ranking": flow_ranking.head(10).to_dict("records")
            if not flow_ranking.empty
            else [],
        }

    def generate_markdown(self, data: dict | None = None) -> str:
        """生成 Markdown 格式报告.

        Args:
            data: 报告数据，如果为 None 则自动生成

        Returns:
            Markdown 格式的报告字符串

        """
        if data is None:
            data = self.generate_data()

        # 读取模板
        template_path = (
            Path(__file__).parent.parent.parent / "assets" / "templates" / "market_report.md.j2"
        )

        if template_path.exists():
            with Path(template_path).open(encoding="utf-8") as f:
                template_content = f.read()
            template = Template(template_content)
            return template.render(**data)

        # 如果模板不存在，使用内置模板
        return self._render_builtin_template(data)

    def _render_builtin_template(self, data: dict) -> str:
        """渲染内置模板."""
        lines = []

        # 标题
        lines.append("# A股市场日报")
        lines.append(f"\n**生成时间**：{data['timestamp']}\n")

        # 市场概览
        lines.append("## 📊 市场概览\n")
        lines.append("| 指数 | 点位 | 涨跌 |")
        lines.append("|------|------|------|")
        for idx in data["indices"]:
            change_str = f"+{idx['change']}%" if idx["change_pct"] > 0 else f"{idx['change']}%"
            arrow = "↑" if idx["change_pct"] > 0 else "↓"
            lines.append(f"| {idx['name']} | {idx['price']:,.2f} | {change_str} {arrow} |")

        stats = data["statistics"]

        lines.append(f"\n**总成交额**：{stats['total_turnover'] / 100000000:,.0f} 亿")

        # 市场情绪
        lines.append("\n## 🎭 市场情绪\n")
        sentiment = data["sentiment"]
        lines.append("| 指标 | 数值 | 状态 |")
        lines.append("|------|------|------|")
        lines.append(
            f"| 涨跌比 | {sentiment['breadth_ratio']} | {self._get_breadth_status(sentiment['breadth_ratio'])} |",
        )
        lines.append(
            f"| 涨停/跌停 | {stats['limit_up_count']}/{stats['limit_down_count']} | {self._get_limit_status(stats)} |",
        )
        lines.append(f"| 情绪评分 | {sentiment['overall_score']}/5 | {sentiment['status']} |")

        # 热点板块
        lines.append("\n## 🔥 热点板块 TOP5\n")
        lines.append("| 排名 | 板块 | 涨跌幅 | 净流入 | 领涨股 |")
        lines.append("|------|------|--------|--------|--------|")

        for sector in data["hot_sectors"][:5]:
            flow_str = (
                f"+{sector['flow_net']:.0f}亿"
                if sector.get("flow_net", 0) > 0
                else f"{sector.get('flow_net', 0):.0f}亿"
            )
            leading = sector.get("leading_stocks", [])
            leading_names = ", ".join([s["name"] for s in leading[:3]]) if leading else "-"
            lines.append(
                f"| {sector['rank']} | {sector['sector_name']} | +{sector['change_pct']}% | {flow_str} | {leading_names} |",
            )

        # 资金流向
        if data["flow_ranking"]:
            lines.append("\n## 💰 资金流向排行\n")
            lines.append("| 板块 | 主力净流入 | 解读 |")
            lines.append("|------|------------|------|")

            for item in data["flow_ranking"][:5]:
                flow = item.get("flow_net", 0)
                flow_str = f"+{flow:.0f}亿" if flow > 0 else f"{flow:.0f}亿"
                lines.append(
                    f"| {item['sector_name']} | {flow_str} | {self._get_flow_comment(flow)} |",
                )

        return "\n".join(lines)

    def _get_breadth_status(self, ratio: float) -> str:
        """获取涨跌比状态."""
        if ratio >= 2:
            return "偏多"
        if ratio >= 1:
            return "偏强"
        if ratio >= 0.5:
            return "偏弱"
        return "偏空"

    def _get_limit_status(self, stats: dict) -> str:
        """获取涨跌停状态."""
        ratio = stats["limit_up_count"] / max(stats["limit_down_count"], 1)
        if ratio >= 3:
            return "活跃"
        if ratio >= 1:
            return "正常"
        return "低迷"

    def _get_flow_comment(self, flow: float) -> str:
        """获取资金流向评论."""
        if flow > 50:
            return "持续流入"
        if flow > 0:
            return "逢低吸纳"
        if flow > -50:
            return "资金流出"
        return "大幅流出"

    def save_csv(self, data: dict, output_path: str) -> None:
        """保存为 CSV 格式.

        Args:
            data: 报告数据
            output_path: 输出文件路径

        """
        # 创建输出目录
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 将数据转换为 DataFrame
        snapshot = self.snapshot.to_dataframe()
        snapshot.to_csv(output_path, index=False, encoding="utf-8-sig")

    def save_markdown(self, data: dict, output_path: str) -> None:
        """保存为 Markdown 格式.

        Args:
            data: 报告数据
            output_path: 输出文件路径

        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate_markdown(data)

        with output_file.open("w", encoding="utf-8") as f:
            f.write(content)
