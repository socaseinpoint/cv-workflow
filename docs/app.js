(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;

  // ---- reveal-on-scroll ----
  var reveals = document.querySelectorAll('.reveal');
  if (!hasIO || reduce) {
    reveals.forEach(function (e) { e.classList.add('in'); });
  } else {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); revealIO.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (e) { revealIO.observe(e); });
  }

  // ---- docs section nav: scroll-spy ----
  var navLinks = document.querySelectorAll('.docs-nav a[href^="#"]');
  if (navLinks.length && hasIO) {
    var linkFor = {};
    navLinks.forEach(function (a) { linkFor[a.getAttribute('href').slice(1)] = a; });

    var setActive = function (id) {
      navLinks.forEach(function (a) { a.classList.remove('active'); });
      if (linkFor[id]) linkFor[id].classList.add('active');
    };

    var sections = document.querySelectorAll('.docs-section[id]');
    var spyIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) setActive(en.target.id);
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    sections.forEach(function (s) { spyIO.observe(s); });
  }
})();
