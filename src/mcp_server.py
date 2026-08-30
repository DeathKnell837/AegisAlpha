# src/mcp_server.py
"""
FastMCP Server for AegisOptions Trading Desk.
Exposes autonomous tools for Claude / Cursor / Antigravity agents.
"""
from fastmcp import FastMCP
from src.alpaca_service import AlpacaService
from src.agent_desk import AegisOptionsDesk
from alpaca.trading.enums import OrderSide, OrderType

mcp = FastMCP("AegisOptions Desk", description="Autonomous Options Alpha & Risk Gate Trading System")
desk = AegisOptionsDesk()


@mcp.tool()
def get_portfolio_telemetry() -> dict:
    """Returns account equity, cash balance, buying power, and active P&L."""
    return desk.alpaca.get_account()


@mcp.tool()
def get_active_options_positions() -> list:
    """Returns all open equity and options positions with Greeks and unrealized P&L."""
    return desk.alpaca.get_positions()


@mcp.tool()
def scan_symbol_for_options_alpha(symbol: str) -> dict:
    """Runs the full AI alpha evaluation and deterministic risk gate for an underlying ticker."""
    log = desk.scan_and_evaluate_symbol(symbol.upper())
    if log:
        return log.model_dump()
    return {"error": f"No actionable options candidates found for {symbol}"}


@mcp.tool()
def run_autonomous_trading_cycle() -> list:
    """Scans the default watchlist and executes all risk-approved defined-risk option spreads."""
    logs = desk.run_cycle()
    return [l.model_dump() for l in logs]


@mcp.tool()
def emergency_kill_switch() -> list:
    """Emergency risk guardrail: cancels all open orders and liquidates all positions."""
    return desk.alpaca.close_all_positions()


if __name__ == "__main__":
    mcp.run()
