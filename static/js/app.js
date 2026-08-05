/* ═══════════════════════════════════════════════
   HiddenYatra — App JavaScript v2.0
   Theme, search, scroll, animations, carousel
   ═══════════════════════════════════════════════ */

(function() {
  'use strict';

  // ── THEME TOGGLE ──
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;

  function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('hy-theme', theme);
  }

  const saved = localStorage.getItem('hy-theme');
  if (saved) setTheme(saved);
  else setTheme('light');

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // ── MOBILE MENU ──
  const mobileToggle = document.getElementById('mobile-toggle');
  const navLinks = document.getElementById('nav-links');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      mobileToggle.classList.toggle('active');
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        mobileToggle.classList.remove('active');
      });
    });
  }

  // ── PROFILE DROPDOWN ──
  const profileDropdown = document.getElementById('nav-profile-dropdown');
  const profileBtn = document.getElementById('profile-dropdown-btn');

  if (profileBtn && profileDropdown) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      profileDropdown.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!profileDropdown.contains(e.target)) {
        profileDropdown.classList.remove('open');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') profileDropdown.classList.remove('open');
    });
  }

  // ── NAVBAR SCROLL ──
  const navbar = document.getElementById('navbar');

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    if (navbar) {
      navbar.classList.toggle('scrolled', scrollY > 50);
    }

    const scrollBtn = document.getElementById('scroll-top-btn');
    if (scrollBtn) {
      scrollBtn.classList.toggle('visible', scrollY > 400);
    }
  }, { passive: true });

  // Scroll to top
  const scrollTopBtn = document.getElementById('scroll-top-btn');
  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ── HTML ESCAPE UTILITY (XSS prevention) ──
  function _esc(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ── SEARCH AUTOCOMPLETE ──
  const searchInput = document.getElementById('nav-search-input');
  const autocomplete = document.getElementById('nav-autocomplete');
  let searchTimeout = null;

  if (searchInput && autocomplete) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      const q = searchInput.value.trim();

      if (q.length < 2) {
        autocomplete.classList.remove('active');
        autocomplete.innerHTML = '';
        return;
      }

      searchTimeout = setTimeout(() => {
        fetch('/api/autocomplete?q=' + encodeURIComponent(q))
          .then(r => r.json())
          .then(data => {
            if (data.length === 0) {
              autocomplete.classList.remove('active');
              return;
            }

            autocomplete.innerHTML = data.map(p =>
              `<a href="/place/${_esc(p.slug)}" class="autocomplete-item">
                <div class="autocomplete-item-name">${_esc(p.name)}</div>
                <div class="autocomplete-item-meta">${_esc(p.district_name || p.state_name)}</div>
              </a>`
            ).join('');
            autocomplete.classList.add('active');
          })
          .catch(() => autocomplete.classList.remove('active'));
      }, 250);
    });

    document.addEventListener('click', (e) => {
      if (!e.target.closest('#nav-search')) {
        autocomplete.classList.remove('active');
      }
    });
  }

  // ── SCROLL REVEAL ──
  const revealSelectors = '.reveal, .reveal-left, .reveal-right, .reveal-scale';
  const revealElements = document.querySelectorAll(revealSelectors);
  if (revealElements.length > 0) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    revealElements.forEach(el => revealObserver.observe(el));
  }

  // ── FLASH MESSAGES AUTO-DISMISS ──
  document.querySelectorAll('.flash-message').forEach(msg => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(100%)';
      setTimeout(() => msg.remove(), 300);
    }, 5000);
  });

  // ── BUTTON RIPPLE EFFECT ──
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      ripple.classList.add('btn-ripple');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // ── MOBILE BOTTOM NAV ACTIVE STATE ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.mobile-nav-item').forEach(item => {
    item.classList.remove('active');
    const href = item.getAttribute('href');
    if (currentPath === href || (href === '/' && currentPath === '/')) {
      item.classList.add('active');
    }
  });
  // ── ANIMATED STAT COUNTERS ──
  const statNumbers = document.querySelectorAll('.stat-number[data-target]');
  if (statNumbers.length) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.target) || 0;
          const duration = 1500;
          const start = performance.now();
          function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(eased * target);
            if (progress < 1) requestAnimationFrame(tick);
            else el.textContent = target;
          }
          requestAnimationFrame(tick);
          counterObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    statNumbers.forEach(el => counterObserver.observe(el));
  }

})();

// ── CAROUSEL (global) ──
function scrollCarousel(id, direction) {
  const track = document.getElementById(id);
  if (!track) return;
  const cardWidth = track.querySelector('.place-card')?.offsetWidth || 340;
  track.scrollBy({ left: direction * (cardWidth + 24), behavior: 'smooth' });
}
