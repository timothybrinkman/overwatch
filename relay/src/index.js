// Overwatch relay — a tiny Cloudflare Worker.
//
// The aircraft feeds (adsb.lol, airplanes.live, adsb.fi) and GDELT's map API
// don't allow web pages to read them directly (no CORS headers). This Worker
// fetches them server-side and hands the data back to the Overwatch page.
//
// Locked down on purpose:
//   - only the hosts in ALLOWED_HOSTS can be fetched (not an open proxy)
//   - only GET requests
//   - browsers only get the data when the page comes from ALLOWED_ORIGINS
//
// Usage:  https://<your-worker>.workers.dev/?url=<encoded https URL>

const ALLOWED_HOSTS = new Set([
  'api.adsb.lol',
  'api.airplanes.live',
  'opendata.adsb.fi',
  'api.gdeltproject.org',
]);

// Add your own site here if you host Overwatch somewhere else.
const ALLOWED_ORIGINS = [
  'https://timothybrinkman.github.io',
  'http://localhost',
  'http://127.0.0.1',
];

const UA = 'Overwatch-relay/1.0 (personal, non-commercial; github.com/timothybrinkman/overwatch)';

function corsHeaders(origin) {
  const h = {
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
  if (origin && ALLOWED_ORIGINS.some(o => origin === o || origin.startsWith(o + ':'))) {
    h['Access-Control-Allow-Origin'] = origin;
  }
  return h;
}

function reply(body, status, headers, type = 'application/json') {
  return new Response(typeof body === 'string' ? body : JSON.stringify(body), {
    status,
    headers: { ...headers, 'content-type': type, 'cache-control': 'no-store' },
  });
}

export default {
  async fetch(request) {
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (request.method !== 'GET') return reply({ error: 'GET only' }, 405, cors);

    const target = new URL(request.url).searchParams.get('url');
    if (!target) return reply('Overwatch relay is running.', 200, cors, 'text/plain');
    if (origin && !cors['Access-Control-Allow-Origin']) return reply({ error: 'Origin not allowed: ' + origin }, 403, cors);

    let url;
    try { url = new URL(target); } catch { return reply({ error: 'Bad url' }, 400, cors); }
    if (url.protocol !== 'https:' || !ALLOWED_HOSTS.has(url.hostname)) {
      return reply({ error: 'Host not allowed: ' + url.hostname }, 403, cors);
    }

    try {
      const upstream = await fetch(url.toString(), {
        headers: { 'User-Agent': UA, 'Accept': 'application/json, */*' },
        redirect: 'follow',
      });
      const headers = new Headers(cors);
      headers.set('content-type', upstream.headers.get('content-type') || 'application/json');
      headers.set('cache-control', 'no-store');
      headers.set('x-relay-upstream-status', String(upstream.status));
      return new Response(upstream.body, { status: upstream.status, headers });
    } catch (err) {
      return reply({ error: 'Upstream fetch failed', detail: String(err && err.message || err) }, 502, cors);
    }
  },
};
