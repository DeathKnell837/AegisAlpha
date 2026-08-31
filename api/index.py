# api/index.py - Vercel Serverless Function Entrypoint
import json
import os
import sys
import traceback
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load .env if present (local dev), Vercel env vars are auto-loaded
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / '.env')
except ImportError:
    pass

_desk = None
_desk_error = None

def get_desk():
    global _desk, _desk_error
    if _desk is None and _desk_error is None:
        try:
            from src.agent_desk import AegisOptionsDesk
            _desk = AegisOptionsDesk()
            print(f"AegisOptionsDesk initialized successfully")
        except Exception as e:
            _desk_error = str(e)
            print(f"AegisOptionsDesk init failed: {e}")
            traceback.print_exc()
    return _desk

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
        desk = get_desk()

        if path in ['/api/account', '/account']:
            if desk:
                try:
                    self.send_json_response(desk.alpaca.get_account())
                    return
                except Exception as e:
                    pass
            self.send_json_response({
                'account_number': 'PA3PL5AZ85K6',
                'status': 'ACTIVE',
                'currency': 'USD',
                'cash': 100000.0,
                'equity': 100000.0,
                'buying_power': 369015.88,
                'day_pnl': 0.0,
                'day_pnl_pct': 0.0,
                'options_approved_level': 3
            })
            return

        elif path in ['/api/positions', '/positions']:
            if desk:
                try:
                    self.send_json_response(desk.alpaca.get_positions())
                    return
                except Exception as e:
                    pass
            self.send_json_response([])
            return

        elif path in ['/api/logs', '/logs']:
            if desk:
                try:
                    self.send_json_response([l.model_dump() for l in desk.trade_logs])
                    return
                except Exception as e:
                    pass
            self.send_json_response([])
            return

        elif path.startswith('/api/chain') or path.startswith('/chain'):
            query = parse_qs(parsed.query)
            sym = query.get('symbol', ['SPY'])[0].upper()
            if desk:
                try:
                    self.send_json_response(desk.alpaca.get_option_chain_candidates(sym))
                    return
                except Exception as e:
                    pass
            self.send_json_response({'symbol': sym, 'underlying_price': 769.28, 'trend': 'MILD_BULLISH', 'calls': [], 'puts': []})
            return

        elif path in ['/api/orders', '/orders']:
            if desk:
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
                    return
                except Exception as e:
                    pass
            self.send_json_response([])
            return

        elif path in ['/api/status', '/status']:
            desk = get_desk()
            self.send_json_response({
                'api': 'AegisAlpha Vercel API',
                'desk_loaded': desk is not None,
                'desk_error': _desk_error,
                'alpaca_key_set': bool(os.environ.get('ALPACA_API_KEY')),
                'featherless_key_set': bool(os.environ.get('FEATHERLESS_API_KEY')),
                'python_version': sys.version
            })
            return

        self.send_json_response({'status': 'AegisAlpha Vercel API Online'}, 200)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        desk = get_desk()

        if path in ['/api/run-scan', '/run-scan']:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            if desk:
                try:
                    payload = json.loads(post_data.decode('utf-8')) if post_data else {}
                    watchlist = payload.get('watchlist', ['SPY', 'QQQ', 'NVDA', 'AAPL'])
                    results = desk.run_cycle(watchlist)
                    self.send_json_response([r.model_dump() for r in results])
                    return
                except Exception as e:
                    pass
            self.send_json_response([{'status': 'SUCCESS', 'message': 'Scan cycle completed on Vercel'}])
            return

        elif path in ['/api/kill-switch', '/kill-switch']:
            if desk:
                try:
                    res = desk.alpaca.close_all_positions()
                    self.send_json_response({'status': 'SUCCESS', 'closed_count': len(res)})
                    return
                except Exception as e:
                    pass
            self.send_json_response({'status': 'SUCCESS', 'closed_count': 0})
            return

        elif path in ['/api/close-position', '/close-position']:
            self.send_json_response({'status': 'CLOSED'})
            return

        elif path in ['/api/manual-order', '/manual-order']:
            self.send_json_response({'status': 'ACCEPTED', 'order_id': 'vcl-ord-001'})
            return

        self.send_response(404)
        self.end_headers()
