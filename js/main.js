document.addEventListener('DOMContentLoaded', () => {
  /* Mobile nav toggle */
  const toggle = document.getElementById('nav-toggle');
  const nav = document.getElementById('main-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      toggle.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* Highlight current page in nav */
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.main-nav a').forEach((link) => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
  });

  /* Countdown to the wedding day */
  const countdownEl = document.getElementById('countdown');
  if (countdownEl) {
    const weddingDate = new Date('2027-02-20T14:00:00+02:00');

    const dayEl = countdownEl.querySelector('[data-days]');
    const hourEl = countdownEl.querySelector('[data-hours]');
    const minuteEl = countdownEl.querySelector('[data-minutes]');
    const secondEl = countdownEl.querySelector('[data-seconds]');

    const update = () => {
      const diff = Math.max(0, weddingDate.getTime() - Date.now());
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      const seconds = Math.floor((diff / 1000) % 60);

      if (dayEl) dayEl.textContent = String(days);
      if (hourEl) hourEl.textContent = String(hours).padStart(2, '0');
      if (minuteEl) minuteEl.textContent = String(minutes).padStart(2, '0');
      if (secondEl) secondEl.textContent = String(seconds).padStart(2, '0');
    };

    update();
    setInterval(update, 1000);
  }

  /* FAQ accordion */
  document.querySelectorAll('.faq-question').forEach((btn) => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      if (!item) return;
      const isOpen = item.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(isOpen));
    });
  });
});
