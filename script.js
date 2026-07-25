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

const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const hasFinePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

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
      if (prefersReduced) {
        el.textContent = target + suffix;
        statObserver.unobserve(el);
        return;
      }
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

// Header condense on scroll
const siteHeader = document.querySelector(".site-header");
if (siteHeader) {
  let ticking = false;
  const applyHeaderState = () => {
    siteHeader.classList.toggle("condensed", window.scrollY > 40);
    ticking = false;
  };
  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        requestAnimationFrame(applyHeaderState);
        ticking = true;
      }
    },
    { passive: true }
  );
  applyHeaderState();
}

// Aurora canvas - slow drifting warm glow behind the hero, GPU-cheap radial blobs
const auroraCanvas = document.getElementById("aurora");
if (auroraCanvas) {
  const ctx = auroraCanvas.getContext("2d");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  let w = 0;
  let h = 0;

  const blobs = [
    { baseX: 0.72, baseY: 0.18, r: 0.55, color: "201,161,90", ax: 60, ay: 40, speed: 0.00018, phase: 0 },
    { baseX: 0.18, baseY: 0.55, r: 0.4, color: "233,196,132", ax: 50, ay: 55, speed: 0.00014, phase: 2 },
    { baseX: 0.55, baseY: 0.85, r: 0.45, color: "169,130,47", ax: 45, ay: 35, speed: 0.00021, phase: 4 },
  ];

  function resize() {
    const rect = auroraCanvas.parentElement.getBoundingClientRect();
    w = rect.width;
    h = rect.height;
    auroraCanvas.width = w * dpr;
    auroraCanvas.height = h * dpr;
    auroraCanvas.style.width = w + "px";
    auroraCanvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function drawFrame(t) {
    ctx.clearRect(0, 0, w, h);
    ctx.globalCompositeOperation = "lighter";
    blobs.forEach((b) => {
      const drift = prefersReduced ? 0 : t;
      const x = b.baseX * w + Math.sin(drift * b.speed + b.phase) * b.ax;
      const y = b.baseY * h + Math.cos(drift * b.speed * 1.3 + b.phase) * b.ay;
      const radius = b.r * Math.max(w, h);
      const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);
      grad.addColorStop(0, `rgba(${b.color},0.55)`);
      grad.addColorStop(1, `rgba(${b.color},0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  let animId;
  function loop(t) {
    drawFrame(t);
    animId = requestAnimationFrame(loop);
  }

  resize();
  if (prefersReduced) {
    drawFrame(0);
  } else {
    animId = requestAnimationFrame(loop);
  }

  window.addEventListener(
    "resize",
    () => {
      resize();
      if (prefersReduced) drawFrame(0);
    },
    { passive: true }
  );
}

// Cursor glow - soft trailing light, desktop only
if (hasFinePointer && !prefersReduced) {
  const glow = document.getElementById("cursor-glow");
  if (glow) {
    let targetX = -1000;
    let targetY = -1000;
    let curX = -1000;
    let curY = -1000;

    window.addEventListener(
      "mousemove",
      (e) => {
        targetX = e.clientX;
        targetY = e.clientY;
      },
      { passive: true }
    );

    function followLoop() {
      curX += (targetX - curX) * 0.12;
      curY += (targetY - curY) * 0.12;
      glow.style.transform = `translate3d(${curX - 230}px, ${curY - 230}px, 0)`;
      requestAnimationFrame(followLoop);
    }
    requestAnimationFrame(followLoop);
  }
}

// Magnetic buttons - primary CTAs pull gently toward the cursor, desktop only
if (hasFinePointer && !prefersReduced) {
  document.querySelectorAll(".js-magnetic").forEach((btn) => {
    const strength = 0.25;
    const max = 12;
    btn.addEventListener("mousemove", (e) => {
      const rect = btn.getBoundingClientRect();
      const dx = e.clientX - (rect.left + rect.width / 2);
      const dy = e.clientY - (rect.top + rect.height / 2);
      const x = Math.max(-max, Math.min(max, dx * strength));
      const y = Math.max(-max, Math.min(max, dy * strength));
      btn.style.transform = `translate(${x}px, ${y}px)`;
    });
    btn.addEventListener("mouseleave", () => {
      btn.style.transform = "translate(0, 0)";
    });
  });
}

// Scroll-tied 3D tilt on the hero mockup
const bookTilt = document.querySelector(".book-tilt");
if (bookTilt && hero && !prefersReduced) {
  let tiltTicking = false;
  const applyTilt = () => {
    const rect = hero.getBoundingClientRect();
    const progress = Math.max(0, Math.min(1, -rect.top / (rect.height || 1)));
    const rx = progress * -8;
    const ry = progress * 6;
    bookTilt.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) rotate(3deg)`;
    tiltTicking = false;
  };
  window.addEventListener(
    "scroll",
    () => {
      if (!tiltTicking) {
        requestAnimationFrame(applyTilt);
        tiltTicking = true;
      }
    },
    { passive: true }
  );
  applyTilt();
}
