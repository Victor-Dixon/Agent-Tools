#!/usr/bin/env python3
"""
Trading Strategy Blog Automation
================================

Automated blog post generation based on trading strategy analysis.
Generates free and premium reports for the TSLA strategy.

Usage:
    python tools/strategy_blog_automation.py --site tradingrobotplug.com --strategy tsla
    python tools/strategy_blog_automation.py --site tradingrobotplug.com --generate-report --premium
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "tools"))

try:
    from unified_blogging_automation import UnifiedBloggingAutomation
    HAS_BLOGGING = True
except ImportError:
    HAS_BLOGGING = False

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# TSLA Strategy Configuration
TSLA_STRATEGY = {
    "name": "Improved TSLA Strategy (Risk-True)",
    "symbol": "TSLA",
    "indicators": {
        "ma_short": 50,
        "ma_long": 200,
        "rsi_length": 14,
        "rsi_overbought": 60,
        "rsi_oversold": 40
    },
    "risk_management": {
        "risk_pct_equity": 0.5,
        "stop_loss_pct": 1.0,
        "profit_target_pct": 15.0,
        "trailing_stop": True,
        "trail_offset_pct": 0.5,
        "trail_trigger_pct": 5.0
    },
    "backtest_metrics": {
        "initial_capital": 1000000.00,
        "net_profit": 726897.07,
        "net_profit_pct": 72.69,
        "gross_profit": 1003137.17,
        "gross_profit_pct": 100.31,
        "gross_loss": 276240.10,
        "gross_loss_pct": 27.62,
        "buy_hold_return": 32360.52,
        "buy_hold_return_pct": 3.24,
        "max_contracts_held": 1897,
        "max_equity_drawdown": 33992.48,
        "max_equity_drawdown_pct": 2.03,
        "max_equity_runup": 726933.15,
        "max_equity_runup_pct": 42.09,
        "avg_equity_drawdown": 14170.88,
        "avg_equity_drawdown_pct": 1.42,
        "avg_equity_runup": 44280.70,
        "avg_equity_runup_pct": 4.43,
        "avg_drawdown_duration": "18 hours",
        "avg_runup_duration": "1 day"
    }
}


def generate_strategy_analysis() -> Dict[str, Any]:
    """Generate analysis of the trading strategy."""
    strategy = TSLA_STRATEGY

    analysis = {
        "strategy_name": strategy["name"],
        "symbol": strategy["symbol"],
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "indicators": {
            "trend_analysis": f"Uses {strategy['indicators']['ma_short']}-day and {strategy['indicators']['ma_long']}-day moving averages to identify trend direction",
            "momentum": f"RSI ({strategy['indicators']['rsi_length']}-period) with overbought at {strategy['indicators']['rsi_overbought']} and oversold at {strategy['indicators']['rsi_oversold']}",
            "entry_logic": "Long when price is above both MAs and RSI is not overheated. Short when price is below both MAs and RSI is not oversold."
        },
        "risk_management": {
            "position_sizing": f"Risk-based position sizing: {strategy['risk_management']['risk_pct_equity']}% of equity per trade",
            "stop_loss": f"Stop loss: {strategy['risk_management']['stop_loss_pct']}% of entry price",
            "profit_target": f"Profit target: {strategy['risk_management']['profit_target_pct']}% of entry price",
            "trailing_stop": f"Trailing stop: {'Enabled' if strategy['risk_management']['trailing_stop'] else 'Disabled'}",
            "risk_reward": f"Risk/Reward Ratio: 1:{strategy['risk_management']['profit_target_pct'] / strategy['risk_management']['stop_loss_pct']:.1f}"
        },
        "key_features": [
            "True risk-based position sizing (not fixed contracts)",
            "Dynamic stop loss and profit targets",
            "Optional trailing stop for profit protection",
            "RSI filter to avoid overbought/oversold entries",
            "Trend-following with dual moving average confirmation"
        ],
        "performance_notes": [
            "Strategy designed for trending markets",
            "Works best when clear trend is established",
            "Risk management is the core focus",
            "Suitable for swing trading timeframes"
        ]
    }

    return analysis


def load_blog_template() -> str:
    """Load the blog post template."""
    template_path = project_root / "tools" / \
        "templates" / "strategy_blog_post_template.html"

    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to basic template if file doesn't exist
        return """<!-- wp:heading -->
