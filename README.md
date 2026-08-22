# Maryke & Henry — Wedding Website

A simple static wedding website. No build step required — just plain HTML, CSS
and JavaScript.

**Wedding date:** 20 February 2027
**Venue:** Venue Nouveau, Pretoria

## Pages

| File                  | Section                              |
|------------------------|--------------------------------------|
| `index.html`           | Home / welcome + countdown           |
| `details.html`         | Event details & schedule             |
| `accommodation.html`   | Accommodation suggestions            |
| `travel.html`          | Getting there, parking, map          |
| `gallery.html`         | Photo gallery                        |
| `registry.html`        | Gift registry / honeymoon fund       |
| `faq.html`             | Frequently asked questions           |
| `rsvp.html`            | RSVP (embedded Google Form)          |

## Things still marked as placeholders

Search each page for text in a dashed box (class `todo-note`) — these mark
content you still need to fill in, including:

- Ceremony/reception times and dress code (`details.html`, `index.html`)
- Real accommodation options near Venue Nouveau (`accommodation.html`)
- Travel/parking/shuttle info (`travel.html`)
- Your own photos (`gallery.html`)
- Registry / honeymoon fund links (`registry.html`)
- FAQ answers (`faq.html`)
- Contact details (`rsvp.html`)

## Connecting your real RSVP Google Form

1. Create your RSVP form at [forms.google.com](https://forms.google.com).
2. Click **Send** (top right), then choose the **`<>`** embed tab.
3. Copy the URL inside the `src="..."` attribute of the code Google gives you.
4. Open `rsvp.html` and replace `src="about:blank"` on the `<iframe>` with
   that URL.
5. If your form is long or short, adjust the height in `css/style.css` under
   `.rsvp-form-wrap iframe { min-height: ... }`.

## Adding your own photos

Drop image files into `images/gallery/`, then in `gallery.html` replace each
`<div class="gallery-placeholder">...</div>` block with:

```html
<img src="images/gallery/your-photo.jpg" alt="Maryke and Henry">
```

## Previewing locally

No build tools needed. From this folder, run a simple local server, e.g.:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## Hosting

Because this is a static site, it can be hosted for free on services like:

- **GitHub Pages** — push this repo and enable Pages in the repo settings.
- **Netlify** or **Vercel** — drag-and-drop the folder or connect the repo.

## Colour theme

- Cream backgrounds (`#f9f4ea`, `#f1e9d8`)
- Burgundy accents (`#722f37`)
- Olive accents (`#6f7650`)

Colours and fonts are defined as CSS variables at the top of `css/style.css`
if you'd like to adjust them.
