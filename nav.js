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
  <button class="nav-mobile-btn" id="mobileBtn" type="button" aria-label="Open menu" aria-controls="navLinks" aria-expanded="false">
    <span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span>
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
    if (a.dataset.page === currentPage) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }
  });

  /* ── 3. Mobile menu toggle ── */
  var mobileBtn = document.getElementById('mobileBtn');
  var navLinks = document.getElementById('navLinks');

  function setMobileMenuOpen(open) {
    navLinks.classList.toggle('open', open);
    mobileBtn.setAttribute('aria-expanded', String(open));
    mobileBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('menu-open', open);
  }

  mobileBtn.addEventListener('click', function () {
    setMobileMenuOpen(!navLinks.classList.contains('open'));
  });
  navLinks.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () { setMobileMenuOpen(false); });
  });
  navLinks.addEventListener('click', function (event) {
    if (event.target === navLinks) setMobileMenuOpen(false);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && navLinks.classList.contains('open')) {
      setMobileMenuOpen(false);
      mobileBtn.focus();
    }
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) setMobileMenuOpen(false);
  });

  /* ── 4. Scroll: nav shrink + progress bar + hero parallax ── */
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

  /* ── 5. Reveal on scroll ── */
  function triggerReveals() {
    var reveals = document.querySelectorAll('.reveal');
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) e.target.classList.add('visible');
      });
    }, { threshold: 0.08 });
    reveals.forEach(function (r) { r.classList.remove('visible'); obs.observe(r); });
  }

  /* ── 6. Stagger grid animation ── */
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

  /* Keep the resume section navigation in sync with the visible section. */
  var resumeSections = document.querySelectorAll('.res-section[id]');
  if (resumeSections.length && 'IntersectionObserver' in window) {
    var sectionLinks = document.querySelectorAll('.res-sidebar-link[href^="#"]');
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        sectionLinks.forEach(function (link) {
          var active = link.getAttribute('href') === '#' + entry.target.id;
          link.classList.toggle('rs-active', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-96px 0px -68% 0px', threshold: 0 });
    resumeSections.forEach(function (section) { sectionObserver.observe(section); });
  }

  var printResumeButton = document.getElementById('resumePrint');
  if (printResumeButton) {
    printResumeButton.addEventListener('click', function () { window.print(); });
  }
})();