<h2>Strategy Analysis: {strategy_name}</h2>
<!-- /wp:heading -->
"""


def generate_blog_post_content(analysis: Dict[str, Any], include_premium_teaser: bool = True) -> str:
    """Generate blog post content from strategy analysis using template."""

    strategy = TSLA_STRATEGY

    # Load template
    template = load_blog_template()

    # Build indicators list
    indicators_list = f"""<li><strong>Short Moving Average:</strong> {strategy['indicators']['ma_short']} days</li>
<li><strong>Long Moving Average:</strong> {strategy['indicators']['ma_long']} days</li>
<li><strong>RSI Period:</strong> {strategy['indicators']['rsi_length']}</li>
<li><strong>RSI Overbought Level:</strong> {strategy['indicators']['rsi_overbought']}</li>
<li><strong>RSI Oversold Level:</strong> {strategy['indicators']['rsi_oversold']}</li>"""

    # Build risk parameters list
    risk_parameters_list = f"""<li><strong>Risk per Trade:</strong> {strategy['risk_management']['risk_pct_equity']}% of equity</li>
<li><strong>Stop Loss:</strong> {strategy['risk_management']['stop_loss_pct']}% of price</li>
<li><strong>Profit Target:</strong> {strategy['risk_management']['profit_target_pct']}% of price</li>
<li><strong>Trailing Stop:</strong> {'Enabled' if strategy['risk_management']['trailing_stop'] else 'Disabled'}</li>
<li><strong>Risk/Reward Ratio:</strong> 1:{strategy['risk_management']['profit_target_pct'] / strategy['risk_management']['stop_loss_pct']:.1f}</li>"""

    # Build entry conditions
    long_entry_conditions = f"""<li>Price must be above {strategy['indicators']['ma_short']}-day moving average</li>
<li>Price must be above {strategy['indicators']['ma_long']}-day moving average</li>
<li>RSI must be below {strategy['indicators']['rsi_overbought']} (not overheated)</li>
<li>Trend confirmation from dual moving averages</li>"""

    short_entry_conditions = f"""<li>Price must be below {strategy['indicators']['ma_short']}-day moving average</li>
<li>Price must be below {strategy['indicators']['ma_long']}-day moving average</li>
<li>RSI must be above {strategy['indicators']['rsi_oversold']} (not oversold)</li>
<li>Downtrend confirmation from dual moving averages</li>"""

    # Build exit strategy list
    exit_strategy_list = f"""<li><strong>Profit Target:</strong> {strategy['risk_management']['profit_target_pct']}% from entry price</li>
<li><strong>Stop Loss:</strong> {strategy['risk_management']['stop_loss_pct']}% from entry price</li>"""

    if strategy['risk_management']['trailing_stop']:
        exit_strategy_list += f"""
<li><strong>Trailing Stop:</strong> Activates after {strategy['risk_management']['trail_trigger_pct']}% move in favor</li>
<li><strong>Trail Offset:</strong> {strategy['risk_management']['trail_offset_pct']}% of price</li>"""

    # Build risk management list
    risk_management_list = f"""<li>{analysis['risk_management']['position_sizing']}</li>
