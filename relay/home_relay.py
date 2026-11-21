#!/usr/bin/env python3
"""
Overwatch home relay.

The free flight-data services (adsb.lol, airplanes.live, adsb.fi) block shared
cloud servers such as Cloudflare Workers, but they accept requests from a normal
home internet connection. Run this on a PC or mini server at home, expose it
with Tailscale Funnel (see README → "Home relay"), and paste the address into
Overwatch → Settings → Relay URL.

Plain Python 3 standard library: nothing to install.  Run:  python home_relay.py

Locked down the same way as the Cloudflare relay:
  - only the hosts in ALLOWED_HOSTS can be fetched (not an open proxy)
  - only GET requests
  - browsers only get the data when the page comes from ALLOWED_ORIGINS
  - listens on 127.0.0.1 only; Tailscale Funnel is what makes it reachable
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8787

ALLOWED_HOSTS = {
    'api.adsb.lol',
    'api.airplanes.live',
    'opendata.adsb.fi',
    'api.gdeltproject.org',
}

# Add your own site here if you host Overwatch somewhere else.
ALLOWED_ORIGINS = (
    'https://timothybrinkman.github.io',
    'http://localhost',
    'http://127.0.0.1',
)

UA = 'Overwatch-home-relay/1.0 (personal, non-commercial; github.com/timothybrinkman/overwatch)'


class Relay(BaseHTTPRequestHandler):
    server_version = 'OverwatchRelay/1.0'

    def _origin(self):
        origin = self.headers.get('Origin', '')
        allowed = bool(origin) and any(origin == o or origin.startswith(o + ':') for o in ALLOWED_ORIGINS)
        return origin, (origin if allowed else None)

    def _send(self, status, body, ctype='application/json', allow=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Vary', 'Origin')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Max-Age', '86400')
        if allow:
            self.send_header('Access-Control-Allow-Origin', allow)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        _, allow = self._origin()
        self._send(204, b'', 'text/plain', allow)

    def do_POST(self):
        _, allow = self._origin()
        self._send(405, {'error': 'GET only'}, allow=allow)

    def do_GET(self):
        origin, allow = self._origin()
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        target = (query.get('url') or [None])[0]
        if not target:
            return self._send(200, 'Overwatch home relay is running.', 'text/plain', allow)
        if origin and not allow:
            return self._send(403, {'error': 'Origin not allowed: ' + origin})
        parsed = urllib.parse.urlparse(target)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
            return self._send(403, {'error': 'Host not allowed: %s' % parsed.hostname}, allow=allow)

        is_gdelt = parsed.hostname == 'api.gdeltproject.org'
        status, body, ctype = 502, b'', 'application/json'
        for attempt in range(3 if is_gdelt else 1):
            if attempt:
                time.sleep(5.5)  # GDELT allows about one request every 5 seconds
            try:
                req = urllib.request.Request(target, headers={'User-Agent': UA, 'Accept': 'application/json, */*'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    status, body = resp.status, resp.read()
                    ctype = resp.headers.get('Content-Type', 'application/json')
            except urllib.error.HTTPError as err:
                status, body = err.code, err.read()
                ctype = err.headers.get('Content-Type', 'text/plain')
            except Exception as err:  # network error, timeout, bad TLS…
                status, ctype = 502, 'application/json'
                body = json.dumps({'error': 'Upstream fetch failed', 'detail': str(err)}).encode()
            if not is_gdelt or (status == 200 and 'json' in ctype.lower()):
                break
        self._send(status, body, ctype, allow)

    def log_message(self, fmt, *args):
        print('%s  %s' % (time.strftime('%H:%M:%S'), fmt % args), flush=True)


if __name__ == '__main__':
    print('Overwatch home relay running on http://localhost:%d  (close this window or press Ctrl+C to stop)' % PORT, flush=True)
    print('Quick test: http://localhost:%d/?url=https%%3A%%2F%%2Fapi.adsb.lol%%2Fv2%%2Fmil' % PORT, flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), Relay).serve_forever()
