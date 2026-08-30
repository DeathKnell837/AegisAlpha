# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(str(ENV_PATH))


class RiskSettings(BaseModel):
    """Deterministic risk management boundaries."""
    max_risk_per_trade_pct: float = Field(default=0.02, description="Max 2% of portfolio equity at risk per trade")
    max_portfolio_options_pct: float = Field(default=0.20, description="Max 20% of equity allocated to options")
    max_position_size_usd: float = Field(default=2500.0, description="Max dollar loss risk per single position")
    max_slippage_bid_ask_pct: float = Field(default=0.15, description="Max bid-ask spread relative to mid-price (15%)")
    min_dte: int = Field(default=5, description="Minimum days to expiration to avoid extreme gamma pin risk")
    max_dte: int = Field(default=45, description="Maximum days to expiration for short-to-medium duration alpha")
    profit_target_pct: float = Field(default=0.50, description="Take profit at +50% of max spread profit / premium")
    stop_loss_pct: float = Field(default=0.40, description="Cut loss at -40% of premium paid")
    max_daily_drawdown_pct: float = Field(default=0.03, description="Halt new trades if daily portfolio drawdown exceeds 3%")


class AppConfig:
    def __init__(self):
        # Alpaca Credentials
        self.alpaca_api_key = os.getenv("ALPACA_API_KEY", "")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY", "")
        self.alpaca_base_url = os.getenv("ALPACA_API_BASE_URL", "https://paper-api.alpaca.markets")
        self.alpaca_account_id = os.getenv("ALPACA_ACCOUNT_ID", "PA3PL5AZ85K6")
        self.is_paper = "paper" in self.alpaca_base_url.lower()

        # Featherless AI Credentials
        self.featherless_api_key = os.getenv("FEATHERLESS_API_KEY", "")
        self.featherless_base_url = "https://api.featherless.ai/v1"
        self.default_model = os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-72B-Instruct")
        self.fallback_model = "Qwen/Qwen2.5-32B-Instruct"

        # Trading Watchlist
        self.default_watchlist = ["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT", "AMD"]

        # Risk parameters
        self.risk = RiskSettings()

    def validate(self):
        if not self.alpaca_api_key or not self.alpaca_secret_key:
            raise ValueError("Alpaca API credentials missing in .env")
        if not self.featherless_api_key:
            raise ValueError("Featherless API Key missing in .env")
        return True


config = AppConfig()

def get_config() -> AppConfig:
    return config

