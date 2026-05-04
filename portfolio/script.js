/* ============================================
   CINEMATCH DEVELOPER PORTFOLIO
   Animations, 3D Tilt, Particles, Interactions
   ============================================ */

(function () {
  'use strict';

  // ---- Particles Background ----
  function initParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    const count = Math.min(40, Math.floor(window.innerWidth / 30));
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      p.style.left = Math.random() * 100 + '%';
      p.style.animationDuration = (12 + Math.random() * 20) + 's';
      p.style.animationDelay = (Math.random() * 15) + 's';
      p.style.width = p.style.height = (1 + Math.random() * 2.5) + 'px';
      p.style.opacity = (0.15 + Math.random() * 0.3).toString();
      container.appendChild(p);
    }
  }

  // ---- Scroll Animations (Intersection Observer) ----
  function initScrollAnimations() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const delay = parseInt(entry.target.dataset.delay) || 0;
            setTimeout(() => {
              entry.target.classList.add('visible');
            }, delay);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.animate-in').forEach((el) => {
      observer.observe(el);
    });
  }

  // ---- 3D Tilt Effect ----
  function initTiltCards() {
    const cards = document.querySelectorAll('.tilt-card');
    const maxTilt = 6;

    cards.forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const tiltX = ((y - centerY) / centerY) * -maxTilt;
        const tiltY = ((x - centerX) / centerX) * maxTilt;

        card.style.setProperty('--tilt-x', tiltX + 'deg');
        card.style.setProperty('--tilt-y', tiltY + 'deg');
        card.style.transform =
          `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.02, 1.02, 1.02)`;

        // Glow follow
        card.style.setProperty('--mouse-x', ((x / rect.width) * 100) + '%');
        card.style.setProperty('--mouse-y', ((y / rect.height) * 100) + '%');
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
      });
    });
  }

  // ---- Counter Animation ----
  function initCounters() {
    const counters = document.querySelectorAll('.counter');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const target = parseInt(el.dataset.target);
            animateCounter(el, 0, target, 1500);
            observer.unobserve(el);
          }
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach((c) => observer.observe(c));
  }

  function animateCounter(el, start, end, duration) {
    const startTime = performance.now();
    function update(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + (end - start) * eased);
      el.textContent = current;
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    requestAnimationFrame(update);
  }

  // ---- Navigation ----
  function initNav() {
    const nav = document.getElementById('nav');
    const toggle = document.getElementById('navToggle');
    const mobileMenu = document.getElementById('mobileMenu');

    // Scroll effect
    let lastScroll = 0;
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      if (scrollY > 50) {
        nav.classList.add('scrolled');
      } else {
        nav.classList.remove('scrolled');
      }
      lastScroll = scrollY;
    }, { passive: true });

    // Mobile toggle
    if (toggle && mobileMenu) {
      toggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('open');
        toggle.classList.toggle('active');
      });

      // Close on link click
      mobileMenu.querySelectorAll('a').forEach((a) => {
        a.addEventListener('click', () => {
          mobileMenu.classList.remove('open');
          toggle.classList.remove('active');
        });
      });
    }

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener('click', (e) => {
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // ---- Code Tabs ----
  function initCodeTabs() {
    const tabs = document.querySelectorAll('.code-tab');
    const panels = document.querySelectorAll('.code-panel');

    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const target = tab.dataset.tab;

        tabs.forEach((t) => t.classList.remove('active'));
        panels.forEach((p) => p.classList.remove('active'));

        tab.classList.add('active');
        const panel = document.getElementById('tab-' + target);
        if (panel) {
          panel.classList.add('active');
          // Re-trigger animations inside the panel
          panel.querySelectorAll('.animate-in').forEach((el) => {
            el.classList.remove('visible');
            setTimeout(() => el.classList.add('visible'), 50);
          });
        }
      });
    });
  }

  // ---- Mouse Glow on Cards ----
  function initCardGlow() {
    document.addEventListener('mousemove', (e) => {
      document.querySelectorAll('.bento-card').forEach((card) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        if (x >= 0 && x <= rect.width && y >= 0 && y <= rect.height) {
          card.style.setProperty('--mouse-x', x + 'px');
          card.style.setProperty('--mouse-y', y + 'px');
        }
      });
    });
  }

  // ---- Parallax on Scroll ----
  function initParallax() {
    const heroGlow = document.querySelector('.hero-glow');
    if (!heroGlow) return;

    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      const rate = scrollY * 0.3;
      heroGlow.style.transform = `translate(-50%, calc(-50% + ${rate}px))`;
    }, { passive: true });
  }

  // ---- Initialize Everything ----
  function init() {
    initParticles();
    initScrollAnimations();
    initTiltCards();
    initCounters();
    initNav();
    initCodeTabs();
    initCardGlow();
    initParallax();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