<li>{analysis['risk_management']['stop_loss']}</li>
<li>{analysis['risk_management']['profit_target']}</li>
<li>{analysis['risk_management']['trailing_stop']}</li>
<li>{analysis['risk_management']['risk_reward']}</li>"""

    # Build key features list
    key_features_list = "\n".join(
        [f"<li>{feature}</li>" for feature in analysis['key_features']])

    # Build performance notes list
    performance_notes_list = "\n".join(
        [f"<li>{note}</li>" for note in analysis['performance_notes']])

    # Determine report slugs
    symbol_lower = analysis['symbol'].lower()
    report_slug = f"{symbol_lower}-strategy-report"
    premium_report_slug = f"{symbol_lower}-strategy-report-premium"

    # Get metrics (if available)
    metrics = analysis.get('backtest_metrics', {})

    # Format metrics for display
    def format_currency(value):
        return f"${value:,.2f}" if value else "$0.00"

    def format_percent(value):
        return f"{value:+.2f}" if value else "0.00"

    # Fill template
    content = template.format(
        strategy_name=analysis['strategy_name'],
        analysis_date=analysis['analysis_date'],
        symbol=analysis['symbol'],
        strategy_type="trend-following",
        indicators_list=indicators_list,
        risk_parameters_list=risk_parameters_list,
        long_entry_conditions=long_entry_conditions,
        short_entry_conditions=short_entry_conditions,
        exit_strategy_list=exit_strategy_list,
        risk_management_list=risk_management_list,
        key_features_list=key_features_list,
        performance_notes_list=performance_notes_list,
        report_slug=report_slug,
        premium_report_slug=premium_report_slug,
        # Metrics (formatted)
        initial_capital_formatted=format_currency(
            metrics.get('initial_capital', 0)),
        net_profit_formatted=format_currency(metrics.get('net_profit', 0)),
        net_profit_pct_formatted=format_percent(
            metrics.get('net_profit_pct', 0)),
        gross_profit_formatted=format_currency(metrics.get('gross_profit', 0)),
        gross_profit_pct_formatted=format_percent(
            metrics.get('gross_profit_pct', 0)),
        gross_loss_formatted=format_currency(metrics.get('gross_loss', 0)),
        gross_loss_pct_formatted=format_percent(
            metrics.get('gross_loss_pct', 0)),
        buy_hold_return_formatted=format_currency(
            metrics.get('buy_hold_return', 0)),
        buy_hold_return_pct_formatted=format_percent(
            metrics.get('buy_hold_return_pct', 0)),
        max_drawdown_formatted=format_currency(
            metrics.get('max_equity_drawdown', 0)),
        max_drawdown_pct_formatted=format_percent(
            metrics.get('max_equity_drawdown_pct', 0)),
        max_runup_formatted=format_currency(
            metrics.get('max_equity_runup', 0)),
        max_runup_pct_formatted=format_percent(
            metrics.get('max_equity_runup_pct', 0))
    )

    return content


def generate_report_content(analysis: Dict[str, Any], premium: bool = False) -> str:
    """Generate report content (free or premium version)."""

    metrics = analysis.get('backtest_metrics', {})
    strategy = TSLA_STRATEGY

    # Format currency and percentages
    def fmt_curr(v): return f"${v:,.2f}" if v else "$0.00"
    def fmt_pct(v): return f"{v:+.2f}%" if v else "0.00%"

    base_content = f"""
# {analysis['strategy_name']} - {'Premium' if premium else 'Free'} Report

**Analysis Date:** {analysis['analysis_date']}  
**Symbol:** {analysis['symbol']}

## Executive Summary

This report provides a comprehensive analysis of the {analysis['strategy_name']} trading strategy for {analysis['symbol']}.

### Backtest Performance Overview

