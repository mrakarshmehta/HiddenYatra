document.addEventListener("DOMContentLoaded", () => {

  /* ═══════════════════════════════════════════
     DOM REFERENCES
     ═══════════════════════════════════════════ */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const homeView = $("#home-view");
  const detailView = $("#detail-view");
  const searchInput = $("#search-input");
  const dropdown = $("#autocomplete-dropdown");
  const citiesGrid = $("#featured-cities-grid");
  const headerLogo = $("#header-logo");
  const backBtn = $("#back-to-home-btn");
  const randomBtn = $("#random-btn");
  const scrollTopBtn = $("#scroll-to-top");
  const tabsContainer = $("#tabs-container");
  const tabIndicator = $("#tab-indicator");

  const cityHero = $("#city-hero-container");
  const quickFacts = $("#quick-facts-container");
  const highlights = $("#highlights-container");
  const landmarksGrid = $("#landmarks-grid");
  const delicaciesGrid = $("#delicacies-grid");
  const attractionsGrid = $("#attractions-grid");

  const tabButtons = $$(".tab-btn");
  const tabPanels = $$(".tab-panel");

  /* ═══════════════════════════════════════════
     STATE
     ═══════════════════════════════════════════ */
  let activeSuggIdx = -1;
  let suggestions = [];
  let statsAnimated = false;

  /* ═══════════════════════════════════════════
     INIT
     ═══════════════════════════════════════════ */
  function init() {
    setupParticles();
    renderCityCards();
    bindEvents();
    handleRoute();
    window.addEventListener("hashchange", handleRoute);
  }

  /* ═══════════════════════════════════════════
     ROUTING
     ═══════════════════════════════════════════ */
  function handleRoute() {
    const hash = location.hash;
    if (hash.startsWith("#city-")) {
      const city = CITIES_DATA.find(c => c.id === hash.slice(6));
      if (city) return showCity(city);
    }
    showHome();
  }

  function showHome() {
    if (location.hash !== "#home" && location.hash !== "") location.hash = "home";
    detailView.classList.remove("active");
    homeView.classList.remove("exiting");
    homeView.classList.add("active");
    searchInput.value = "";
    hideDropdown();
    window.scrollTo({ top: 0, behavior: "smooth" });
    // Trigger scroll reveals again
    requestAnimationFrame(checkScrollReveals);
  }

  function goToCity(id) {
    location.hash = `city-${id}`;
  }

  /* ═══════════════════════════════════════════
     EVENTS
     ═══════════════════════════════════════════ */
  function bindEvents() {
    headerLogo.addEventListener("click", e => { e.preventDefault(); showHome(); });
    backBtn.addEventListener("click", showHome);

    // Search
    searchInput.addEventListener("input", onSearchInput);
    searchInput.addEventListener("keydown", onSearchKey);
    searchInput.addEventListener("focus", () => {
      if (searchInput.value.trim()) onSearchInput({ target: searchInput });
    });

    document.addEventListener("click", e => {
      if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) hideDropdown();
    });

    // Ctrl+K shortcut
    document.addEventListener("keydown", e => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });

    // Tabs
    tabButtons.forEach(btn => {
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });

    // Random destination
    randomBtn.addEventListener("click", () => {
      const randomCity = CITIES_DATA[Math.floor(Math.random() * CITIES_DATA.length)];
      goToCity(randomCity.id);
    });

    // Scroll to top
    window.addEventListener("scroll", () => {
      scrollTopBtn.classList.toggle("visible", window.scrollY > 500);
      checkScrollReveals();
      if (!statsAnimated) checkStatsAnimation();
    }, { passive: true });

    scrollTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ═══════════════════════════════════════════
     RENDER CITY CARDS
     ═══════════════════════════════════════════ */
  function renderCityCards() {
    citiesGrid.innerHTML = "";
    CITIES_DATA.forEach((city, i) => {
      const card = document.createElement("div");
      card.className = "city-card";
      card.style.transitionDelay = `${i * 0.06}s`;
      card.innerHTML = `
        <div class="card-image-wrapper">
          <img class="card-image" src="${city.image}" alt="${city.name}" loading="lazy">
          <div class="card-image-overlay"></div>
          <div class="card-badge">${city.emoji} ${city.country}</div>
          <div class="card-explore-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </div>
        </div>
        <div class="card-content">
          <h3 class="card-title">${city.name}</h3>
          <p class="card-tagline">${city.tagline}</p>
          <p class="card-description">${city.description}</p>
          <div class="card-meta">
            <span class="card-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M3 7v1a3 3 0 006 0V7m0 1a3 3 0 006 0V7m0 1a3 3 0 006 0V7"/></svg>
              ${city.landmarks.length} Landmarks
            </span>
            <span class="card-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 010 8h-1M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8zM6 1v3M10 1v3M14 1v3"/></svg>
              ${city.delicacies.length} Dishes
            </span>
            <span class="card-meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
              ${city.attractions.length} Spots
            </span>
          </div>
        </div>
      `;
      card.addEventListener("click", () => goToCity(city.id));
      citiesGrid.appendChild(card);
    });
    // Initial reveal check
    requestAnimationFrame(checkScrollReveals);
  }

  /* ═══════════════════════════════════════════
     SCROLL REVEAL
     ═══════════════════════════════════════════ */
  function checkScrollReveals() {
    const cards = $$(".city-card:not(.revealed)");
    cards.forEach(card => {
      const rect = card.getBoundingClientRect();
      if (rect.top < window.innerHeight - 60) {
        card.classList.add("revealed");
      }
    });
  }

  /* ═══════════════════════════════════════════
     STATS COUNTER ANIMATION
     ═══════════════════════════════════════════ */
  function checkStatsAnimation() {
    const statsBar = $("#stats-bar");
    if (!statsBar) return;
    const rect = statsBar.getBoundingClientRect();
    if (rect.top < window.innerHeight - 50) {
      statsAnimated = true;
      $$(".stat-number").forEach(el => {
        const target = parseInt(el.dataset.target);
        animateCounter(el, target);
      });
    }
  }

  function animateCounter(el, target) {
    let current = 0;
    const increment = target / 40;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current) + "+";
    }, 30);
  }

  /* ═══════════════════════════════════════════
     SEARCH & AUTOCOMPLETE
     ═══════════════════════════════════════════ */
  function onSearchInput(e) {
    const q = e.target.value.trim().toLowerCase();
    activeSuggIdx = -1;
    if (!q) return hideDropdown();

    suggestions = CITIES_DATA.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.country.toLowerCase().includes(q) ||
      c.tagline.toLowerCase().includes(q)
    );
    renderDropdown(q);
  }

  function renderDropdown(query) {
    dropdown.innerHTML = "";

    if (!suggestions.length) {
      dropdown.innerHTML = `
        <div class="no-results">
          <div class="no-results-icon">🔍</div>
          <div class="no-results-text">No destinations found</div>
          <div class="no-results-hint">Try searching for "Paris", "India", or "Tokyo"</div>
        </div>`;
      dropdown.classList.add("active");
      return;
    }

    const label = document.createElement("div");
    label.className = "dropdown-label";
    label.textContent = `${suggestions.length} destination${suggestions.length > 1 ? 's' : ''} found`;
    dropdown.appendChild(label);

    suggestions.forEach((city, i) => {
      const item = document.createElement("div");
      item.className = "suggestion-item";
      item.innerHTML = `
        <div class="suggestion-emoji">${city.emoji}</div>
        <div class="suggestion-info">
          <div class="suggestion-name">${highlightMatch(city.name, query)}</div>
          <div class="suggestion-tagline">${city.tagline}</div>
        </div>
        <svg class="suggestion-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      `;
      item.addEventListener("click", () => { goToCity(city.id); hideDropdown(); });
      item.addEventListener("mouseenter", () => highlightSuggestion(i));
      dropdown.appendChild(item);
    });

    dropdown.classList.add("active");
  }

  function highlightMatch(text, query) {
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return text;
    return text.slice(0, idx) +
      `<span class="match-highlight">${text.slice(idx, idx + query.length)}</span>` +
      text.slice(idx + query.length);
  }

  function highlightSuggestion(index) {
    dropdown.querySelectorAll(".suggestion-item").forEach((item, i) => {
      item.classList.toggle("highlighted", i === index);
    });
    activeSuggIdx = index;
  }

  function hideDropdown() {
    dropdown.classList.remove("active");
    suggestions = [];
    activeSuggIdx = -1;
  }

  function onSearchKey(e) {
    const items = dropdown.querySelectorAll(".suggestion-item");
    if (!dropdown.classList.contains("active") || !items.length) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      activeSuggIdx = (activeSuggIdx + 1) % suggestions.length;
      highlightSuggestion(activeSuggIdx);
      items[activeSuggIdx].scrollIntoView({ block: "nearest" });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeSuggIdx = (activeSuggIdx - 1 + suggestions.length) % suggestions.length;
      highlightSuggestion(activeSuggIdx);
      items[activeSuggIdx].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter" && activeSuggIdx >= 0) {
      e.preventDefault();
      goToCity(suggestions[activeSuggIdx].id);
      hideDropdown();
    } else if (e.key === "Escape") {
      hideDropdown();
      searchInput.blur();
    }
  }

  /* ═══════════════════════════════════════════
     CITY DETAIL VIEW
     ═══════════════════════════════════════════ */
  function showCity(city) {
    homeView.classList.remove("active");
    detailView.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Hero
    cityHero.innerHTML = `
      <img class="city-hero-image" src="${city.image}" alt="${city.name}">
      <div class="city-hero-overlay"></div>
      <div class="city-hero-content">
        <div class="city-hero-badge">${city.emoji} ${city.country}</div>
        <h1 class="city-title">${city.name}</h1>
        <p class="city-tagline">${city.tagline}</p>
        <p class="city-description">${city.description}</p>
      </div>
    `;

    // Quick Facts
    const facts = city.quickFacts;
    const factIcons = { population: "👥", language: "🗣️", currency: "💰", bestTime: "☀️", timezone: "🕐" };
    const factLabels = { population: "Population", language: "Language", currency: "Currency", bestTime: "Best Time to Visit", timezone: "Timezone" };
    quickFacts.innerHTML = Object.entries(facts).map(([key, val]) => `
      <div class="fact-item">
        <span class="fact-label">${factIcons[key] || ""} ${factLabels[key] || key}</span>
        <span class="fact-value">${val}</span>
      </div>
    `).join("");

    // Highlights
    const allCategories = [
      ...city.landmarks.map(l => l.category),
      ...city.delicacies.map(d => d.category),
      ...city.attractions.map(a => a.category)
    ];
    const uniqueCategories = [...new Set(allCategories)].slice(0, 8);
    highlights.innerHTML = uniqueCategories.map(cat => `
      <span class="highlight-tag">🏷️ ${cat}</span>
    `).join("");

    // Landmarks
    landmarksGrid.innerHTML = city.landmarks.map(lm => `
      <div class="detail-item-card">
        <div class="card-header-row">
          <div class="item-icon-name">
            <span class="item-emoji">🏛️</span>
            <h4 class="item-name">${lm.name}</h4>
          </div>
          <span class="item-badge ${lm.mustVisit ? 'must-visit' : ''}">${lm.mustVisit ? '⭐ Must Visit' : lm.category}</span>
        </div>
        <p class="item-description">${lm.description}</p>
        <div class="item-meta-row">
          <span>📂 <strong>${lm.category}</strong></span>
        </div>
      </div>
    `).join("");

    // Delicacies
    delicaciesGrid.innerHTML = city.delicacies.map(food => `
      <div class="detail-item-card">
        <div class="card-header-row">
          <div class="item-icon-name">
            <span class="item-emoji">🍽️</span>
            <h4 class="item-name">${food.name}</h4>
          </div>
          <span class="item-badge">${food.category}</span>
        </div>
        <p class="item-description">${food.description}</p>
        <div class="item-meta-row">
          <span>💰 Price: <strong>${food.priceRange}</strong></span>
          <span>📂 <strong>${food.category}</strong></span>
        </div>
      </div>
    `).join("");

    // Attractions
    attractionsGrid.innerHTML = city.attractions.map(attr => `
      <div class="detail-item-card">
        <div class="card-header-row">
          <div class="item-icon-name">
            <span class="item-emoji">📸</span>
            <h4 class="item-name">${attr.name}</h4>
          </div>
          <span class="item-badge">${attr.category}</span>
        </div>
        <p class="item-description">${attr.description}</p>
        <div class="item-meta-row">
          <span>⏱️ Duration: <strong>${attr.duration}</strong></span>
          <span>📂 <strong>${attr.category}</strong></span>
        </div>
      </div>
    `).join("");

    // Reset tab
    switchTab("landmarks");
  }

  /* ═══════════════════════════════════════════
     TABS WITH SLIDING INDICATOR
     ═══════════════════════════════════════════ */
  function switchTab(tabId) {
    tabButtons.forEach(btn => btn.classList.toggle("active", btn.dataset.tab === tabId));
    tabPanels.forEach(p => p.classList.toggle("active", p.id === tabId));
    updateTabIndicator();
  }

  function updateTabIndicator() {
    const activeBtn = tabsContainer.querySelector(".tab-btn.active");
    if (!activeBtn || !tabIndicator) return;
    const containerRect = tabsContainer.getBoundingClientRect();
    const btnRect = activeBtn.getBoundingClientRect();
    tabIndicator.style.width = btnRect.width + "px";
    tabIndicator.style.left = (btnRect.left - containerRect.left) + "px";
  }

  // Recalculate on resize
  window.addEventListener("resize", updateTabIndicator);

  /* ═══════════════════════════════════════════
     CONSTELLATION PARTICLE ENGINE
     ═══════════════════════════════════════════ */
  function setupParticles() {
    const canvas = document.getElementById("particle-canvas");
    const ctx = canvas.getContext("2d");
    let particles = [];
    const COUNT = 80;
    const CONNECT_DIST = 120;
    let mouse = { x: -999, y: -999 };

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    window.addEventListener("resize", resize);
    resize();

    document.addEventListener("mousemove", e => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    });

    class Particle {
      constructor() { this.reset(true); }
      reset(initial) {
        this.x = Math.random() * canvas.width;
        this.y = initial ? Math.random() * canvas.height : canvas.height + 10;
        this.size = Math.random() * 1.8 + 0.6;
        this.vx = (Math.random() - 0.5) * 0.4;
        this.vy = -(Math.random() * 0.4 + 0.1);
        this.alpha = Math.random() * 0.5 + 0.15;
        this.baseAlpha = this.alpha;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;

        // Subtle mouse repulsion
        const dx = this.x - mouse.x;
        const dy = this.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          this.x += dx / dist * 0.5;
          this.y += dy / dist * 0.5;
        }

        if (this.y < -10 || this.x < -10 || this.x > canvas.width + 10) this.reset(false);
      }
      draw() {
        ctx.fillStyle = `rgba(129, 140, 248, ${this.alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    for (let i = 0; i < COUNT; i++) particles.push(new Particle());

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Background radial glow
      const g = ctx.createRadialGradient(
        canvas.width * 0.5, canvas.height * 0.35, 0,
        canvas.width * 0.5, canvas.height * 0.35, canvas.width * 0.6
      );
      g.addColorStop(0, "rgba(99, 102, 241, 0.03)");
      g.addColorStop(1, "transparent");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update & draw
      particles.forEach(p => { p.update(); p.draw(); });

      // Constellation lines
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECT_DIST) {
            const opacity = (1 - dist / CONNECT_DIST) * 0.12;
            ctx.strokeStyle = `rgba(129, 140, 248, ${opacity})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(animate);
    }
    animate();
  }

  /* ═══════════════════════════════════════════
     LAUNCH
     ═══════════════════════════════════════════ */
  init();
});
