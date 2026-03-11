---
name: stock-analysis
description: A股综合分析工具，支持市场整体报告和股票分组分析。集成 AKShare 数据源，提供市场快照、情绪分析、热点板块跟踪、技术信号生成、基本面评分等功能。输出 Markdown 和 CSV 格式报告。
---

## 核心功能

stock-analysis 提供两种核心报告能力：

### 1. 市场整体报告 (`report market`)

**市场快照**

- 4大指数实时行情（上证指数、深证成指、创业板指、科创50）
- 市场统计数据（涨跌家数、涨停跌停、成交额）

**市场情绪分析**

- 涨跌比分析
- 量比分析
- 综合情绪评分（0-5分制）
- 情绪状态判断（恐慌、中性、贪婪）

**热点板块跟踪**

- 行业板块涨跌幅排行
- 板块资金流向分析
- 板块成分股查询
- 领涨股票识别

### 2. 股票分组分析报告 (`report group`)

**交易建议**

- ✅ 建议关注：综合评分高，看多信号明确
- ⚠️ 谨慎持有：信号不明确，建议观望
- ❌ 建议规避：出现看空信号

**技术面扫描**

- 金叉/死叉检测（MA、MACD）
- 超买超卖识别（RSI、KDJ）
- 放量突破检测
- 支撑压力位分析

**基本面评分**

- 估值水平分析（PE、PB）
- 成长性评估
- 财务健康度检查
- **同行比较分析**（估值、成长性、杜邦分析）
- **主营构成分析**（业务收入分布）
- **新闻情绪分析**（个股最新资讯）

**组合分析**

- 涨跌统计
- 领涨股/滞后股识别
- 行业分布分析

## CLI 命令

### 市场报告

```bash
# 生成市场完整报告（Markdown）
python scripts/cli/stock_analysis.py report market \
    --format markdown \
    --output market_report.md

# 生成市场数据（CSV）
python scripts/cli/stock_analysis.py report market \
    --format csv \
    --output market_data.csv

# 快速查看市场快照
python scripts/cli/stock_analysis.py quick market
```

### 分组报告

```bash
# 从文件生成分组报告
python scripts/cli/stock_analysis.py report group \
    --symbols-file stocks.txt \
    --group-name "科技龙头" \
    --output group_report.md

# 指定股票代码列表
python scripts/cli/stock_analysis.py report group \
    --symbols "600000.SH,600036.SH,000001.SZ" \
    --output my_stocks.md

# 仅查看交易建议
python scripts/cli/stock_analysis.py report group \
    --symbols-file stocks.txt \
    --signals-only

# 快速查看分组
python scripts/cli/stock_analysis.py quick group --symbols-file stocks.txt
```

## 报告示例

### 市场报告输出

```markdown
# A股市场日报

**生成时间**：2024-01-25 15:00:00

## 📊 市场概览

| 指数 | 点位 | 涨跌 |
|------|------|------|
| 上证指数 | 3,234.56 | +1.23% ↑ |
| 深证成指 | 10,234.78 | +1.45% ↑ |
| 创业板指 | 1,987.65 | +2.01% ↑ |
| 科创50 | 1,023.45 | +1.87% ↑ |

**总成交额**：8,500 亿

## 🎭 市场情绪

| 指标 | 数值 | 状态 |
|------|------|------|
| 涨跌比 | 1.97 | 偏多 |
| 涨停/跌停 | 85/12 | 活跃 |
| 情绪评分 | 3.8/5 | 偏乐观 |

## 🔥 热点板块 TOP5

| 排名 | 板块 | 涨跌幅 | 净流入 | 领涨股 |
|------|------|--------|--------|--------|
| 1 | 半导体 | +3.45% | +150亿 | 中微公司 |
| 2 | 新能源 | +2.87% | +80亿 | 宁德时代 |
...
```

### 分组报告输出

```markdown
# 自选分组分析报告 - 科技龙头

**分组**：科技龙头
**股票数量**：25 只
**分析时间**：2024-01-25 15:00:00

## 📋 组合概览

| 指标 | 数值 |
|------|------|
| 今日上涨 | 18 只 |
| 今日下跌 | 7 只 |
| 平均涨跌 | +1.85% |

## 🎯 交易建议

### ✅ 建议关注 (5只)

| 股票 | 代码 | 现价 | 涨跌 | 评分 | 风险 | 建议理由 |
|------|------|------|------|------|------|----------|
| 中微公司 | 688012 | 158.50 | +5.2% | 7.5/10 | 高 | 金叉+RSI适中+放量突破 |
...

## 📊 技术面扫描

### 金叉信号 (3只)
- 688012 中微公司：MA5金叉MA20，MACD金叉
- 688256 寒武纪：MACD金叉，成交量放大
- 002475 立讯精密：KDJ金叉
...
```

## 配置文件

配置文件位于 `config/default.yaml`，可以自定义：

```yaml
# 交易信号配置
signals:
  golden_cross:
    fast_period: 5
    slow_period: 20
    strength: 8

# 评分权重
scoring:
  technical:
    trend: 0.4
    momentum: 0.3
    volume: 0.3
  fundamental:
    valuation: 0.3
    growth: 0.4
    quality: 0.3

# 市场报告配置
market_report:
  hot_sectors_top_n: 5

# 分组报告配置
group_report:
  buy_threshold: 7.0
  sell_threshold: 3.0
```

## 数据来源

### AKShare 数据接口

stock-analysis 使用以下 AKShare 接口获取 A股数据：

| 功能 | AKShare 方法 | 说明 |
|------|-------------|------|
| 指数行情 | `stock_zh_index_spot_em` | 主要指数实时数据 |
| 市场统计 | `stock_zh_a_spot_em` | 全市场涨跌统计 |
| 板块排行 | `stock_board_industry_name_em` | 行业板块涨跌幅 |
| 板块成分股 | `stock_board_industry_cons_em` | 板块内股票列表 |
| 资金流向 | `stock_sector_fund_flow_rank` | 板块资金流向 |
| 同行成长性比较 | `stock_zh_growth_comparison_em` | 营收/利润增长率对比 |
| 同行估值比较 | `stock_zh_valuation_comparison_em` | PE/PB/PS 对比 |
| 同行杜邦分析 | `stock_zh_dupont_comparison_em` | ROE 分解对比 |
| 主营构成 | `stock_zygc_em` | 业务收入分布 |
| 千股千评 | `stock_comment_em` | 市场情绪参考 |
| 个股新闻 | `stock_news_em` | 最新资讯 |

### LongPort

- **港股/美股数据**：保留原有 LongPort 能力，支持跨市场分析

## 快速开始

详见 [快速开始指南](references/quick_start.md) 了解端到端示例。

详见 [报告解读指南](references/report_guide.md) 了解如何解读报告内容。

原有技术指标功能见 [指标参考](references/indicator_reference.md)。
