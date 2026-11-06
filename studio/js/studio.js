/* ===========================================================
   EDIT YOUR BUSINESS DETAILS HERE
   Everything on index.html and order.html that shows a price,
   your name, or a contact link is filled in from this object.
   =========================================================== */
const STUDIO = {
  brandName: 'Ever After Sites',
  essentialPrice: 'R1 499',
  bespokePrice: 'R4 999',
  extraSessionPrice: 'R450',      // optional add-on: extra session with the developer
  essentialTurnaround: '7 days',
  bespokeTurnaround: '3–4 weeks',

  email: 'hello@example.com',     // TODO: your business email
  whatsapp: '27000000000',        // TODO: your number in international format, no + or spaces
  liveExample: 'https://henryenmaryketrou.co.za',

  // Where the order form is sent. Easiest free option:
  //   'https://formsubmit.co/your@email.com'  (confirm the first email they send you)
  // Leave empty to fall back to opening the client's email app with the answers.
  formEndpoint: ''
};

document.addEventListener('DOMContentLoaded', () => {
  /* ---- Fill in config values ---- */
  document.querySelectorAll('[data-cfg]').forEach((el) => {
    const v = STUDIO[el.dataset.cfg];
    if (v) el.textContent = v;
  });
  document.querySelectorAll('[data-cfg-href]').forEach((el) => {
    const key = el.dataset.cfgHref;
    if (key === 'email') el.href = `mailto:${STUDIO.email}`;
    else if (key === 'whatsapp') {
      const msg = encodeURIComponent(el.dataset.msg || `Hi! I'd like to know more about a wedding website.`);
      el.href = `https://wa.me/${STUDIO.whatsapp}?text=${msg}`;
    } else if (STUDIO[key]) el.href = STUDIO[key];
  });
  document.title = document.title.replace('{brand}', STUDIO.brandName);
  const yearEl = document.querySelector('[data-year]');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---- Mobile nav ---- */
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }));
  }

  /* ---- Screenshot lightbox ---- */
  const lb = document.getElementById('lightbox');
  if (lb) {
    const lbImg = lb.querySelector('img');
    const close = () => { lb.classList.remove('open'); lbImg.src = ''; };
    document.querySelectorAll('[data-full]').forEach((btn) => {
      btn.addEventListener('click', () => {
        lbImg.src = btn.dataset.full;
        lbImg.alt = btn.querySelector('img')?.alt || '';
        lb.classList.add('open');
      });
    });
    lb.addEventListener('click', (e) => { if (e.target !== lbImg) close(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  }

  /* ---- Order form ---- */
  const form = document.getElementById('order-form');
  if (form) setupOrderForm(form);
});

function setupOrderForm(form) {
  const wrap = document.getElementById('order-wrap');
  const status = document.getElementById('form-status');

  // Preselect package from ?package=bespoke
  const wanted = new URLSearchParams(location.search).get('package');
  if (wanted) {
    const radio = form.querySelector(`input[name="package"][value="${wanted}"]`);
    if (radio) radio.checked = true;
  }

  const syncPackage = () => {
    const bespoke = form.querySelector('input[name="package"]:checked')?.value === 'bespoke';
    wrap.classList.toggle('is-bespoke', bespoke);
    // Hidden bespoke questions must not block submission of the Essential form
    form.querySelectorAll('.bespoke-only [data-required]').forEach((el) => { el.required = bespoke; });
  };
  form.querySelectorAll('input[name="package"]').forEach((r) => r.addEventListener('change', syncPackage));
  syncPackage();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const bespoke = wrap.classList.contains('is-bespoke');

    // Collect answers, skipping hidden bespoke-only questions for Essential
    const lines = [];
    const data = new FormData();
    const seen = new Set();
    form.querySelectorAll('input, select, textarea').forEach((el) => {
      if (!el.name || seen.has(el.name)) return;
      if (!bespoke && el.closest('.bespoke-only')) return;
      seen.add(el.name);
      let value;
      if (el.type === 'checkbox' || el.type === 'radio') {
        value = [...form.querySelectorAll(`[name="${el.name}"]:checked`)].map((c) => c.value).join(', ');
      } else {
        value = el.value.trim();
      }
      if (!value) return;
      const label = el.dataset.label || el.name;
      lines.push(`${label}: ${value}`);
      data.append(label, value);
    });

    const couple = form.querySelector('[name="partner1"]').value.trim() + ' & ' + form.querySelector('[name="partner2"]').value.trim();
    const subject = `New ${bespoke ? 'Bespoke' : 'Essential'} wedding website order — ${couple}`;
    data.append('_subject', subject);
    data.append('_template', 'table');
    data.append('_captcha', 'false');

    if (STUDIO.formEndpoint) {
      status.className = 'form-status';
      status.textContent = 'Sending…';
      try {
        const res = await fetch(STUDIO.formEndpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
        if (!res.ok) throw new Error(res.statusText);
        form.reset();
        syncPackage();
        status.className = 'form-status ok';
        status.textContent = `Thank you! Your answers are in. We'll be in touch within 1–2 working days.`;
        return;
      } catch (err) {
        status.className = 'form-status err';
        status.textContent = 'Something went wrong sending online — opening your email app instead.';
      }
    }

    const body = encodeURIComponent(lines.join('\n\n'));
    location.href = `mailto:${STUDIO.email}?subject=${encodeURIComponent(subject)}&body=${body}`;
  });
}
