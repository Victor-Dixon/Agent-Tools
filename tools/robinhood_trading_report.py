#!/usr/bin/env python3
"""
Robinhood Trading Robot Report Generator
Generates comprehensive report on Robinhood positions and trading robot systems
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from trading_robot.core.broker_factory import create_broker_client
    from trading_robot.config.settings import config
    from trading_robot.core.robinhood_client import ROBINHOOD_AVAILABLE
    TRADING_ROBOT_AVAILABLE = True
except ImportError as e:
    TRADING_ROBOT_AVAILABLE = False
    print(f"⚠️ Trading robot not available: {e}")

try:
    import discord
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️ discord.py not installed. Install with: pip install discord.py")


def get_robinhood_positions() -> Dict[str, Any]:
    """Attempt to get Robinhood positions if credentials are available"""
    if not TRADING_ROBOT_AVAILABLE:
        return {"error": "Trading robot not available", "positions": []}
    
    if not ROBINHOOD_AVAILABLE:
        return {"error": "robin_stocks library not installed", "positions": []}
    
    if config.broker != "robinhood":
        return {"error": f"Broker is set to '{config.broker}', not 'robinhood'", "positions": []}
    
    if not getattr(config, 'robinhood_username', '') or not getattr(config, 'robinhood_password', ''):
        return {"error": "Robinhood credentials not configured", "positions": []}
    
    try:
        client = create_broker_client()
        if not client.connect():
            return {"error": "Failed to connect to Robinhood API", "positions": []}
        
        account_info = client.get_account_info()
        positions = client.get_positions()
        
        return {
            "connected": True,
            "account_info": account_info,
            "positions": positions,
            "total_positions": len(positions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "positions": []}


def get_trading_robot_systems() -> Dict[str, Any]:
    """Document all trading robot systems and tools"""
    systems = {
        "core_components": {
            "trading_engine": {
                "file": "trading_robot/core/trading_engine.py",
                "description": "Main trading engine managing broker API interactions",
                "features": [
                    "Broker connection management",
                    "Position monitoring",
                    "Order execution",
                    "Market clock tracking",
                    "Pre-flight validation"
                ]
            },
            "broker_interface": {
                "file": "trading_robot/core/broker_interface.py",
                "description": "Abstract interface for multi-broker support",
                "features": [
                    "Unified API for Alpaca and Robinhood",
                    "Account info retrieval",
                    "Position management",
                    "Order submission",
                    "Historical data access"
                ]
            },
            "alpaca_client": {
                "file": "trading_robot/core/alpaca_client.py",
                "description": "Alpaca API client implementation",
                "features": [
                    "Alpaca API integration",
                    "Paper and live trading support",
                    "Real-time market data",
                    "Order execution"
                ]
            },
            "robinhood_client": {
                "file": "trading_robot/core/robinhood_client.py",
                "description": "Robinhood API client using robin_stocks library",
                "features": [
                    "Robinhood API integration (unofficial)",
                    "Position retrieval",
                    "Order submission",
                    "Historical data",
                    "⚠️ Uses unofficial robin_stocks library - may violate ToS"
                ],
                "status": "Unofficial - use at own risk"
            },
            "broker_factory": {
                "file": "trading_robot/core/broker_factory.py",
                "description": "Factory for creating broker clients",
                "features": [
                    "Dynamic broker selection",
                    "Alpaca and Robinhood support"
                ]
            },
            "risk_manager": {
                "file": "trading_robot/core/risk_manager.py",
                "description": "Comprehensive risk management system",
                "features": [
                    "Daily loss limits",
                    "Position size limits",
                    "Portfolio risk management",
                    "Emergency stop functionality",
                    "Trade validation",
                    "Risk metrics calculation"
                ]
            },
            "preflight_validator": {
                "file": "trading_robot/core/preflight_validator.py",
                "description": "Pre-flight validation before trading",
                "features": [
                    "Configuration validation",
                    "API connectivity checks",
                    "Account status verification"
                ]
            }
        },
        "strategies": {
            "base_strategy": {
                "file": "trading_robot/strategies/base_strategy.py",
                "description": "Abstract base class for trading strategies",
                "features": [
                    "Strategy framework",
                    "Technical indicator integration",
                    "Risk management integration",
                    "Data validation"
                ]
            },
            "indicators": {
                "file": "trading_robot/strategies/indicators.py",
                "description": "Technical indicators library",
                "features": [
                    "20+ technical indicators",
                    "RSI, MACD, Bollinger Bands",
                    "Moving averages",
                    "Signal processing"
                ]
            },
            "strategy_implementations": {
                "file": "trading_robot/strategies/strategy_implementations.py",
                "description": "Built-in trading strategies",
                "features": [
                    "Trend following",
                    "Mean reversion",
                    "Custom strategy support"
                ]
            },
            "risk_management": {
                "file": "trading_robot/strategies/risk_management.py",
                "description": "Strategy-level risk management",
                "features": [
                    "Position sizing",
                    "Stop loss calculation",
                    "Take profit calculation"
                ]
            },
            "signal_processing": {
                "file": "trading_robot/strategies/signal_processing.py",
                "description": "Signal generation and processing",
                "features": [
                    "Buy/sell signal generation",
                    "Signal confidence scoring",
                    "Signal filtering"
                ]
            }
        },
        "execution": {
            "live_executor": {
                "file": "trading_robot/execution/live_executor.py",
                "description": "Live trading execution engine",
                "features": [
                    "Real-time order execution",
                    "Position monitoring",
                    "Risk management integration"
                ]
            }
        },
        "backtesting": {
            "backtester": {
                "file": "trading_robot/backtesting/backtester.py",
                "description": "Historical backtesting system",
                "features": [
                    "Strategy performance testing",
                    "Portfolio value tracking",
                    "Performance metrics",
                    "Visualization support"
                ]
            }
        },
        "web_dashboard": {
            "dashboard": {
                "file": "trading_robot/web/dashboard.py",
                "description": "Web dashboard for monitoring",
                "features": [
                    "Real-time portfolio monitoring",
                    "Position tracking",
                    "WebSocket updates",
                    "FastAPI-based"
                ]
            },
            "dashboard_routes": {
                "file": "trading_robot/web/dashboard_routes.py",
                "description": "Dashboard API routes",
                "features": [
                    "Portfolio API",
                    "Status API",
                    "Market data API"
                ]
            }
        },
        "configuration": {
            "settings": {
                "file": "trading_robot/config/settings.py",
                "description": "Trading robot configuration",
                "features": [
                    "Broker selection (Alpaca/Robinhood)",
                    "Risk management settings",
                    "Trading mode (paper/live)",
                    "Dashboard configuration"
                ]
            }
        }
    }
    
    return systems


def generate_report() -> str:
    """Generate comprehensive trading robot report"""
    report_lines = []
    
    # Header
    report_lines.append("# 📊 ROBINHOOD TRADING ROBOT REPORT")
    report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("**Agent**: Agent-8 (SSOT & System Integration Specialist)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Robinhood Positions Section
    report_lines.append("## 🎯 ROBINHOOD OPEN POSITIONS")
    report_lines.append("")
    
    positions_data = get_robinhood_positions()
    
    if "error" in positions_data:
        report_lines.append(f"⚠️ **Status**: {positions_data['error']}")
        report_lines.append("")
        report_lines.append("**Note**: Robinhood positions cannot be retrieved because:")
        report_lines.append(f"- {positions_data['error']}")
        report_lines.append("")
        report_lines.append("**To enable position retrieval:**")
        report_lines.append("1. Set `BROKER=robinhood` in environment/config")
        report_lines.append("2. Configure `ROBINHOOD_USERNAME` and `ROBINHOOD_PASSWORD`")
        report_lines.append("3. Install `robin_stocks` library: `pip install robin-stocks`")
        report_lines.append("4. ⚠️ **Warning**: Robinhood API access is unofficial and may violate ToS")
    else:
        account_info = positions_data.get("account_info", {})
        positions = positions_data.get("positions", [])
        
        report_lines.append(f"✅ **Connection Status**: Connected")
        report_lines.append(f"📅 **Timestamp**: {positions_data.get('timestamp', 'N/A')}")
        report_lines.append("")
        
        # Account Info
        report_lines.append("### 💰 Account Information")
        report_lines.append("")
        report_lines.append(f"- **Account ID**: {account_info.get('id', 'N/A')}")
        report_lines.append(f"- **Cash Balance**: ${account_info.get('cash', 0):,.2f}")
        report_lines.append(f"- **Portfolio Value**: ${account_info.get('portfolio_value', 0):,.2f}")
        report_lines.append(f"- **Buying Power**: ${account_info.get('buying_power', 0):,.2f}")
        report_lines.append(f"- **Day Trade Count**: {account_info.get('daytrade_count', 0)}")
        report_lines.append(f"- **Account Status**: {account_info.get('status', 'N/A')}")
        report_lines.append("")
        
        # Positions
        total_positions = len(positions)
        report_lines.append(f"### 📈 Open Positions ({total_positions})")
        report_lines.append("")
        
        if total_positions == 0:
            report_lines.append("**No open positions**")
        else:
            total_market_value = 0
            total_unrealized_pl = 0
            
            report_lines.append("| Symbol | Quantity | Avg Entry | Current Price | Market Value | Unrealized P&L | P&L % |")
            report_lines.append("|--------|----------|-----------|---------------|---------------|----------------|-------|")
            
            for pos in positions:
                symbol = pos.get('symbol', 'N/A')
                qty = pos.get('qty', 0)
                avg_entry = pos.get('avg_entry_price', 0)
                current_price = pos.get('current_price', 0)
                market_value = pos.get('market_value', 0)
                unrealized_pl = pos.get('unrealized_pl', 0)
                unrealized_plpc = pos.get('unrealized_plpc', 0)
                
                total_market_value += market_value
                total_unrealized_pl += unrealized_pl
                
                pl_sign = "+" if unrealized_pl >= 0 else ""
                plpc_sign = "+" if unrealized_plpc >= 0 else ""
                
                report_lines.append(
                    f"| {symbol} | {qty} | ${avg_entry:.2f} | ${current_price:.2f} | "
                    f"${market_value:,.2f} | {pl_sign}${unrealized_pl:,.2f} | {plpc_sign}{unrealized_plpc:.2f}% |"
                )
            
            report_lines.append("")
            report_lines.append(f"**Total Market Value**: ${total_market_value:,.2f}")
            pl_sign = "+" if total_unrealized_pl >= 0 else ""
            report_lines.append(f"**Total Unrealized P&L**: {pl_sign}${total_unrealized_pl:,.2f}")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Trading Robot Systems Section
    report_lines.append("## 🤖 TRADING ROBOT SYSTEMS & TOOLS")
    report_lines.append("")
    
    systems = get_trading_robot_systems()
    
    # Core Components
    report_lines.append("### 🔧 Core Components")
    report_lines.append("")
    for name, info in systems["core_components"].items():
        report_lines.append(f"#### {name.replace('_', ' ').title()}")
        report_lines.append(f"- **File**: `{info['file']}`")
        report_lines.append(f"- **Description**: {info['description']}")
        report_lines.append("- **Features**:")
        for feature in info['features']:
            report_lines.append(f"  - {feature}")
        if 'status' in info:
            report_lines.append(f"- **Status**: {info['status']}")
        report_lines.append("")
    
    # Strategies
    report_lines.append("### 📊 Trading Strategies")
    report_lines.append("")
    for name, info in systems["strategies"].items():
        report_lines.append(f"#### {name.replace('_', ' ').title()}")
        report_lines.append(f"- **File**: `{info['file']}`")
        report_lines.append(f"- **Description**: {info['description']}")
        report_lines.append("- **Features**:")
        for feature in info['features']:
            report_lines.append(f"  - {feature}")
        report_lines.append("")
    
    # Execution
    report_lines.append("### ⚡ Execution Systems")
    report_lines.append("")
    for name, info in systems["execution"].items():
        report_lines.append(f"#### {name.replace('_', ' ').title()}")
        report_lines.append(f"- **File**: `{info['file']}`")
        report_lines.append(f"- **Description**: {info['description']}")
        report_lines.append("- **Features**:")
        for feature in info['features']:
            report_lines.append(f"  - {feature}")
        report_lines.append("")
    
    # Backtesting
    report_lines.append("### 📈 Backtesting")
    report_lines.append("")
    for name, info in systems["backtesting"].items():
        report_lines.append(f"#### {name.replace('_', ' ').title()}")
        report_lines.append(f"- **File**: `{info['file']}`")
        report_lines.append(f"- **Description**: {info['description']}")
        report_lines.append("- **Features**:")
        for feature in info['features']:
            report_lines.append(f"  - {feature}")
        report_lines.append("")
    
    # Web Dashboard
    report_lines.append("### 🌐 Web Dashboard")
    report_lines.append("")
    for name, info in systems["web_dashboard"].items():
        report_lines.append(f"#### {name.replace('_', ' ').title()}")
        report_lines.append(f"- **File**: `{info['file']}`")
        report_lines.append(f"- **Description**: {info['description']}")
        report_lines.append("- **Features**:")
        for feature in info['features']:
            report_lines.append(f"  - {feature}")
        report_lines.append("")
    
    # Configuration
    report_lines.append("### ⚙️ Configuration")
    report_lines.append("")
    for name, info in systems["configuration"].items():
        report_lines.append(f"#### {name.replace('_', ' ').title()}")
        report_lines.append(f"- **File**: `{info['file']}`")
        report_lines.append(f"- **Description**: {info['description']}")
        report_lines.append("- **Features**:")
        for feature in info['features']:
            report_lines.append(f"  - {feature}")
        report_lines.append("")
    
    # Summary
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## 📋 SUMMARY")
    report_lines.append("")
    report_lines.append("### Trading Robot Capabilities")
    report_lines.append("")
    report_lines.append("- ✅ **Multi-Broker Support**: Alpaca (official) and Robinhood (unofficial)")
    report_lines.append("- ✅ **Risk Management**: Comprehensive position sizing, stop losses, portfolio protection")
    report_lines.append("- ✅ **Strategy Framework**: Extensible strategy system with 20+ technical indicators")
    report_lines.append("- ✅ **Backtesting**: Historical performance analysis and validation")
    report_lines.append("- ✅ **Web Dashboard**: Real-time monitoring and control interface")
    report_lines.append("- ✅ **Live Execution**: Automated order execution with safety checks")
    report_lines.append("- ✅ **Pre-flight Validation**: Configuration and API connectivity checks")
    report_lines.append("")
    report_lines.append("### Current Configuration")
    report_lines.append("")
    if TRADING_ROBOT_AVAILABLE:
        report_lines.append(f"- **Broker**: {config.broker.upper()}")
        report_lines.append(f"- **Trading Mode**: {config.trading_mode}")
        report_lines.append(f"- **Live Trading Enabled**: {config.live_trading_enabled}")
        report_lines.append(f"- **Max Positions**: {config.max_positions}")
        report_lines.append(f"- **Daily Loss Limit**: {config.daily_loss_limit_pct * 100}%")
        report_lines.append(f"- **Max Position Size**: {config.max_position_size_pct * 100}% of portfolio")
    else:
        report_lines.append("- Trading robot configuration not available")
    report_lines.append("")
    report_lines.append("### ⚠️ Important Notes")
    report_lines.append("")
    report_lines.append("- **Robinhood Integration**: Uses unofficial `robin_stocks` library - may violate ToS")
    report_lines.append("- **Live Trading**: Requires explicit `LIVE_TRADING_ENABLED=true` flag for safety")
    report_lines.append("- **Paper Trading**: Default mode - safe for testing strategies")
    report_lines.append("- **Risk Management**: Always test strategies in paper mode before live trading")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("**Generated by**: Agent-8 (SSOT & System Integration Specialist)")
    report_lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("🐝 **WE. ARE. SWARM. ⚡🔥**")
    
    return "\n".join(report_lines)


def post_to_discord(report: str, channel_id: Optional[int] = None) -> bool:
    """Post report to Discord"""
    if not DISCORD_AVAILABLE:
        print("❌ discord.py not installed. Install with: pip install discord.py")
        return False
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found in environment")
        return False
    
    if not channel_id:
        # Default channel ID (can be overridden)
        channel_id = int(os.getenv("DISCORD_REPORT_CHANNEL_ID", "0"))
        if channel_id == 0:
            print("❌ DISCORD_REPORT_CHANNEL_ID not set")
            return False
    
    try:
        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            channel = client.get_channel(channel_id)
            if channel:
                # Discord has a 2000 character limit per message
                # Split report into chunks if needed
                max_length = 1900  # Leave room for formatting
                chunks = [report[i:i+max_length] for i in range(0, len(report), max_length)]
                
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await channel.send(f"```markdown\n{chunk}\n```")
                    else:
                        await channel.send(f"```markdown\n{chunk}\n```")
                
                print(f"✅ Report posted to Discord channel {channel_id}")
            else:
                print(f"❌ Channel {channel_id} not found")
            
            await client.close()
        
        client.run(token)
        return True
        
    except Exception as e:
        print(f"❌ Error posting to Discord: {e}")
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Robinhood Trading Robot Report")
    parser.add_argument("--output", type=str, help="Output file path (optional)")
    parser.add_argument("--discord", action="store_true", help="Post to Discord")
    parser.add_argument("--channel", type=int, help="Discord channel ID")
    
    args = parser.parse_args()
    
    print("📊 Generating Robinhood Trading Robot Report...")
    report = generate_report()
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Report saved to: {output_path}")
    
    # Post to Discord if requested
    if args.discord:
        print("📤 Posting to Discord...")
        post_to_discord(report, args.channel)
    else:
        # Print to console
        print("\n" + "="*80)
        print(report)
        print("="*80)
        print("\n💡 Tip: Use --discord to post to Discord, --output to save to file")


if __name__ == "__main__":
    main()