- **Initial Capital:** {fmt_curr(metrics.get('initial_capital', 0))}
- **Net Profit:** {fmt_curr(metrics.get('net_profit', 0))} ({fmt_pct(metrics.get('net_profit_pct', 0))})
- **Gross Profit:** {fmt_curr(metrics.get('gross_profit', 0))} ({fmt_pct(metrics.get('gross_profit_pct', 0))})
- **Gross Loss:** {fmt_curr(metrics.get('gross_loss', 0))} ({fmt_pct(metrics.get('gross_loss_pct', 0))})
- **Buy & Hold Return:** {fmt_curr(metrics.get('buy_hold_return', 0))} ({fmt_pct(metrics.get('buy_hold_return_pct', 0))})
- **Max Drawdown:** {fmt_curr(metrics.get('max_equity_drawdown', 0))} ({fmt_pct(metrics.get('max_equity_drawdown_pct', 0))})
- **Max Run-up:** {fmt_curr(metrics.get('max_equity_runup', 0))} ({fmt_pct(metrics.get('max_equity_runup_pct', 0))})

## Strategy Configuration

### Indicators
- **Short MA:** {TSLA_STRATEGY['indicators']['ma_short']} days
- **Long MA:** {TSLA_STRATEGY['indicators']['ma_long']} days
- **RSI Period:** {TSLA_STRATEGY['indicators']['rsi_length']}
- **RSI Overbought:** {TSLA_STRATEGY['indicators']['rsi_overbought']}
- **RSI Oversold:** {TSLA_STRATEGY['indicators']['rsi_oversold']}

### Risk Management
- **Risk per Trade:** {TSLA_STRATEGY['risk_management']['risk_pct_equity']}% of equity
- **Stop Loss:** {TSLA_STRATEGY['risk_management']['stop_loss_pct']}% of price
- **Profit Target:** {TSLA_STRATEGY['risk_management']['profit_target_pct']}% of price
- **Trailing Stop:** {'Enabled' if TSLA_STRATEGY['risk_management']['trailing_stop'] else 'Disabled'}

## Entry Logic

### Long Entries
- Price must be above both {TSLA_STRATEGY['indicators']['ma_short']}-day and {TSLA_STRATEGY['indicators']['ma_long']}-day moving averages
- RSI must be below {TSLA_STRATEGY['indicators']['rsi_overbought']} (not overheated)

### Short Entries
- Price must be below both moving averages
- RSI must be above {TSLA_STRATEGY['indicators']['rsi_oversold']} (not oversold)

## Risk Management Details

The strategy uses true risk-based position sizing:
- Calculates risk amount: Equity × {TSLA_STRATEGY['risk_management']['risk_pct_equity']}%
- Determines stop distance: Entry Price × {TSLA_STRATEGY['risk_management']['stop_loss_pct']}%
- Calculates position size: Risk Amount ÷ Stop Distance

This ensures consistent risk across all trades regardless of entry price.

## Exit Strategy

### Profit Target
- Long: Entry Price × (1 + {TSLA_STRATEGY['risk_management']['profit_target_pct']}%)
- Short: Entry Price × (1 - {TSLA_STRATEGY['risk_management']['profit_target_pct']}%)

### Trailing Stop (if enabled)
- Trigger: Price moves {TSLA_STRATEGY['risk_management']['trail_trigger_pct']}% in favor
- Offset: {TSLA_STRATEGY['risk_management']['trail_offset_pct']}% of price

## Risk/Reward Analysis

- **Risk per Trade:** {TSLA_STRATEGY['risk_management']['stop_loss_pct']}%
- **Reward Target:** {TSLA_STRATEGY['risk_management']['profit_target_pct']}%
- **Risk/Reward Ratio:** 1:{TSLA_STRATEGY['risk_management']['profit_target_pct'] / TSLA_STRATEGY['risk_management']['stop_loss_pct']:.1f}

This means for every $1 risked, the strategy targets $15 in profit.

## Backtest Performance Summary

