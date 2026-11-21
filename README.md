# Overwatch

**A free, self-hosted live threat map for your phone.** Overwatch shows military flights, emergency squawks, earthquakes, wildfires, severe weather, world conflict news, and local and state crime data on one map. There's no subscription. It's a single HTML file on GitHub Pages, plus an optional free relay you own for the aircraft feeds.

Built as a do-it-yourself alternative to paid "threat map" apps, using the same kinds of public data they use. It also adds a local layer centered on Columbus, Nebraska, and you can move that to any home location.

---

## What it does

| Layer | What you see | Source | Refresh |
|---|---|---|---|
| **Military** | Military aircraft worldwide, color-coded by role (tanker, recon/ISR, bomber, fighter, transport, command/VIP, helicopter, drone, trainer) | [adsb.lol](https://adsb.lol), falls back to [airplanes.live](https://airplanes.live), then [adsb.fi](https://adsb.fi). **Needs the [home relay](#home-relay).** | 30 sec |
| **Emergencies** | Any aircraft squawking 7500 (hijack), 7600 (radio failure) or 7700 (emergency) | Same ADS-B feeds. **Needs the home relay.** | 60 sec |
| **Quakes** | Earthquakes M2.5+ in the past 24 hours | [USGS](https://earthquake.usgs.gov) | 5 min |
| **Fires & storms** | Open wildfires, severe storms, volcanoes, floods | [NASA EONET](https://eonet.gsfc.nasa.gov) | 30 min |
| **Weather** | Active NWS alerts for your state, drawn as polygons, plus alerts covering your home | [National Weather Service](https://www.weather.gov) | 5 min |
| **World events** | Places with heavy news coverage of strikes, shelling, attacks, etc. in the past 24 hours, with article links | [GDELT](https://www.gdeltproject.org) headlines, placed by the country or city they name, so locations are approximate. GDELT's own map API now returns 404. A relay makes it more reliable. | 15 min |
| **Police / crime** | Every police and sheriff agency in your state. Tap one to see its crime numbers | [FBI Crime Data Explorer](https://cde.ucr.cjis.gov) | Cached 30 days |

Nearby military bases are marked on the map: Offutt, Lincoln ANGB, Whiteman, McConnell, F.E. Warren and Ellsworth.

### Tabs

- **Near me:** weather alerts at home, emergencies nearby, and military aircraft inside your radius sorted by distance and direction ("44 mi SE · FL240"). Tap any row to fly to it on the map.
- **Feed:** one timeline of everything: squawks, weather alerts, notable quakes, fires and storms, and crime news.
- **Crime:**
  - Official FBI numbers for violent and property crime: latest full year, change from the year before, rate per 100k compared with your state and the U.S., percent cleared, the current year so far, and a 10-year trend.
  - Comes preloaded with Columbus PD, Platte County Sheriff and Nebraska statewide. Search for any agency in your state, or tap one on the map.
  - Recent local and statewide crime and police news.
  - Quick links to the jail roster, sheriff press releases, sex offender registry, and more.
- **Brief:** a plain-language summary of everything above.
  - **Copy for Claude** copies the live data with a briefing request so you can paste it into Claude for a written analysis. This is free and needs no key.
  - Optionally, add your own Anthropic API key to write the brief right in the app.

### Alerts

While the app is open, a banner pops up and the phone vibrates when:
- a new 7500 hijack squawk appears anywhere
- a 7600 or 7700 squawk appears within twice your radius
- a weather **warning** is issued for your home location
- an M6+ quake hits anywhere, or an M3+ quake within your radius
- an aircraft on your **watchlist** enters your radius

---

## Setup (GitHub Pages)

1. Create a new repository, for example `overwatch`.
2. Upload `index.html` (and this README) to the root of the repo.
3. Go to **Settings → Pages**. Under *Build and deployment*, set Source to **Deploy from a branch**, Branch to **main**, and folder to **/ (root)**. Save.
4. After a minute or two, the app is live at `https://<your-username>.github.io/overwatch/`.
5. On Android, open that link in Chrome, then choose **⋮ → Add to Home screen**.

> Opening `index.html` straight from your phone's files usually won't work. The live data feeds need the page to be served from a real web address, which GitHub Pages provides.

## Relay setup

> **Update (Nov 2026):** the flight-data services (adsb.lol, airplanes.live, adsb.fi) **block shared cloud servers**, including Cloudflare Workers. In testing they returned `429` and `403`. The Cloudflare relay below still helps with GDELT news. **For aircraft, use the [home relay](#home-relay).**

The military-aircraft and emergency-squawk feeds, and GDELT's news API, **don't let web pages read them directly**. They send no CORS headers, or they send error pages without them. Every browser blocks them, and no app setting can get around that. The fix is a tiny relay that runs on **your own free Cloudflare account**. Its code is in [`relay/`](relay/).

The relay is locked down:
- It only fetches from the four data hosts it needs.
- It only answers your GitHub Pages site.
- It only allows read-only requests.

Cloudflare's free plan allows 100,000 requests a day, far more than one phone uses.

### Quick way: copy and paste (about 5 minutes, works from a phone)

1. Go to **[dash.cloudflare.com](https://dash.cloudflare.com/sign-up)** and create a free account. Verify your email.
2. Open **Workers & Pages → Create**, choose the **Hello World** starter, name it `overwatch-relay`, and tap **Deploy**.
3. Tap **Edit code**. Delete everything in the editor.
4. Open **[relay/src/index.js (raw)](https://raw.githubusercontent.com/timothybrinkman/overwatch/main/relay/src/index.js)**, select all, copy, and paste it into the editor. Tap **Deploy**.
5. Copy your Worker's address. It looks like `https://overwatch-relay.<your-name>.workers.dev`. Open it in a browser and it should say **"Overwatch relay is running."**
6. In Overwatch, open **Settings → Relay URL**, paste the address, tap **Test relay**, then **Save**.

### Alternative: deploy straight from this repo

In Cloudflare, go to **Workers & Pages → Create → Import a repository**, connect GitHub, pick this repo, and set the **root directory** to `relay`. The default deploy command (`npx wrangler deploy`) uses [`relay/wrangler.toml`](relay/wrangler.toml). After that, every change pushed to `relay/` redeploys on its own. Cloudflare's menu names change from time to time, so look for the closest match.

> **Hosting Overwatch somewhere other than `timothybrinkman.github.io`?** Add your site's address to `ALLOWED_ORIGINS` at the top of `relay/src/index.js`.

## Home relay

This is the relay that makes **military aircraft and emergency squawks** work. It runs on a PC or mini server on your home internet connection, which the flight-data services accept. [Tailscale Funnel](https://tailscale.com/kb/1223/funnel) (free) gives it a fixed `https://` address your phone can reach from anywhere.

You need a Windows, Mac or Linux machine with Python 3, left running. It's a good first job for a home server.

1. **Get the script.** Save [`relay/home_relay.py`](https://raw.githubusercontent.com/timothybrinkman/overwatch/main/relay/home_relay.py) into a folder, for example `C:\overwatch`.
2. **Run it.** Open a terminal in that folder and run `python home_relay.py`. It says it's running on `http://localhost:8787`. Then open
   `http://localhost:8787/?url=https%3A%2F%2Fapi.adsb.lol%2Fv2%2Fmil` in a browser. You should see a page of JSON aircraft data.
3. **Install Tailscale** from [tailscale.com/download](https://tailscale.com/download) and sign in. Google or GitHub login is fine.
4. **Open it to the internet.** In a second terminal, run `tailscale funnel --bg 8787`. The first time, it prints a link to turn Funnel on for your account. Open it, approve, and run the command again. It prints your address, something like `https://desktop-xxxx.tailxxxx.ts.net`.
5. **Connect Overwatch.** On your phone, go to **Settings → Relay URL**, paste that address, tap **Test relay**, then **Save**.

**Keep it running after a reboot.** `--bg` keeps the Funnel on. For the script itself, on Windows use **Task Scheduler → Create Basic Task → When I log on → Start a program**. Set the program to `pythonw` (or `python`), the argument to `home_relay.py`, and *Start in* to your folder.

The home relay is locked down the same way as the Cloudflare one: it only fetches the four data hosts, only answers your Overwatch site, and only listens on `localhost`. Tailscale is what makes it reachable from outside.

## Free FBI data key (recommended)

Crime numbers work out of the box on the shared `DEMO_KEY`, which allows about 30 requests an hour. For regular use, get a free key at **[api.data.gov/signup](https://api.data.gov/signup/)** and paste it into **Settings → api.data.gov key**.

---

## Settings

Tap the gear in the top right.

- **Home:** name, latitude and longitude, or tap *Use my current location*. Default is Columbus, NE.
- **"Near me" radius:** default 300 miles.
- **State:** used for weather alerts, crime stats and the agency list. Default `NE`.
- **Relay URL:** your Cloudflare relay (see [Relay setup](#relay-setup)). *Test relay* checks it on the spot.
- **Watchlist:** callsign prefixes, aircraft type codes or hex codes, separated by commas (for example `RCH, SAM, COBRA, B52`). Matches get a yellow ring and an alert.
- **Saved police agencies:** one per line, in the form `ORI = Name`. Tap an agency on the map and hit *Save* to add it.
- **API keys:** api.data.gov (FBI crime data), and optionally Anthropic for in-app AI briefs.
- **Advanced:** edit the search terms behind the world-events map and the crime news feeds.
- **Data sources:** live status of every feed, showing whether it's working, how many items it returned, and when it last updated. Check here first if something looks empty.

---

## Known limits

- **Not every military flight shows up.** Only aircraft broadcasting ADS-B appear, and many military flights turn their transponders off. Paid apps have the same blind spot.
- **There's no live local crime feed.** Columbus and Platte County don't publish a free real-time incident feed. FBI numbers are yearly and run about a year behind. The news feed and quick links fill in the present.
- **Aircraft need the home relay.** The free flight-data services block cloud servers, so aircraft only load through a relay on a home connection. Without one, the Military and Emergencies layers stay empty and the app shows setup steps. Everything else works without it.
- **GDELT is flaky.** It often drops requests, so the app retries and keeps the last good world map and news on your phone.
- **There's no ship tracking yet.** The free AIS source ([aisstream.io](https://aisstream.io)) streams over a live connection that needs a different kind of relay. It's planned for a later version.
- **Alerts only fire while the app is open.** There are no background push notifications.
- **The free feeds have no uptime guarantee.** Military flights fall back across three providers. Other feeds retry automatically after about 90 seconds.

---

## Privacy

- No accounts and no tracking. Everything runs in your browser, except the optional relay, which runs on your own Cloudflare account and only passes public flight and news data through.
- Settings and API keys are saved in your browser's local storage on **your device only**. They are never in this repo and never sent anywhere except the API they belong to.
- If you add an Anthropic key, use one with a spending limit, since anyone using that phone's browser could read it.
- **Never commit API keys to this repository.**

---

## Tech

- Single self-contained `index.html` written in plain JavaScript, with no build step.
- [Leaflet](https://leafletjs.com) for the map, using [CARTO](https://carto.com) dark basemap tiles.
- Mobile-first layout with a bottom sheet for the tabs.
- `relay/`: a small Cloudflare Worker (`src/index.js` + `wrangler.toml`) and a home relay (`home_relay.py`).

```
index.html          the whole app
relay/src/index.js  the relay Worker
relay/wrangler.toml Cloudflare config for repo-based deploys
relay/home_relay.py home relay for aircraft (Python, no installs)
.nojekyll           tells GitHub Pages to serve files as-is
```

## Data credits

Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, tiles © [CARTO](https://carto.com/attributions). Aircraft data from [adsb.lol](https://adsb.lol) (ODbL), [airplanes.live](https://airplanes.live) and [adsb.fi](https://adsb.fi). Earthquakes from USGS. Natural events from NASA EONET. Weather alerts from the National Weather Service. News and event data from the GDELT Project. Crime statistics from the FBI Uniform Crime Reporting Program via the Crime Data Explorer API.

## Disclaimer

Overwatch is for general awareness only. It is **not** an emergency alerting system. Always follow official sources and local authorities, and **call 911 in an emergency**.
