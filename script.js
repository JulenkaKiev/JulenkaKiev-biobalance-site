// Встав сюди посилання на оплату WayForPay, коли воно буде готове.
// Поки що всі кнопки "Отримати гайд" ведуть на блок з ціною.
const PAYMENT_LINK = "";

if (PAYMENT_LINK) {
  document.querySelectorAll(".js-buy-anchor").forEach((el) => {
    el.setAttribute("href", PAYMENT_LINK);
    el.setAttribute("target", "_blank");
    el.setAttribute("rel", "noopener");
  });
}

// Scroll reveal
const revealEls = document.querySelectorAll(".reveal");
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("on");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 }
);
revealEls.forEach((el) => revealObserver.observe(el));

// Stat counters
const statEls = document.querySelectorAll(".stat-n");
const statObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.count, 10);
      const suffix = el.dataset.suffix || "";
      const duration = 900;
      const start = performance.now();
      function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const value = Math.round(target * progress);
        el.textContent = value + suffix;
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
      statObserver.unobserve(el);
    });
  },
  { threshold: 0.4 }
);
statEls.forEach((el) => statObserver.observe(el));

// Sticky CTA visibility
const stickyCta = document.querySelector(".sticky-cta");
const hero = document.querySelector(".hero");
const pricing = document.querySelector(".pricing");
const stickyObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.target === hero) {
        if (!entry.isIntersecting) stickyCta.classList.add("show");
        else stickyCta.classList.remove("show");
      }
    });
  },
  { threshold: 0 }
);
if (hero) stickyObserver.observe(hero);

const pricingObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) stickyCta.classList.remove("show");
    });
  },
  { threshold: 0.6 }
);
if (pricing) pricingObserver.observe(pricing);