### Key Metrics
- **Initial Capital:** {fmt_curr(metrics.get('initial_capital', 0))}
- **Net Profit:** {fmt_curr(metrics.get('net_profit', 0))} ({fmt_pct(metrics.get('net_profit_pct', 0))})
- **Gross Profit:** {fmt_curr(metrics.get('gross_profit', 0))} ({fmt_pct(metrics.get('gross_profit_pct', 0))})
- **Gross Loss:** {fmt_curr(metrics.get('gross_loss', 0))} ({fmt_pct(metrics.get('gross_loss_pct', 0))})
- **Maximum Drawdown:** {fmt_curr(metrics.get('max_equity_drawdown', 0))} ({fmt_pct(metrics.get('max_equity_drawdown_pct', 0))})
- **Buy & Hold Return:** {fmt_curr(metrics.get('buy_hold_return', 0))} ({fmt_pct(metrics.get('buy_hold_return_pct', 0))})

### Performance Highlights
- Strategy outperformed buy & hold by {fmt_pct(metrics.get('net_profit_pct', 0) - metrics.get('buy_hold_return_pct', 0))}
- Maximum contracts held: {metrics.get('max_contracts_held', 0):,}
- Average drawdown duration: {metrics.get('avg_drawdown_duration', 'N/A')}
- Average run-up duration: {metrics.get('avg_runup_duration', 'N/A')}
"""

    if premium:
        premium_content = f"""

## Premium Analysis (Premium Report Only)

### Detailed Performance Metrics

#### Profit Analysis
- **Net Profit:** {fmt_curr(metrics.get('net_profit', 0))} ({fmt_pct(metrics.get('net_profit_pct', 0))})
- **Gross Profit:** {fmt_curr(metrics.get('gross_profit', 0))} ({fmt_pct(metrics.get('gross_profit_pct', 0))})
- **Gross Loss:** {fmt_curr(metrics.get('gross_loss', 0))} ({fmt_pct(metrics.get('gross_loss_pct', 0))})
- **Profit Factor:** {metrics.get('gross_profit', 0) / abs(metrics.get('gross_loss', 1)):.2f} (Gross Profit / Gross Loss)

#### Risk Metrics
- **Maximum Drawdown:** {fmt_curr(metrics.get('max_equity_drawdown', 0))} ({fmt_pct(metrics.get('max_equity_drawdown_pct', 0))})
- **Average Drawdown:** {fmt_curr(metrics.get('avg_equity_drawdown', 0))} ({fmt_pct(metrics.get('avg_equity_drawdown_pct', 0))})
- **Average Drawdown Duration:** {metrics.get('avg_drawdown_duration', 'N/A')}
- **Maximum Run-up:** {fmt_curr(metrics.get('max_equity_runup', 0))} ({fmt_pct(metrics.get('max_equity_runup_pct', 0))})
- **Average Run-up:** {fmt_curr(metrics.get('avg_equity_runup', 0))} ({fmt_pct(metrics.get('avg_equity_runup_pct', 0))})
- **Average Run-up Duration:** {metrics.get('avg_runup_duration', 'N/A')}

#### Position Sizing
- **Maximum Contracts Held:** {metrics.get('max_contracts_held', 0):,}
- **Risk per Trade:** {strategy['risk_management']['risk_pct_equity']}% of equity
- **Stop Loss:** {strategy['risk_management']['stop_loss_pct']}% of price

#### Comparison to Buy & Hold
- **Strategy Return:** {fmt_pct(metrics.get('net_profit_pct', 0))}
- **Buy & Hold Return:** {fmt_pct(metrics.get('buy_hold_return_pct', 0))}
- **Outperformance:** {fmt_pct(metrics.get('net_profit_pct', 0) - metrics.get('buy_hold_return_pct', 0))}

### Trade-by-Trade Analysis
*Detailed analysis of each trade signal would appear here in a full premium report. This includes entry/exit prices, profit/loss per trade, and trade duration.*

### Optimization Suggestions
1. **Parameter Testing:** Consider testing different MA periods (40/180, 50/200, 60/220)
2. **RSI Thresholds:** Adjust overbought/oversold levels (55/45, 60/40, 65/35) based on market conditions
3. **Risk Percentage:** Test different risk percentages (0.25%, 0.5%, 1.0%, 1.5%)
4. **Timeframe:** Strategy may perform differently on different timeframes (daily, 4-hour, weekly)
5. **Trailing Stop:** Test different trail trigger and offset percentages

