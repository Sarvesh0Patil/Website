/* nav.js — injected into every page */
(function () {
  /* ── 1. Inject nav HTML ── */
  const NAV_HTML = `
<nav id="mainNav">
  <a class="nav-logo" href="index.html">Sarvesh <span>Patil</span></a>
  <ul class="nav-links" id="navLinks">
    <li><a href="index.html"     data-page="home">Home</a></li>
    <li><a href="projects.html"  data-page="projects">Projects</a></li>
    <li><a href="travels.html"   data-page="travels">Travels</a></li>
    <li><a href="resume.html"    data-page="resume">Resume</a></li>
    <li><a href="resources.html" data-page="resources">Resources</a></li>
    <li><a href="contact.html"   data-page="contact" class="nav-cta">Book a call</a></li>
  </ul>
  <button class="nav-mobile-btn" id="mobileBtn" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
</nav>`;
  document.body.insertAdjacentHTML('afterbegin', NAV_HTML);

  /* ── 2. Mark active link based on current filename ── */
  const file = window.location.pathname.split('/').pop() || 'index.html';
  const PAGE_MAP = {
    'index.html': 'home', '': 'home',
    'projects.html':  'projects',
    'travels.html':   'travels',
    'resume.html':    'resume',
    'resources.html': 'resources',
    'contact.html':   'contact'
  };
  const currentPage = PAGE_MAP[file] || 'home';
  document.querySelectorAll('.nav-links a[data-page]').forEach(function (a) {
    if (a.dataset.page === currentPage) a.classList.add('active');
  });

  /* ── 3. Mobile menu toggle ── */
  document.getElementById('mobileBtn').addEventListener('click', function () {
    document.getElementById('navLinks').classList.toggle('open');
  });

  /* ── 4. Custom cursor ── */
  var cursor = document.getElementById('cursor');
  if (cursor) {
    /* Hide until mouse enters so it doesn't sit at (0,0) on load */
    cursor.style.opacity = '0';

    document.addEventListener('mousemove', function (e) {
      cursor.style.left    = e.clientX + 'px';
      cursor.style.top     = e.clientY + 'px';
      cursor.style.opacity = '1';
    });

    /* Hide when mouse leaves the window, show when it returns */
    document.addEventListener('mouseleave', function () { cursor.style.opacity = '0'; });
    document.addEventListener('mouseenter', function () { cursor.style.opacity = '1'; });

    function attachCursorHovers() {
      document.querySelectorAll(
        'a,button,.country-card,.proj-card,.highlight-card,.social-link,.tl-card'
      ).forEach(function (el) {
        el.addEventListener('mouseenter', function () { cursor.classList.add('big'); });
        el.addEventListener('mouseleave', function () { cursor.classList.remove('big'); });
      });
    }
    attachCursorHovers();
    /* Re-attach after dynamic content is added (e.g. travel cards) */
    window.reattachCursorHovers = attachCursorHovers;
  }

  /* ── 5. Scroll: nav shrink + progress bar + hero parallax ── */
  var scrollProg = document.getElementById('scroll-progress');
  var nav = document.getElementById('mainNav');
  window.addEventListener('scroll', function () {
    var y = window.scrollY;
    var shrunk = y > 40;
    nav.classList.toggle('shrunk', shrunk);
    if (scrollProg) {
      scrollProg.style.top = (shrunk ? 52 : 64) + 'px';
      var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (maxScroll > 0) scrollProg.style.width = Math.min((y / maxScroll) * 100, 100) + '%';
    }
    /* Hero parallax — only fires on home page where .hero-left exists */
    if (y > 60) {
      var heroLeft  = document.querySelector('.hero-left');
      var heroRight = document.querySelector('.hero-right');
      if (heroLeft)  heroLeft.style.transform  = 'translateY(' + (y * 0.1)   + 'px)';
      if (heroRight) heroRight.style.transform = 'translateY(' + (y * 0.055) + 'px)';
    }
  }, { passive: true });

  /* ── 6. Reveal on scroll ── */
  function triggerReveals() {
    var reveals = document.querySelectorAll('.reveal');
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) e.target.classList.add('visible');
      });
    }, { threshold: 0.08 });
    reveals.forEach(function (r) { r.classList.remove('visible'); obs.observe(r); });
  }

  /* ── 7. Stagger grid animation ── */
  function triggerStaggerGrids() {
    var grids = document.querySelectorAll('.stagger-grid');
    grids.forEach(function (grid) {
      Array.from(grid.children).forEach(function (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(22px)';
        card.style.transition = 'none';
      });
    });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        obs.unobserve(e.target);
        Array.from(e.target.children).forEach(function (card, i) {
          setTimeout(function () {
            card.style.transition = 'opacity .55s cubic-bezier(0.22,1,0.36,1), transform .55s cubic-bezier(0.22,1,0.36,1)';
            card.style.opacity = '1';
            card.style.transform = 'none';
          }, i * 100);
        });
      });
    }, { threshold: 0.05 });
    grids.forEach(function (g) { obs.observe(g); });
  }

  /* Expose so page-specific scripts (e.g. travels) can call after dynamic render */
  window.triggerReveals      = triggerReveals;
  window.triggerStaggerGrids = triggerStaggerGrids;

  triggerReveals();
  triggerStaggerGrids();
})();
