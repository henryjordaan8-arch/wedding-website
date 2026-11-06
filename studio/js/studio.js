/* ===========================================================
   EDIT YOUR BUSINESS DETAILS HERE
   Everything on index.html and order.html that shows a price,
   your name, or a contact link is filled in from this object.
   =========================================================== */
const STUDIO = {
  brandName: 'Ever After Sites',
  essentialPrice: 'R900',
  bespokePrice: 'R1 600',
  extraSessionPrice: 'R350',      // optional add-on: extra session with the developer
  essentialTurnaround: '7 days',
  bespokeTurnaround: '3–4 weeks',

  email: 'hello@example.com',     // TODO: your business email
  whatsapp: '27000000000',        // TODO: your number in international format, no + or spaces
  liveExample: 'https://henryenmaryketrou.co.za',
  // Demo sites made by the builder (update once client sites are hosted on their own domains)
  demoEnvelope: '../builder/sites/example-anna-pieter/index.html',
  demoMonogram: '../builder/sites/example-lize-ruan/index.html',
  demoOpenings: '../builder/sites/example-anna-pieter/openings.html',

  // Where the order form is sent. Easiest free option:
  //   'https://formsubmit.co/ajax/your@email.com'  (send one test order, then click 'Activate' in the email)
  // Leave empty to fall back to opening the client's email app with the answers.
  formEndpoint: ''
};

// Price difference between the packages, e.g. 'R700' (shown as "only R700 more")
const toNumber = (price) => Number(String(price).replace(/[^0-9]/g, ''));
STUDIO.upgradeDiff = 'R' + (toNumber(STUDIO.bespokePrice) - toNumber(STUDIO.essentialPrice)).toLocaleString('en-ZA').replace(/,/g, ' ');

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

/* ---------- Order form ---------- */
function setPath(obj, path, value) {
  const keys = path.split('.');
  let o = obj;
  keys.slice(0, -1).forEach((k) => { o = o[k] = o[k] || {}; });
  o[keys[keys.length - 1]] = value;
}

function getPath(obj, path) {
  return path.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
}

function setupRepeaters(form) {
  form.querySelectorAll('.repeater').forEach((rep) => {
    const first = rep.querySelector('.rep-row, .rep-card');
    const blank = first.cloneNode(true);
    blank.querySelectorAll('input, textarea').forEach((el) => { el.value = ''; el.removeAttribute('value'); });
    const max = Number(rep.dataset.max || 50);
    const addBtn = rep.querySelector('.rep-add');
    const refresh = () => {
      addBtn.hidden = rep.querySelectorAll('.rep-row, .rep-card').length >= max;
    };
    addBtn.addEventListener('click', () => {
      const row = blank.cloneNode(true);
      addBtn.before(row);
      row.querySelector('input, textarea')?.focus();
      refresh();
    });
    rep.addEventListener('click', (e) => {
      const btn = e.target.closest('.rep-remove');
      if (!btn) return;
      btn.closest('.rep-row, .rep-card').remove();
      refresh();
    });
    refresh();
  });
}

/* Turn the answers into the build file that builder/build.py reads */
function collectOrder(form, bespoke) {
  const order = { schema: 1, submitted: new Date().toISOString() };
  const skip = (el) => !bespoke && el.closest('.bespoke-only');

  form.querySelectorAll('[data-path]').forEach((el) => {
    if (skip(el) || el.closest('.repeater')) return;
    const path = el.dataset.path;
    if (el.type === 'checkbox') {
      const list = getPath(order, path) || [];
      if (el.checked) list.push(el.value);
      setPath(order, path, list);
    } else if (el.type === 'radio') {
      if (el.checked) setPath(order, path, el.value);
    } else {
      setPath(order, path, el.value.trim());
    }
  });

  form.querySelectorAll('.repeater').forEach((rep) => {
    if (skip(rep)) return;
    const items = [...rep.querySelectorAll('.rep-row, .rep-card')].map((row) => {
      const item = {};
      row.querySelectorAll('[data-key]').forEach((el) => { item[el.dataset.key] = el.value.trim(); });
      return item;
    }).filter((item) => Object.values(item).some(Boolean));
    setPath(order, rep.dataset.repeat, items);
  });

  // Single yes/no checkbox → boolean
  if (order.style) order.style.animations = (order.style.animations || []).includes('yes');
  if (order.photos) order.photos.home_strip = (order.photos.home_strip || []).includes('yes');
  // FAQ rows without an answer are left off the website
  order.faqs = (order.faqs || []).filter((f) => f.q && f.a);
  return order;
}

