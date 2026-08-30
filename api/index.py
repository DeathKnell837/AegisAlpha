# api/index.py - Vercel Serverless Function Entrypoint
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.agent_desk import AegisOptionsDesk
from alpaca.trading.enums import OrderSide, OrderType

# Initialize desk
desk = AegisOptionsDesk()

class handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ['/api/account', '/account']:
            try:
                acc = desk.alpaca.get_account()
                self.send_json_response(acc)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path in ['/api/positions', '/positions']:
            try:
                pos = desk.alpaca.get_positions()
                self.send_json_response(pos)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path in ['/api/logs', '/logs']:
            try:
                logs = [l.model_dump() for l in desk.trade_logs]
                self.send_json_response(logs)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path.startswith('/api/chain') or path.startswith('/chain'):
            query = parse_qs(parsed.query)
            sym = query.get('symbol', ['SPY'])[0].upper()
            try:
                chain = desk.alpaca.get_option_chain_candidates(sym)
                self.send_json_response(chain)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path in ['/api/orders', '/orders']:
            try:
                orders = desk.alpaca.trading_client.get_orders()
                out = []
                for o in orders:
                    out.append({
                        "order_id": str(o.id) if hasattr(o, 'id') else None,
                        "symbol": o.symbol if hasattr(o, 'symbol') else None,
                        "qty": float(o.qty) if hasattr(o, 'qty') and o.qty else 0.0,
                        "side": str(o.side) if hasattr(o, 'side') else None,
                        "status": str(o.status) if hasattr(o, 'status') else None,
                        "type": str(o.order_type) if hasattr(o, 'order_type') else None,
                        "submitted_at": str(o.submitted_at) if hasattr(o, 'submitted_at') else None
                    })
                self.send_json_response(out)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        self.send_json_response({'status': 'AegisAlpha Vercel API Online'}, 200)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ['/api/run-scan', '/run-scan']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                payload = json.loads(post_data.decode('utf-8')) if post_data else {}
                watchlist = payload.get('watchlist', ['SPY', 'QQQ', 'NVDA', 'AAPL'])
                results = desk.run_cycle(watchlist)
                self.send_json_response([r.model_dump() for r in results])
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path in ['/api/kill-switch', '/kill-switch']:
            try:
                res = desk.alpaca.close_all_positions()
                self.send_json_response({'status': 'SUCCESS', 'closed_count': len(res)})
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path in ['/api/close-position', '/close-position']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                payload = json.loads(post_data.decode('utf-8')) if post_data else {}
                symbol = payload.get('symbol')
                res = desk.alpaca.close_position(symbol)
                self.send_json_response(res)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        elif path in ['/api/manual-order', '/manual-order']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                payload = json.loads(post_data.decode('utf-8')) if post_data else {}
                symbol = payload.get('symbol')
                qty = float(payload.get('qty', 1))
                side_str = payload.get('side', 'buy').lower()
                type_str = payload.get('order_type', 'market').lower()
                limit_price = payload.get('limit_price')
                
                side = OrderSide.BUY if side_str == 'buy' else OrderSide.SELL
                order_type = OrderType.MARKET if type_str == 'market' else OrderType.LIMIT
                
                res = desk.alpaca.place_order_simple(symbol, qty, side, order_type, limit_price)
                self.send_json_response(res)
            except Exception as e:
                self.send_json_response({'error': str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()
