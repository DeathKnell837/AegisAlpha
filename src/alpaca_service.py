# src/alpaca_service.py
import datetime
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    LimitOrderRequest,
    MarketOrderRequest,
    OrderRequest,
)
from alpaca.trading.enums import (
    OrderSide,
    TimeInForce,
    OrderType,
    QueryOrderStatus,
    AssetClass,
)
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    OptionChainRequest,
)
from alpaca.data.timeframe import TimeFrame

from alpaca.data.enums import DataFeed, OptionsFeed

from src.config import get_config


class AlpacaService:
    def __init__(self):
        self.config = get_config()
        self.trading_client = TradingClient(
            api_key=self.config.alpaca_api_key,
            secret_key=self.config.alpaca_secret_key,
            paper=self.config.is_paper,
        )
        self.stock_data_client = StockHistoricalDataClient(
            api_key=self.config.alpaca_api_key,
            secret_key=self.config.alpaca_secret_key,
        )
        self.option_data_client = OptionHistoricalDataClient(
            api_key=self.config.alpaca_api_key,
            secret_key=self.config.alpaca_secret_key,
        )

    def get_account(self) -> Dict[str, Any]:
        acc = self.trading_client.get_account()
        equity = float(acc.equity)
        last_equity = float(acc.last_equity)
        day_pnl = equity - last_equity
        day_pnl_pct = (day_pnl / last_equity * 100) if last_equity > 0 else 0.0

        return {
            'account_number': acc.account_number,
            'status': str(acc.status),
            'currency': acc.currency,
            'cash': float(acc.cash),
            'equity': equity,
            'buying_power': float(acc.buying_power),
            'day_pnl': round(day_pnl, 2),
            'day_pnl_pct': round(day_pnl_pct, 2),
            'options_approved_level': getattr(acc, 'options_approved_level', 3),
            'options_trading_level': getattr(acc, 'options_trading_level', 3),
            'pattern_day_trader': getattr(acc, 'pattern_day_trader', False),
            'trading_blocked': getattr(acc, 'trading_blocked', False),
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        positions = self.trading_client.get_all_positions()
        res = []
        for p in positions:
            res.append({
                'asset_id': str(p.asset_id),
                'symbol': p.symbol,
                'asset_class': str(p.asset_class),
                'qty': float(p.qty),
                'side': str(p.side),
                'avg_entry_price': float(p.avg_entry_price),
                'current_price': float(p.current_price) if p.current_price else float(p.avg_entry_price),
                'market_value': float(p.market_value) if p.market_value else 0.0,
                'cost_basis': float(p.cost_basis),
                'unrealized_pl': float(p.unrealized_pl),
                'unrealized_plpc': float(p.unrealized_plpc) * 100,
                'change_today': float(p.change_today) * 100 if p.change_today else 0.0,
            })
        return res

    def get_stock_price_and_momentum(self, symbol: str) -> Dict[str, Any]:
        end_dt = datetime.now(timezone.utc) - timedelta(minutes=15)
        start_dt = end_dt - timedelta(days=30)
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_dt,
            end=end_dt,
            feed=DataFeed.IEX,
        )
        bars_dict = self.stock_data_client.get_stock_bars(req)
        bars = bars_dict.data.get(symbol, [])

        if not bars:
            return {'symbol': symbol, 'price': 0.0, 'trend': 'UNKNOWN', 'volatility_pct': 0.0}

        df = pd.DataFrame([{
            'timestamp': b.timestamp,
            'open': b.open,
            'high': b.high,
            'low': b.low,
            'close': b.close,
            'volume': b.volume
        } for b in bars])

        current_price = float(df['close'].iloc[-1])
        ma_5 = df['close'].tail(5).mean()
        ma_20 = df['close'].mean()
        daily_returns = df['close'].pct_change().dropna()
        realized_vol = float(daily_returns.std() * (252 ** 0.5) * 100) if len(daily_returns) > 1 else 20.0

        if current_price > ma_5 > ma_20:
            trend = 'STRONG_BULLISH'
        elif current_price > ma_20:
            trend = 'MILD_BULLISH'
        elif current_price < ma_5 < ma_20:
            trend = 'STRONG_BEARISH'
        elif current_price < ma_20:
            trend = 'MILD_BEARISH'
        else:
            trend = 'RANGE_BOUND_NEUTRAL'

        return {
            'symbol': symbol,
            'price': round(current_price, 2),
            'ma_5': round(float(ma_5), 2),
            'ma_20': round(float(ma_20), 2),
            'realized_volatility_annual_pct': round(realized_vol, 2),
            'trend': trend,
            'high_30d': round(float(df['high'].max()), 2),
            'low_30d': round(float(df['low'].min()), 2),
        }

    def get_option_chain_candidates(
        self,
        underlying_symbol: str,
        min_dte: int = 5,
        max_dte: int = 45
    ) -> Dict[str, Any]:
        stock_info = self.get_stock_price_and_momentum(underlying_symbol)
        curr_price = stock_info['price']
        if curr_price <= 0:
            return {'symbol': underlying_symbol, 'calls': [], 'puts': []}

        try:
            req = OptionChainRequest(
                underlying_symbol=underlying_symbol,
                feed=OptionsFeed.INDICATIVE
            )
            chain_snapshots = self.option_data_client.get_option_chain(req)
        except Exception as e:
            print(f'Warning fetching option chain for {underlying_symbol}: {e}')
            return {'symbol': underlying_symbol, 'calls': [], 'puts': []}

        calls = []
        puts = []

        for contract_symbol, snap in chain_snapshots.items():
            try:
                # Type detection
                # E.g. AAPL260918C00230000 -> CALL, AAPL260918P00230000 -> PUT
                is_call = 'C' in contract_symbol[len(underlying_symbol)+6:len(underlying_symbol)+8]
                type_char = 'C' if is_call else 'P'
                greeks = snap.greeks if snap.greeks else None
                latest_quote = snap.latest_quote
                if not latest_quote or not latest_quote.bid_price or not latest_quote.ask_price:
                    continue

                bid = float(latest_quote.bid_price)
                ask = float(latest_quote.ask_price)
                if bid <= 0 or ask <= 0:
                    continue

                mid = round((bid + ask) / 2, 2)
                spread_pct = round((ask - bid) / mid, 3) if mid > 0 else 1.0

                delta = float(greeks.delta) if greeks and greeks.delta is not None else 0.0
                gamma = float(greeks.gamma) if greeks and greeks.gamma is not None else 0.0
                theta = float(greeks.theta) if greeks and greeks.theta is not None else 0.0
                vega = float(greeks.vega) if greeks and greeks.vega is not None else 0.0
                iv = float(snap.implied_volatility) if snap.implied_volatility is not None else 0.0

                # Extract strike from contract symbol
                raw_strike = contract_symbol[-8:]
                strike_price = float(raw_strike) / 1000.0 if raw_strike.isdigit() else curr_price

                item = {
                    'contract_symbol': contract_symbol,
                    'type': 'CALL' if type_char == 'C' else 'PUT',
                    'strike': strike_price,
                    'bid': bid,
                    'ask': ask,
                    'mid': mid,
                    'spread_pct': spread_pct,
                    'delta': round(delta, 3),
                    'gamma': round(gamma, 4),
                    'theta': round(theta, 3),
                    'vega': round(vega, 3),
                    'iv': round(iv * 100, 2),
                }

                if type_char == 'C':
                    calls.append(item)
                else:
                    puts.append(item)
            except Exception:
                continue

        # Sort by proximity to 0.40 delta (optimal long leg for alpha spreads)
        calls.sort(key=lambda x: abs(abs(x['delta']) - 0.40))
        puts.sort(key=lambda x: abs(abs(x['delta']) - 0.40))

        return {
            'symbol': underlying_symbol,
            'underlying_price': curr_price,
            'trend': stock_info['trend'],
            'calls': calls[:15],
            'puts': puts[:15],
        }

    def place_option_order(
        self,
        contract_symbol: str,
        qty: int,
        side: OrderSide = OrderSide.BUY,
        order_type: OrderType = OrderType.LIMIT,
        limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Submits an options order (single or spread leg) with Day time-in-force."""
        if order_type == OrderType.LIMIT and limit_price is not None:
            req = LimitOrderRequest(
                symbol=contract_symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=round(limit_price, 2),
            )
        else:
            req = MarketOrderRequest(
                symbol=contract_symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
            )

        order = self.trading_client.submit_order(req)
        return {
            'order_id': str(order.id),
            'client_order_id': order.client_order_id,
            'symbol': order.symbol,
            'qty': float(order.qty),
            'side': str(order.side),
            'status': str(order.status),
            'type': str(order.type),
            'submitted_at': str(order.submitted_at),
        }

    def place_order_simple(
        self,
        symbol: str,
        qty: int,
        side: OrderSide,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        if order_type == OrderType.LIMIT and limit_price:
            req = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=limit_price,
            )
        else:
            req = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
            )
        
        order = self.trading_client.submit_order(req)
        return {
            'order_id': str(order.id),
            'client_order_id': order.client_order_id,
            'symbol': order.symbol,
            'qty': float(order.qty),
            'side': str(order.side),
            'status': str(order.status),
            'type': str(order.type),
            'submitted_at': str(order.submitted_at),
        }

    def close_position(self, symbol: str) -> Dict[str, Any]:
        try:
            res = self.trading_client.close_position(symbol)
            return {'symbol': symbol, 'status': 'CLOSED', 'order_id': str(res.id)}
        except Exception as e:
            err_str = str(e)
            if "market hours" in err_str.lower() or "42210000" in err_str:
                # When market is closed, submit offsetting Limit Order to close at current price
                try:
                    pos = [p for p in self.get_positions() if p['symbol'] == symbol]
                    if pos:
                        p = pos[0]
                        side = OrderSide.SELL if p['qty'] > 0 else OrderSide.BUY
                        close_qty = abs(int(p['qty']))
                        price = max(0.01, round(float(p.get('current_price', 0.01)), 2))
                        order = self.place_option_order(symbol, close_qty, side, OrderType.LIMIT, limit_price=price)
                        return {
                            'symbol': symbol,
                            'status': 'QUEUED_FOR_OPEN',
                            'order_id': order.get('order_id'),
                            'message': 'Order queued for market open at 9:30 PM PHT'
                        }
                except Exception as e2:
                    return {'symbol': symbol, 'status': 'ERROR', 'message': str(e2)}
            return {'symbol': symbol, 'status': 'ERROR', 'message': err_str}

    def close_all_positions(self) -> List[Dict[str, Any]]:
        try:
            orders = self.trading_client.close_all_positions(cancel_orders=True)
            return [{'order_id': str(o.id), 'symbol': o.symbol, 'status': str(o.status)} for o in orders]
        except Exception as e:
            # Fallback to closing positions individually via limit orders if market is closed
            closed = []
            for p in self.get_positions():
                res = self.close_position(p['symbol'])
                closed.append(res)
            return closed

    def harvest_green_positions(self, min_profit_pct: float = 0.0) -> Dict[str, Any]:
        """Closes all winning/green positions to immediately lock in profits into cash."""
        positions = self.get_positions()
        green_positions = [
            p for p in positions
            if p.get('unrealized_pl', 0.0) > 0 and p.get('unrealized_plpc', 0.0) >= min_profit_pct
        ]

        harvested = []
        total_profit_banked = 0.0

        for p in green_positions:
            sym = p['symbol']
            pl = p.get('unrealized_pl', 0.0)
            try:
                res = self.close_position(sym)
                if res.get('status') in ('CLOSED', 'QUEUED_FOR_OPEN') or res.get('order_id'):
                    harvested.append({
                        'symbol': sym,
                        'profit_locked': pl,
                        'profit_pct': p.get('unrealized_plpc', 0.0),
                        'order_id': res.get('order_id'),
                        'status': res.get('status')
                    })
                    total_profit_banked += pl
            except Exception as e:
                print(f"Error harvesting {sym}: {e}")

        return {
            'status': 'SUCCESS',
            'harvested_count': len(harvested),
            'total_profit_banked': round(total_profit_banked, 2),
            'harvested_positions': harvested
        }