### PineScript Code
```pinescript
//@version=6
strategy("Improved TSLA Strategy (Risk-True)", overlay=true, initial_capital=1000000, pyramiding=0)

// Trend
maShortLength = input.int(50, title="Short Moving Average")
maLongLength  = input.int(200, title="Long Moving Average")

// RSI
rsiLength     = input.int(14, title="RSI Length")
rsiOverbought = input.int(60, title="RSI Overbought")
rsiOversold   = input.int(40, title="RSI Oversold")

// Risk model
riskPctEquity = input.float(0.5, title="Risk % of Equity per Trade", minval=0.1, step=0.1)
stopPctPrice  = input.float(1.0, title="Stop Loss % of Price", minval=0.1, step=0.1)

// Reward
targetPctPrice   = input.float(15.0, title="Profit Target % of Price", minval=0.5, step=0.5)
useTrailingStop  = input.bool(true,  title="Use Trailing Stop")
trailOffsetPct   = input.float(0.5,  title="Trail Offset % of Price", minval=0.1, step=0.1)
trailTriggerPct  = input.float(5.0,  title="Trail Trigger % of Price", minval=0.5, step=0.5)

// Indicators
maShort = ta.sma(close, maShortLength)
maLong  = ta.sma(close, maLongLength)
rsi     = ta.rsi(close, rsiLength)

plot(maShort, color=color.blue, linewidth=1, title="MA 50")
plot(maLong,  color=color.red,  linewidth=1, title="MA 200")

// Entry conditions
longCondition  = (close > maShort and close > maLong) and (rsi < rsiOverbought)
shortCondition = (close < maShort and close < maLong) and (rsi > rsiOversold)

// True risk-based position sizing
riskAmount = strategy.equity * (riskPctEquity / 100.0)
stopDist   = close * (stopPctPrice / 100.0)
safeStopDist = math.max(stopDist, syminfo.mintick * 10)
rawQty = riskAmount / safeStopDist
qty    = math.floor(rawQty)
canTrade = qty >= 1

if longCondition and canTrade
    strategy.entry("Long", strategy.long, qty=qty)

if shortCondition and canTrade
    strategy.entry("Short", strategy.short, qty=qty)

// Exits
longStop  = close - stopDist
shortStop = close + stopDist
longTarget  = close * (1 + targetPctPrice / 100.0)
shortTarget = close * (1 - targetPctPrice / 100.0)
trailOffsetPts  = close * (trailOffsetPct / 100.0)
trailTriggerPts = close * (trailTriggerPct / 100.0)

if useTrailingStop
    strategy.exit("Exit Long", from_entry="Long",
         stop=longStop,
         trail_points=trailTriggerPts,
         trail_offset=trailOffsetPts)
    strategy.exit("Exit Short", from_entry="Short",
         stop=shortStop,
         trail_points=trailTriggerPts,
         trail_offset=trailOffsetPts)
else
    strategy.exit("Exit Long", from_entry="Long", stop=longStop, limit=longTarget)
    strategy.exit("Exit Short", from_entry="Short", stop=shortStop, limit=shortTarget)
```
"""
        base_content += premium_content

    else:
        base_content += """
## Upgrade to Premium

Want more detailed analysis? Upgrade to the Premium Report to get:
- Complete backtesting results with performance metrics
- Trade-by-trade analysis
- Optimization suggestions
- Full PineScript code download
- Email support for strategy questions

