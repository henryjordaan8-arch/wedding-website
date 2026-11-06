# Repository guide

This repo holds three things:
- **Root** (`index.html`, `css/`, `js/`, …): Maryke & Henry's live wedding site (henryenmaryketrou.co.za). Don't change it unless asked.
- **`studio/`**: the sales site for the wedding-website business, with its order form (`studio/order.html`). Prices, brand and contact details are in the `STUDIO` object in `studio/js/studio.js`.
- **`builder/`**: the generator that turns an order's build file into a client website (see `builder/README.md`).

## When the user pastes a new order (a JSON "build file")

Build the site with minimal back-and-forth:

1. **Save** the JSON to `builder/clients/<slug>/order.json`. Use the slug `partner1-partner2` (lowercase, ASCII, hyphens).
2. **Photos.** If a link was given, try to download the photos into `builder/clients/<slug>/photos/` (Drive and WeTransfer
   often block automated downloads, so don't fight it; note it in the checklist). If the user already put photos
   there, look at them and rename the best portrait/couple shot to `hero.<ext>`.
3. **Polish the wording in `order.json` only.** Never invent facts like times, prices, policies or addresses.
   - If `style.welcome` is blank, write 2–3 warm, natural sentences in the site language, mentioning the venue/town.
   - If `registry.message` is blank and there are registry links or bank details, write a gracious one-liner.
   - If `style.language` is `af`, translate English programme titles and FAQ questions (the form pre-fills some in
     English) into natural Afrikaans. Fix capitalisation and obvious typos. Keep the couple's own phrasing otherwise.
   - Drop FAQ rows without answers. Make sure website links start with https://.
4. **Build:** `python3 builder/build.py builder/clients/<slug>/order.json`.
5. **Check:** serve the repo (`python3 -m http.server 8765`) and screenshot `/builder/sites/<slug>/` index and two
   other pages at 1366px and 390px wide with Playwright. Look for overflow, empty sections and broken images. Fix any
   problems through `order.json` or the template, then rebuild.
6. **Commit** the order, photos and generated site together, then push to the working branch.
7. **Report back** briefly:
   - the build checklist (missing info to chase),
   - what you wrote or changed on the couple's behalf (so it can be confirmed in their session),
   - 3–5 suggestions for their **developer session** (Essential includes one; Bespoke includes three).

Package rules: Essential (R900) gets 15 palettes, 8 lettering styles, the envelope / card / monogram openings,
up to 12 photos, one language and 1 developer session. Bespoke-only features are the doors and curtain openings, up to 40
photos, both languages, exact custom colours and fonts, extra pages, special features, 3 sessions and 12 months online.
The form locks these for Essential, and `build.py` falls back (with a checklist note) if an Essential order asks for them.

Bespoke orders (`"package": "bespoke"`) are built the same way as a starting point. The `bespoke` answers then
guide hand-made changes to the generated site.
