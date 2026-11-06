# Wedding website builder

Turns an Essential order into a finished wedding website. The order comes from the questionnaire at `studio/order.html`.

```
order form  ──►  email with "Build file" (JSON)  ──►  builder/clients/<slug>/order.json
                                                       builder/clients/<slug>/photos/
                                     python3 builder/build.py builder/clients/<slug>/order.json
                                                  ──►  builder/sites/<slug>/   (finished static site)
```

## The quick way: give Claude the order

Copy the **Build file** from the order email and paste it into Claude Code with this prompt:

> New Essential order, please build it.
> Photos: *(paste the client's photo link, or say "I've put them in builder/clients/<slug>/photos")*
>
> ```json
> (paste the build file here)
> ```

Claude follows the steps in `CLAUDE.md`. It saves the order, tidies the wording (in Afrikaans if that's the
chosen language), builds the site, checks it on desktop and mobile, commits it, and gives you a checklist.
That checklist has anything missing from the order plus talking points for the client session.

## Doing it by hand

1. Create `builder/clients/<partner1>-<partner2>/order.json` and paste the build file into it.
2. Put the photos in `builder/clients/<slug>/photos/`. Name the home-page photo `hero.jpg`; every other
   photo goes in the gallery. Photos are resized automatically (needs Pillow: `pip install pillow`).
3. Run `python3 builder/build.py builder/clients/<slug>/order.json` (Python 3.12+).
4. Read the **Checklist** it prints. Preview with `python3 -m http.server` and open
   `/builder/sites/<slug>/`.
5. Edit `order.json` and run the build again as many times as you like. The output folder is rebuilt from scratch
   each time, so make changes in `order.json`, not in the generated HTML. Bespoke work can start from the
   generated site and be edited directly.

## What the builder makes

| Page | Built from |
|------|-----------|
| Home | names, headline/tagline, hero photo, countdown to ceremony time, welcome message, page cards |
| Details | date/venue/dress strip, programme timeline, dress-code notes, separate reception venue |
| Venue | Google map + "Open in Google Maps" button from the address (or venue + town) |
| Stay | accommodation cards (phone, email, website) |
| Gallery | all photos except the hero, optionally locked behind question(s); answers are stored hashed |
| Registry | registry links and/or banking details |
| FAQ | question/answer pairs (questions without answers are dropped) |
| RSVP | on-site form emailed to the couple (FormSubmit), the couple's Google Form, or WhatsApp |

Options from the questionnaire:
- `style.palette`: `navy`, `burgundy`, `sage`, `dusty-blue`, `blush`, `terracotta`, `classic`
- `style.fonts`: `classic` (Playfair), `modern` (Cormorant), `romantic` (script names)
- `style.language`: `en`, `af`

Palettes, fonts and all fixed wording (English and Afrikaans) are at the top of `build.py`. The page
styling is in `template/style.css` and the behaviour is in `template/site.js`.

## Before handing over a site
- **RSVP emails:** FormSubmit needs a one-time activation. Send a test RSVP, then the couple clicks
  "Activate" in the email they receive. Until then, RSVPs fall back to WhatsApp.
- **Domain:** a `CNAME` file is written when a domain is given. Host each site as its own GitHub
  Pages repo (or Netlify) and point the domain's DNS at it.

## Example
`clients/example-anna-pieter/` is a demo order with placeholder photos. Its output is in
`sites/example-anna-pieter/`.
