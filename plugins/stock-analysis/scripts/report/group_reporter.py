# /// script
# dependencies = [
#     "pandas>=3.0.0",
#     "jinja2>=3.1.0",
# ]
# ///

"""分组报告生成器.

生成分组分析报告。
"""

from datetime import datetime
from pathlib import Path

from jinja2 import Template
import pandas as pd


class GroupReporter:
    """分组报告生成器."""

    def __init__(self, provider, config: dict | None = None) -> None:
        """初始化报告生成器.

        Args:
            provider: 数据提供者实例
            config: 配置字典

        """
        self.provider = provider
        self.config = config or {}

        # 导入分析模块
        from group.group_analyzer import GroupAnalyzer

        self.analyzer = GroupAnalyzer(provider, config)

    def generate_data(self, symbols: list[str], group_name: str | None = None) -> dict:
        """生成报告数据.

        Args:
            symbols: 股票代码列表
            group_name: 分组名称

        Returns:
            报告数据字典

        """
        # 分析分组
        analysis = self.analyzer.analyze_group(symbols, group_name)

        # 添加时间戳
        analysis["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return analysis

    def generate_markdown(self, data: dict) -> str:
        """生成 Markdown 格式报告.

        Args:
            data: 报告数据

        Returns:
            Markdown 格式的报告字符串

        """
        # 读取模板
        template_path = (
            Path(__file__).parent.parent.parent / "assets" / "templates" / "group_report.md.j2"
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
        group_name = data.get("group_name", "未命名分组")
        lines.append(f"# 自选分组分析报告 - {group_name}")
        lines.append(f"\n**分组**：{group_name}")
        lines.append(f"**股票数量**：{data['stock_count']} 只")
        lines.append(f"**分析时间**：{data['timestamp']}\n")

        # 组合概览
        lines.append("## 📋 组合概览\n")
        summary = data["summary"]
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 今日上涨 | {summary['up_count']} 只 |")
        lines.append(f"| 今日下跌 | {summary['down_count']} 只 |")
        lines.append(f"| 平均涨跌 | {summary['avg_change']}% |")

        # 交易建议
        signals = data.get("signals", {})
        buy_list = signals.get("buy", [])
        hold_list = signals.get("hold", [])
        sell_list = signals.get("sell", [])

        lines.append("\n## 🎯 交易建议\n")

        if buy_list:
            lines.append(f"### ✅ 建议关注 ({len(buy_list)}只)\n")
            lines.append("| 股票 | 代码 | 现价 | 涨跌 | 评分 | 风险 |")
            lines.append("|------|------|------|------|------|------|")
            for stock in buy_list[:10]:
                lines.append(
                    f"| {stock['name']} | {stock['symbol']} | {stock['price']:.2f} | {stock['change_pct']:.2f}% | {stock['overall_score']}/10 | {stock['risk_level']} |",
                )

        if hold_list:
            lines.append(f"\n### ⚠️ 谨慎持有 ({len(hold_list)}只)\n")
            lines.append("| 股票 | 代码 | 现价 | 涨跌 | 建议 |")
            lines.append("|------|------|------|------|------|")
            for stock in hold_list[:10]:
                lines.append(
                    f"| {stock['name']} | {stock['symbol']} | {stock['price']:.2f} | {stock['change_pct']:.2f}% | 观望 |",
                )

        if sell_list:
            lines.append(f"\n### ❌ 建议规避 ({len(sell_list)}只)\n")
            lines.append("| 股票 | 代码 | 现价 | 涨跌 | 建议 |")
            lines.append("|------|------|------|------|------|")
            for stock in sell_list[:10]:
                lines.append(
                    f"| {stock['name']} | {stock['symbol']} | {stock['price']:.2f} | {stock['change_pct']:.2f}% | 规避 |",
                )

        # 综合建议
        summary_text = signals.get("summary", "暂无建议")
        lines.append(f"\n**综合建议**：{summary_text}")

        # 技术面扫描
        signal_summary = self.analyzer.get_signal_summary(signals)

        lines.append("\n## 📊 技术面扫描\n")

        if signal_summary["golden_cross"]:
            lines.append("### 金叉信号\n")
            for stock in signal_summary["golden_cross"][:5]:
                signals_str = ", ".join([
                    s["name"] for s in stock.get("signals", []) if "cross" in s.get("type", "")
                ])
                lines.append(f"- {stock['name']}（{stock['symbol']}）：{signals_str}")

        if signal_summary["oversold"]:
            lines.append("\n### 超卖反弹\n")
            for stock in signal_summary["oversold"][:5]:
                lines.append(f"- {stock['name']}（{stock['symbol']}）：RSI偏低，关注反弹机会")

        if signal_summary["breakout"]:
            lines.append("\n### 放量突破\n")
            for stock in signal_summary["breakout"][:5]:
                lines.append(f"- {stock['name']}（{stock['symbol']}）：放量突破关键位")

        # 表现分析
        lines.append("\n## 📈 表现分析\n")

        top = data.get("top_performers", [])
        if top:
            lines.append("### 领涨股\n")
            lines.append("| 股票 | 代码 | 涨跌幅 |")
            lines.append("|------|------|--------|")
            for stock in top[:5]:
                lines.append(
                    f"| {stock['name']} | {stock['symbol']} | {stock['change_pct']:.2f}% |",
                )

        laggards = data.get("laggards", [])
        if laggards:
            lines.append("\n### 滞后股\n")
            lines.append("| 股票 | 代码 | 涨跌幅 |")
            lines.append("|------|------|--------|")
            for stock in laggards[:5]:
                lines.append(
                    f"| {stock['name']} | {stock['symbol']} | {stock['change_pct']:.2f}% |",
                )

        # 基本面评分
        fundamental_scores = data.get("fundamental_scores", [])
        if fundamental_scores:
            lines.append("\n## 💰 基本面评分\n")

            high_scores = [s for s in fundamental_scores if s["score"] >= 7]
            if high_scores:
                lines.append("### 优质标的（评分 >= 7）\n")
                lines.append("| 股票 | 代码 | 综合评分 |")
                lines.append("|------|------|----------|")
                for stock in high_scores[:10]:
                    lines.append(f"| {stock['name']} | {stock['symbol']} | {stock['score']}/10 |")

        return "\n".join(lines)

    def save_markdown(self, data: dict, output_path: str | Path) -> None:
        """保存为 Markdown 格式.

        Args:
            data: 报告数据
            output_path: 输出文件路径

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate_markdown(data)

        with Path(output_path).open("w", encoding="utf-8") as f:
            f.write(content)

    def save_csv(self, data: dict, output_path: str | Path) -> None:
        """保存为 CSV 格式.

        Args:
            data: 报告数据
            output_path: 输出文件路径

        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        signals = data.get("signals", {})

        # 将所有股票合并到一个列表
        all_stocks = []
        for action in ["buy", "hold", "sell"]:
            for stock in signals.get(action, []):
                stock["recommendation"] = action
                all_stocks.append(stock)

        if all_stocks:
            df = pd.DataFrame(all_stocks)

            # 选择要输出的列
            columns = [
                "symbol",
                "name",
                "price",
                "change_pct",
                "overall_score",
                "recommendation",
                "risk_level",
            ]
            available_columns = [c for c in columns if c in df.columns]

            df[available_columns].to_csv(output_path, index=False, encoding="utf-8-sig")
