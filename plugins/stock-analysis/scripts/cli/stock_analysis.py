# /// script
# dependencies = [
#     "pandas>=3.0.0",
#     "pyyaml>=6.0",
#     "akshare>=1.12.0",
#     "jinja2>=3.1.0",
#     "ta-lib>=0.6.8",
# ]
# ///

"""Stock Analysis CLI.

A股综合分析工具 - 命令行入口
"""

import argparse
from pathlib import Path
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.akshare_provider import AKShareProvider
from core.data_router import DataRouter
from group.group_analyzer import GroupAnalyzer

# Import market snapshot module at top level
from market.market_snapshot import MarketSnapshot
from report.group_reporter import GroupReporter
from report.market_reporter import MarketReporter


def load_config(config_path: str | None = None) -> tuple[dict, DataRouter]:
    """加载配置."""
    router = DataRouter(config_path)
    return router.config, router


def cmd_market_report(args, config: dict) -> None:
    """生成市场报告."""
    provider = AKShareProvider(
        timeout=config.get("data_sources", {}).get("akshare", {}).get("timeout", 60),
    )

    reporter = MarketReporter(provider, config)

    # 生成报告数据
    data = reporter.generate_data()

    # 输出
    if args.format == "markdown":
        content = reporter.generate_markdown(data)
        if args.output:
            reporter.save_markdown(data, args.output)
            print(f"报告已保存到: {args.output}")
        else:
            print(content)
    else:  # csv
        if args.output:
            reporter.save_csv(data, args.output)
            print(f"CSV 已保存到: {args.output}")
        else:
            print(data)


def cmd_group_report(args, config: dict) -> int:
    """生成分组报告."""
    provider = AKShareProvider(
        timeout=config.get("data_sources", {}).get("akshare", {}).get("timeout", 60),
    )

    reporter = GroupReporter(provider, config)
    analyzer = GroupAnalyzer(provider, config)

    # 获取股票列表
    if args.symbols_file:
        symbols = analyzer.read_symbols_from_file(args.symbols_file)
        group_name = args.group_name or Path(args.symbols_file).stem
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",")]
        group_name = args.group_name or "自定义分组"
    else:
        print("错误：请提供 --symbols 或 --symbols-file")
        return 1

    if not symbols:
        print("错误：没有找到有效的股票代码")
        return 1

    print(f"正在分析 {len(symbols)} 只股票...")

    # 生成报告数据
    data = reporter.generate_data(symbols, group_name)

    # 输出
    if args.format == "markdown":
        if args.output:
            reporter.save_markdown(data, args.output)
            print(f"报告已保存到: {args.output}")
        else:
            content = reporter.generate_markdown(data)
            print(content)
    else:  # csv
        if args.output:
            reporter.save_csv(data, args.output)
            print(f"CSV 已保存到: {args.output}")
        else:
            print(data)

    return 0


def cmd_quick_market(args: argparse.Namespace) -> None:
    """快速查看市场."""
    provider = AKShareProvider()

    # 获取市场快照
    snapshot = MarketSnapshot(provider)
    data = snapshot.generate()

    print("\n=== A股市场快照 ===\n")

    print("指数行情:")
    for idx in data["indices"]:
        arrow = "↑" if idx["change_pct"] > 0 else "↓"
        print(f"  {idx['name']:6s}: {idx['price']:>8.2f}  ({idx['change_pct']:+.2f}%) {arrow}")

    stats = data["statistics"]
    print("\n市场统计:")
    print(
        f"  上涨: {stats['up_count']} | 下跌: {stats['down_count']} | 涨停: {stats['limit_up_count']}"
    )

    nc = data["north_capital"]
    nc_str = f"+{nc['north_flow']:.0f}" if nc["north_flow"] > 0 else f"{nc['north_flow']:.0f}"
    print(f"  北向资金: {nc_str} 亿")

    print(f"\n更新时间: {data['timestamp']}\n")