[Get Premium Report](/reports/tsla-strategy-report-premium)
"""

    return base_content


def create_blog_post(site_name: str, analysis: Dict[str, Any]) -> bool:
    """Create a blog post about the strategy."""
    if not HAS_BLOGGING:
        print("❌ Blogging automation not available")
        return False

    try:
        automation = UnifiedBloggingAutomation()
        content = generate_blog_post_content(analysis)

        # Create post
        post_title = f"{analysis['strategy_name']} - Strategy Analysis {analysis['analysis_date']}"
        # Clean title for WordPress
        post_title = post_title.replace(
            '(', '').replace(')', '').replace(',', '')

        # Get tags
        config_path = project_root / ".deploy_credentials" / "blogging_api.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        if site_name not in config:
            print(f"❌ Site {site_name} not found in config")
            return False

        site_config = config[site_name]
        tags = site_config.get('default_tags', []) + \
            ['strategy-analysis', 'tsla', 'risk-management']

        # Use site_purpose to get categories/tags, or pass None to use defaults
        result = automation.publish_to_site(
            site_id=site_name,
            title=post_title,
            content=content,
            site_purpose=site_config.get('purpose', 'trading_education'),
            status='publish'
        )

        if result.get('success'):
            print(f"✅ Blog post created: {result.get('post_url', 'N/A')}")
            return True
        else:
            print(
                f"❌ Failed to create post: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Error creating blog post: {e}")
        return False


def create_report_page(site_name: str, analysis: Dict[str, Any], premium: bool = False) -> bool:
    """Create a WordPress page for the report."""
    if not HAS_REQUESTS:
        print("❌ requests library required")
        return False

    try:
        config_path = project_root / ".deploy_credentials" / "blogging_api.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        if site_name not in config:
            print(f"❌ Site {site_name} not found")
            return False

        site_config = config[site_name]
        site_url = site_config['site_url']
        username = site_config['username']
        app_password = site_config['app_password']

        report_type = "premium" if premium else "free"
        slug = f"tsla-strategy-report-{report_type}" if premium else "tsla-strategy-report"
        title = f"TSLA Strategy Report - {'Premium' if premium else 'Free'}"

        content = generate_report_content(analysis, premium)

        # Convert markdown to HTML (simple conversion)
        html_content = content.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_content = f"<p>{html_content}</p>"
        html_content = html_content.replace(
            '<p># ', '<h1>').replace('</p>', '</h1>', 1)
        html_content = html_content.replace(
            '<br>## ', '</p><h2>').replace('<br>', '</h2><p>')
        html_content = html_content.replace(
            '<br>### ', '</p><h3>').replace('<br>', '</h3><p>')

        # Create page via REST API
        api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
        auth = HTTPBasicAuth(username, app_password)

        page_data = {
            "title": title,
            "slug": slug,
            "status": "publish",
            "content": html_content
        }

        response = requests.post(
            api_url, json=page_data, auth=auth, timeout=30)

        if response.status_code in (200, 201):
            page = response.json()
            print(f"✅ Report page created: {page.get('link')}")
            return True
        else:
            print(
                f"❌ Failed to create page: {response.status_code} - {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error creating report page: {e}")
        return False


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Trading Strategy Blog Automation")
    parser.add_argument("--site", default="freerideinvestor", help="Site name")
    parser.add_argument("--strategy", default="tsla",
                        help="Strategy to analyze")
    parser.add_argument("--generate-post",
                        action="store_true", help="Generate blog post")
    parser.add_argument("--generate-report",
                        action="store_true", help="Generate report page")
    parser.add_argument("--premium", action="store_true",
                        help="Generate premium report")

    args = parser.parse_args()

    # Generate analysis
    analysis = generate_strategy_analysis()

    if args.generate_post:
        create_blog_post(args.site, analysis)

    if args.generate_report:
        create_report_page(args.site, analysis, premium=args.premium)

    if not args.generate_post and not args.generate_report:
        print("Analysis generated. Use --generate-post or --generate-report to publish.")
        print(f"\nStrategy: {analysis['strategy_name']}")
        print(f"Symbol: {analysis['symbol']}")
        print(f"Date: {analysis['analysis_date']}")


if __name__ == "__main__":
    main()
