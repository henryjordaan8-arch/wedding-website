# Wedding website studio (sales site)

The website you use to sell wedding websites. It's plain HTML/CSS/JS, so there's no build step.

| File | What it is |
|------|------------|
| `index.html` | Sales page: hero, screenshots of a real site, features, the two packages (R900 / R1 600), comparison, Bespoke sessions, FAQ |
| `order.html` | Client questionnaire. It emails a readable summary plus a JSON **build file** for `builder/`. Choosing **Bespoke** adds the in-depth questions. |
| `js/studio.js` | **Edit the `STUDIO` object at the top** to set the brand name, prices, turnaround times, email, WhatsApp and form endpoint |
| `css/studio.css` | Colours & fonts are in `:root` at the top |
| `images/examples/` | Screenshots of henryenmaryketrou.co.za used as examples |

## Before going live
1. Set `email`, `whatsapp` and the prices in `js/studio.js`.
2. Set `formEndpoint` so orders arrive in your inbox, e.g.
   `https://formsubmit.co/ajax/your@email.com`. The first submission sends a
   confirmation email to that address. Without an endpoint, the form opens the
   client's email app with their answers filled in. Long Bespoke answers can get
   cut off this way, so an endpoint is recommended.
3. Check the FAQ wording (deposit terms, hosting periods) matches how you work.

## Hosting
Right now it is served at `henryenmaryketrou.co.za/studio/`. For the real
business, copy the `studio/` folder into its own repository and connect your
business domain.

## Refreshing screenshots
Run the wedding site locally (`python3 -m http.server 8765` in the repo root),
then screenshot pages at 1280×800 (desktop) and 390×844 (mobile) into
`images/examples/`, keeping the same file names.