def cmd_quick_group(args: argparse.Namespace, config: dict) -> int | None:
    """快速查看分组."""
    provider = AKShareProvider()
    analyzer = GroupAnalyzer(provider, config)

    # 读取股票列表
    if args.symbols_file:
        symbols = analyzer.read_symbols_from_file(args.symbols_file)
        group_name = Path(args.symbols_file).stem
    else:
        symbols = [args.group_id]
        group_name = args.group_id

    if not symbols:
        print("错误：没有找到股票代码")
        return 1

    # 获取概览
    summary = analyzer._calculate_group_summary(symbols)

    print(f"\n=== 分组快照: {group_name} ===\n")
    print(f"股票数量: {len(symbols)}")
    print(f"今日上涨: {summary['up_count']} | 今日下跌: {summary['down_count']}")
    print(f"平均涨跌: {summary['avg_change']:+.2f}%")

    # 表现最好和最差
    top = analyzer._get_top_performers(symbols, top_n=3)
    laggards = analyzer._get_laggards(symbols, top_n=3)

    if top:
        print("\n领涨股:")
        for stock in top:
            print(f"  {stock['name']:8s} ({stock['symbol']}): {stock['change_pct']:+.2f}%")

    if laggards:
        print("\n滞后股:")
        for stock in laggards:
            print(f"  {stock['name']:8s} ({stock['symbol']}): {stock['change_pct']:+.2f}%")

    print()
    return None


def main() -> int:
    """主入口."""
    parser = argparse.ArgumentParser(
        description="Stock Analysis CLI - A股综合分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成市场报告
  %(prog)s report market --format markdown --output market_report.md

  # 生成分组报告
  %(prog)s report group --symbols-file stocks.txt --output group_report.md

  # 快速查看市场
  %(prog)s quick market

  # 快速查看分组
  %(prog)s quick group --symbols-file stocks.txt
        """,
    )

    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # ===== report 命令 =====
    report_parser = subparsers.add_parser("report", help="生成分析报告")
    report_subparsers = report_parser.add_subparsers(dest="report_type", help="报告类型")

    # report market
    market_report_parser = report_subparsers.add_parser("market", help="市场整体报告")
    market_report_parser.add_argument(
        "--format",
        choices=["markdown", "csv"],
        default="markdown",
        help="输出格式",
    )
    market_report_parser.add_argument("--output", "-o", help="输出文件路径")
    market_report_parser.add_argument("--brief", action="store_true", help="简化版")

    # report group
    group_report_parser = report_subparsers.add_parser("group", help="股票分组报告")
    group_report_parser.add_argument("--symbols", "-s", help="股票代码列表(逗号分隔)")
    group_report_parser.add_argument("--symbols-file", "-f", help="股票代码文件(每行一个)")
    group_report_parser.add_argument("--group-name", "-n", help="分组名称")
    group_report_parser.add_argument(
        "--format",
        choices=["markdown", "csv"],
        default="markdown",
        help="输出格式",
    )
    group_report_parser.add_argument("--output", "-o", help="输出文件路径")
    group_report_parser.add_argument("--signals-only", action="store_true", help="仅显示交易建议")

    # ===== quick 命令 =====
    quick_parser = subparsers.add_parser("quick", help="快速查看")
    quick_subparsers = quick_parser.add_subparsers(dest="quick_type", help="快速查看类型")

    # quick market
    quick_subparsers.add_parser("market", help="快速查看市场")

    # quick group
    quick_group_parser = quick_subparsers.add_parser("group", help="快速查看分组")
    quick_group_parser.add_argument("group_id", nargs="?", help="分组 ID 或股票代码文件")
    quick_group_parser.add_argument("--symbols-file", "-f", help="股票代码文件")

    # 解析参数
    args = parser.parse_args()

    # 加载配置
    config, _router = load_config(args.config)

    # 路由到对应的处理函数
    if args.command == "report":
        if args.report_type == "market":
            cmd_market_report(args, config)
            return 0
        if args.report_type == "group":
            return cmd_group_report(args, config)
        parser.print_help()
        return 1

    if args.command == "quick":
        if args.quick_type == "market":
            cmd_quick_market(args)
            return 0
        if args.quick_type == "group":
            result = cmd_quick_group(args, config)
            return result if result is not None else 0
        parser.print_help()
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