/* Human-readable version for the email */
function summarise(form, bespoke) {
  const lines = [];
  const seen = new Set();
  form.querySelectorAll('[data-label]').forEach((el) => {
    if (!bespoke && el.closest('.bespoke-only')) return;
    const label = el.dataset.label;
    if (seen.has(label)) return;
    if (el.classList.contains('repeater')) {
      seen.add(label);
      const rowsText = [...el.querySelectorAll('.rep-row, .rep-card')]
        .map((row) => [...row.querySelectorAll('[data-key]')].map((i) => i.value.trim()).filter(Boolean).join(' · '))
        .filter(Boolean);
      if (rowsText.length) lines.push(`${label}:\n  - ${rowsText.join('\n  - ')}`);
      return;
    }
    if (el.closest('.repeater')) return;
    seen.add(label);
    let value;
    if (el.type === 'checkbox' || el.type === 'radio') {
      value = [...form.querySelectorAll(`[data-label="${label}"]:checked`)].map((c) => c.value).join(', ');
    } else {
      value = el.value.trim();
    }
    if (value) lines.push(`${label}: ${value}`);
  });
  return lines.join('\n');
}

function setupOrderForm(form) {
  const wrap = document.getElementById('order-wrap');
  const status = document.getElementById('form-status');
  setupRepeaters(form);

  const wanted = new URLSearchParams(location.search).get('package');
  if (wanted) {
    const radio = form.querySelector(`input[name="package"][value="${wanted}"]`);
    if (radio) radio.checked = true;
  }

  const isBespoke = () => form.querySelector('input[name="package"]:checked')?.value === 'bespoke';
  /* Options marked data-bespoke-only are locked for Essential. Tapping one offers a one-click upgrade. */
  const locked = [...form.querySelectorAll('[data-bespoke-only]')];
  const showUpsell = (input) => {
    const field = input.closest('.field');
    let note = field.querySelector('.upsell');
    if (!note) {
      note = document.createElement('p');
      note.className = 'upsell';
      note.innerHTML = `<span>&#10022; This is a <strong>Bespoke</strong> option &mdash; only ${STUDIO.upgradeDiff} more, with 3 sessions, your exact colours and much more.</span> <button type="button" class="upsell-btn">Switch to Bespoke</button>`;
      note.querySelector('button').addEventListener('click', () => {
        form.querySelector('input[name="package"][value="bespoke"]').checked = true;
        syncPackage();
        input.checked = true;
        note.remove();
        form.querySelector('.pkg-switch').scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      field.appendChild(note);
    }
  };
  locked.forEach((input) => {
    const label = input.closest('.font-opt') || input.closest('label');
    label.addEventListener('click', () => { if (input.disabled) showUpsell(input); });
  });

  const syncPackage = () => {
    const bespoke = isBespoke();
    wrap.classList.toggle('is-bespoke', bespoke);
    form.querySelectorAll('.bespoke-only [data-required]').forEach((el) => { el.required = bespoke; });
    locked.forEach((input) => {
      input.disabled = !bespoke;
      (input.closest('.font-opt') || input.closest('label')).classList.toggle('is-locked', !bespoke);
      if (!bespoke && input.checked) document.getElementById(input.dataset.fallback).checked = true;
    });
    if (bespoke) form.querySelectorAll('.upsell').forEach((n) => n.remove());
  };
  form.querySelectorAll('input[name="package"]').forEach((r) => r.addEventListener('change', syncPackage));
  syncPackage();

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const bespoke = isBespoke();
    const order = collectOrder(form, bespoke);
    const summary = summarise(form, bespoke);
    const buildFile = JSON.stringify(order, null, 2);
    const couple = `${order.couple.partner1} & ${order.couple.partner2}`;
    const subject = `New ${bespoke ? 'Bespoke' : 'Essential'} wedding website order — ${couple}`;

    if (STUDIO.formEndpoint) {
      status.className = 'form-status';
      status.textContent = 'Sending…';
      const data = new FormData();
      data.append('_subject', subject);
      data.append('_template', 'box');
      data.append('_captcha', 'false');
      data.append('Answers', summary);
      data.append('Build file (paste into the builder)', buildFile);
      try {
        const res = await fetch(STUDIO.formEndpoint, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
        const out = await res.json().catch(() => ({}));
        if (!res.ok || String(out.success) === 'false') throw new Error(out.message || res.statusText);
        status.className = 'form-status ok';
        status.textContent = "Thank you! Your answers are in. We'll be in touch within 1–2 working days.";
        form.querySelector('button[type="submit"]').disabled = true;
        return;
      } catch (err) {
        status.className = 'form-status err';
        status.textContent = 'Something went wrong sending online — opening your email app instead.';
      }
    }

    const body = `${summary}\n\n----- BUILD FILE (please leave this part as is) -----\n${JSON.stringify(order)}`;
    location.href = `mailto:${STUDIO.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
}
