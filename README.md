# Overwatch

**A free, self-hosted live threat map for your phone.** Overwatch shows military flights, emergency squawks, earthquakes, wildfires, severe weather, world conflict news, and local and state crime data on one map. There's no subscription and no account, and no server to run. It's a single HTML file on GitHub Pages.

Built as a do-it-yourself alternative to paid "threat map" apps, using the same kinds of public data they use. It also adds a local layer centered on Columbus, Nebraska, and you can move that to any home location.

---

## What it does

| Layer | What you see | Source | Refresh |
|---|---|---|---|
| **Military** | Military aircraft worldwide, color-coded by role (tanker, recon/ISR, bomber, fighter, transport, command/VIP, helicopter, drone, trainer) | [adsb.lol](https://adsb.lol), falls back to [airplanes.live](https://airplanes.live), then [adsb.fi](https://adsb.fi) | 30 sec |
| **Emergencies** | Any aircraft squawking 7500 (hijack), 7600 (radio failure) or 7700 (emergency) | Same ADS-B feeds | 60 sec |
| **Quakes** | Earthquakes M2.5+ in the past 24 hours | [USGS](https://earthquake.usgs.gov) | 5 min |
| **Fires & storms** | Open wildfires, severe storms, volcanoes, floods | [NASA EONET](https://eonet.gsfc.nasa.gov) | 30 min |
| **Weather** | Active NWS alerts for your state, drawn as polygons, plus alerts covering your home | [National Weather Service](https://www.weather.gov) | 5 min |
| **World events** | Places with heavy news coverage of strikes, shelling, attacks, etc. in the past 24 hours, with article links | [GDELT](https://www.gdeltproject.org) | 15 min |
| **Police / crime** | Every police and sheriff agency in your state. Tap one to see its crime numbers | [FBI Crime Data Explorer](https://cde.ucr.cjis.gov) | Cached 30 days |

Nearby military bases are marked on the map: Offutt, Lincoln ANGB, Whiteman, McConnell, F.E. Warren and Ellsworth.

### Tabs

- **Near me:** weather alerts at home, emergencies nearby, and military aircraft inside your radius sorted by distance and direction ("44 mi SE · FL240"). Tap any row to fly to it on the map.
- **Feed:** one timeline of everything: squawks, weather alerts, notable quakes, fires and storms, and crime news.
- **Crime:**
  - Official FBI numbers for violent and property crime: latest full year, change from the year before, rate per 100k compared with your state and the U.S., percent cleared, and a 10-year trend.
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

### Recommended: free FBI data key

Crime numbers work out of the box on the shared `DEMO_KEY`, which allows about 30 requests an hour. For regular use, get a free key at **[api.data.gov/signup](https://api.data.gov/signup/)** and paste it into **Settings → api.data.gov key**.

---

## Settings

Tap the gear in the top right.

- **Home:** name, latitude and longitude, or tap *Use my current location*. Default is Columbus, NE.
- **"Near me" radius:** default 300 miles.
- **State:** used for weather alerts, crime stats and the agency list. Default `NE`.
- **Watchlist:** callsign prefixes, aircraft type codes or hex codes, separated by commas (for example `RCH, SAM, COBRA, B52`). Matches get a yellow ring and an alert.
- **Saved police agencies:** one per line, in the form `ORI = Name`. Tap an agency on the map and hit *Save* to add it.
- **API keys:** api.data.gov (FBI crime data), and optionally Anthropic for in-app AI briefs.
- **Advanced:** edit the search terms behind the world-events map and the crime news feeds.
- **Data sources:** live status of every feed, showing whether it's working, how many items it returned, and when it last updated. Check here first if something looks empty.

---

## Known limits

- **Not every military flight shows up.** Only aircraft broadcasting ADS-B appear, and many military flights turn their transponders off. Paid apps have the same blind spot.
- **There's no live local crime feed.** Columbus and Platte County don't publish a free real-time incident feed. FBI numbers are yearly and run about a year behind. The news feed and quick links fill in the present.
- **There's no ship tracking yet.** The free AIS source ([aisstream.io](https://aisstream.io)) doesn't allow direct browser connections, so it needs a small relay server. That's planned for a later version.
- **Alerts only fire while the app is open.** There are no background push notifications.
- **The free feeds have no uptime guarantee.** Military flights fall back across three providers. Other feeds retry automatically after about 90 seconds.

---

## Privacy

- No accounts, no tracking, no backend. Everything runs in your browser.
- Settings and API keys are saved in your browser's local storage on **your device only**. They are never in this repo and never sent anywhere except the API they belong to.
- If you add an Anthropic key, use one with a spending limit, since anyone using that phone's browser could read it.
- **Never commit API keys to this repository.**

---

## Tech

- Single self-contained `index.html` written in plain JavaScript, with no build step.
- [Leaflet](https://leafletjs.com) for the map, using [CARTO](https://carto.com) dark basemap tiles.
- Mobile-first layout with a bottom sheet for the tabs.

## Data credits

Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, tiles © [CARTO](https://carto.com/attributions). Aircraft data from [adsb.lol](https://adsb.lol) (ODbL), [airplanes.live](https://airplanes.live) and [adsb.fi](https://adsb.fi). Earthquakes from USGS. Natural events from NASA EONET. Weather alerts from the National Weather Service. News and event data from the GDELT Project. Crime statistics from the FBI Uniform Crime Reporting Program via the Crime Data Explorer API.

## Disclaimer

Overwatch is for general awareness only. It is **not** an emergency alerting system. Always follow official sources and local authorities, and **call 911 in an emergency**.
